# SPDX-License-Identifier: GPL-3.0-or-later
"""Local LAN discovery: private IPv4 only, no nmap."""

from __future__ import annotations

import csv
import ipaddress
import io
import json
import socket
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from core import fleet, host

COMMON_PORTS: tuple[int, ...] = (22, 80, 443, 3389, 445)
_MAX_PREFIX = 24
_CONCURRENCY = 32
_NEIGH_OK = frozenset({"REACHABLE", "STALE", "DELAY", "PROBE"})
_LAN_NETS: tuple[ipaddress.IPv4Network, ...] = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
)
PingFn = Callable[[str], dict[str, Any]]
TcpFn = Callable[..., dict[str, Any]]
NameFn = Callable[[str], str]
ProgressFn = Callable[[int, int], None]


class LanScanError(Exception):
    """Invalid LAN scan target or input."""


@dataclass
class ScanTarget:
    iface: str
    ip: str
    prefix: int
    network: str


@dataclass
class Neighbor:
    ip: str
    source: str = "neigh"


@dataclass
class ScanHost:
    ip: str
    name: str = ""
    rtt_ms: float | None = None
    ports: list[int] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    is_self: bool = False


def _as_ipv4(text: str) -> ipaddress.IPv4Address:
    try:
        ip = ipaddress.ip_address((text or "").strip())
    except ValueError as exc:
        raise LanScanError("Adresse IPv4 invalide") from exc
    if not isinstance(ip, ipaddress.IPv4Address):
        raise LanScanError("IPv6 ignorée")
    return ip


def is_scan_ipv4(ip: ipaddress.IPv4Address) -> bool:
    return any(ip in net for net in _LAN_NETS)


def clamp_network(ip: str, prefix: int) -> ipaddress.IPv4Network:
    addr = _as_ipv4(ip)
    if not is_scan_ipv4(addr):
        raise LanScanError("Adresse hors LAN privé")
    try:
        raw_prefix = int(prefix)
    except (TypeError, ValueError) as exc:
        raise LanScanError("Préfixe invalide") from exc
    if raw_prefix < 0 or raw_prefix > 32:
        raise LanScanError("Préfixe invalide")
    used = max(raw_prefix, _MAX_PREFIX)
    return ipaddress.ip_network(f"{addr}/{used}", strict=False)


def local_targets(*, ip_json: str | None = None) -> list[ScanTarget]:
    raw = ip_json if ip_json is not None else _ip_addr_json()
    try:
        items = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(items, list):
        return []
    out: list[ScanTarget] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        iface = str(item.get("ifname") or "")
        for info in item.get("addr_info") or []:
            if not isinstance(info, dict) or info.get("family") != "inet":
                continue
            local = str(info.get("local") or "")
            try:
                addr = _as_ipv4(local)
                if not is_scan_ipv4(addr):
                    continue
                prefix = int(info.get("prefixlen") or 24)
                net = clamp_network(local, prefix)
            except (LanScanError, TypeError, ValueError):
                continue
            out.append(ScanTarget(iface=iface, ip=str(addr), prefix=prefix, network=str(net)))
    return out


def parse_neighbors(text: str) -> list[Neighbor]:
    rows: list[Neighbor] = []
    seen: set[str] = set()
    for line in (text or "").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        state = parts[-1].upper()
        if state not in _NEIGH_OK:
            continue
        try:
            ip = _as_ipv4(parts[0])
        except LanScanError:
            continue
        if not is_scan_ipv4(ip):
            continue
        key = str(ip)
        if key in seen:
            continue
        seen.add(key)
        rows.append(Neighbor(ip=key, source="neigh"))
    return rows


def _ip_addr_json() -> str:
    if host.which("ip") is None:
        return "[]"
    try:
        completed = host.run(
            ["ip", "-j", "addr"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, TimeoutError):
        return "[]"
    return completed.stdout or "[]"


def _ip_neigh_text() -> str:
    if host.which("ip") is None:
        return ""
    try:
        completed = host.run(
            ["ip", "neigh"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, TimeoutError):
        return ""
    return completed.stdout or ""


def _default_ping(address: str) -> dict[str, Any]:
    result = fleet.probe_icmp(address, timeout=1.0)
    return {"online": bool(result.get("online")), "rtt_ms": None}


def _default_name(ip: str) -> str:
    try:
        name, _svc = socket.getnameinfo((ip, 0), 0)
    except OSError:
        return ""
    return "" if name == ip else name


def _ensure_host(store: dict[str, ScanHost], ip: str) -> ScanHost:
    row = store.get(ip)
    if row is None:
        row = ScanHost(ip=ip)
        store[ip] = row
    return row


def _add_source(host_row: ScanHost, source: str) -> None:
    if source not in host_row.sources:
        host_row.sources.append(source)


def _reserved(net: ipaddress.IPv4Network, ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return addr == net.network_address or addr == net.broadcast_address


def _ping_sweep(
    candidates: list[str],
    ping_fn: PingFn,
    cancel: threading.Event,
    on_progress: ProgressFn | None,
) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    total = len(candidates)
    done_count = 0
    index = 0

    def work(ip: str) -> tuple[str, dict[str, Any]]:
        if cancel.is_set():
            return ip, {"online": False, "rtt_ms": None, "skipped": True}
        try:
            payload = ping_fn(ip)
        except Exception as exc:  # noqa: BLE001 - per-host isolation
            payload = {"online": False, "rtt_ms": None, "error": str(exc)}
        return ip, payload if isinstance(payload, dict) else {"online": False}

    with ThreadPoolExecutor(max_workers=_CONCURRENCY) as pool:
        pending: set[Any] = set()

        def fill() -> None:
            nonlocal index
            while len(pending) < _CONCURRENCY and index < total and not cancel.is_set():
                ip = candidates[index]
                index += 1
                pending.add(pool.submit(work, ip))

        fill()
        while pending:
            finished, pending = wait(pending, return_when=FIRST_COMPLETED)
            for fut in finished:
                ip, payload = fut.result()
                if not payload.get("skipped"):
                    results[ip] = payload
                done_count += 1
                if on_progress is not None:
                    on_progress(min(done_count, total), total)
            fill()
    return results


def run_scan(
    *,
    ip_json: str | None = None,
    neigh_text: str | None = None,
    ping_fn: PingFn | None = None,
    tcp_fn: TcpFn | None = None,
    cancel: threading.Event | None = None,
    on_progress: ProgressFn | None = None,
    resolve_name: NameFn | None = None,
) -> list[ScanHost]:
    stop = cancel or threading.Event()
    ping = ping_fn or _default_ping
    tcp = tcp_fn or fleet.probe_tcp
    namer = resolve_name or _default_name
    targets = local_targets(ip_json=ip_json)
    neighbors = parse_neighbors(neigh_text if neigh_text is not None else _ip_neigh_text())
    store: dict[str, ScanHost] = {}

    for target in targets:
        net = ipaddress.ip_network(target.network, strict=False)
        if not isinstance(net, ipaddress.IPv4Network):
            continue
        self_row = _ensure_host(store, target.ip)
        self_row.is_self = True
        _add_source(self_row, "self")

        for neigh in neighbors:
            if _reserved(net, neigh.ip):
                continue
            try:
                if ipaddress.ip_address(neigh.ip) not in net:
                    continue
            except ValueError:
                continue
            row = _ensure_host(store, neigh.ip)
            _add_source(row, "neigh")

        candidates = [
            str(item)
            for item in net.hosts()
            if str(item) != target.ip and not stop.is_set()
        ]
        if stop.is_set():
            break
        pinged = _ping_sweep(candidates, ping, stop, on_progress)
        for ip, payload in pinged.items():
            if not payload.get("online"):
                continue
            row = _ensure_host(store, ip)
            _add_source(row, "ping")
            rtt = payload.get("rtt_ms")
            if isinstance(rtt, (int, float)):
                row.rtt_ms = float(rtt)

    live = [row for row in store.values() if not row.is_self and row.sources]
    for row in live:
        if stop.is_set():
            break
        open_ports: list[int] = []
        for port in COMMON_PORTS:
            if stop.is_set():
                break
            try:
                result = tcp(row.ip, port, timeout=0.4)
            except TypeError:
                result = tcp(row.ip, port)
            except (TypeError, OSError, TimeoutError):
                continue
            if isinstance(result, dict) and result.get("online"):
                open_ports.append(port)
        row.ports = open_ports
        if not row.name:
            row.name = namer(row.ip) or ""

    for row in store.values():
        if row.is_self and not row.name:
            row.name = namer(row.ip) or ""

    return sorted(store.values(), key=lambda item: ipaddress.ip_address(item.ip))


def to_csv(hosts: list[ScanHost]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ip", "name", "rtt_ms", "ports", "sources", "self"])
    for item in hosts:
        writer.writerow(
            [
                item.ip,
                item.name,
                "" if item.rtt_ms is None else item.rtt_ms,
                ";".join(str(p) for p in item.ports),
                ";".join(item.sources),
                "1" if item.is_self else "0",
            ]
        )
    return buf.getvalue()


def default_export_path() -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return Path.home() / "Documents" / f"hub-reseau-scan-{stamp}.csv"


def write_export(hosts: list[ScanHost], path: Path | None = None) -> Path:
    target = path or default_export_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(to_csv(hosts), encoding="utf-8")
    return target
