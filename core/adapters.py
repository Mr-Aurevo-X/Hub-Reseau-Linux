# SPDX-License-Identifier: GPL-3.0-or-later
"""Local adapters, default route, DNS, and /proc/net/dev counters."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core import host

_SKIP_PREFIXES = ("veth",)


@dataclass
class Adapter:
    name: str
    ipv4: list[str] = field(default_factory=list)
    ipv6: list[str] = field(default_factory=list)
    mac: str = ""
    is_up: bool = False
    is_loopback: bool = False
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_bps: float = 0.0
    tx_bps: float = 0.0


@dataclass
class DefaultRoute:
    gateway: str
    iface: str


@dataclass
class AdapterSnapshot:
    adapters: list[Adapter]
    gateway: str = ""
    default_iface: str = ""
    dns: list[str] = field(default_factory=list)


def parse_addr_json(text: str) -> list[Adapter]:
    try:
        items = json.loads(text or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(items, list):
        return []
    out: list[Adapter] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("ifname") or "")
        if not name:
            continue
        flags = {str(f).upper() for f in (item.get("flags") or [])}
        ipv4: list[str] = []
        ipv6: list[str] = []
        for info in item.get("addr_info") or []:
            if not isinstance(info, dict):
                continue
            local = str(info.get("local") or "")
            if not local:
                continue
            if info.get("family") == "inet6":
                ipv6.append(local)
            elif info.get("family") == "inet":
                ipv4.append(local)
        out.append(
            Adapter(
                name=name,
                ipv4=ipv4,
                ipv6=ipv6,
                mac=str(item.get("address") or ""),
                is_up=str(item.get("operstate") or "").upper() == "UP" or "UP" in flags,
                is_loopback="LOOPBACK" in flags or name == "lo",
            )
        )
    return out


def up_nics(rows: list[Adapter]) -> list[Adapter]:
    return [
        row
        for row in rows
        if row.is_up and not row.is_loopback and not row.name.startswith(_SKIP_PREFIXES)
    ]


def parse_default_route(text: str) -> DefaultRoute | None:
    try:
        items = json.loads(text or "[]")
    except json.JSONDecodeError:
        return None
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        dst = str(item.get("dst") or "")
        gateway = str(item.get("gateway") or "")
        iface = str(item.get("dev") or "")
        if dst in {"default", "0.0.0.0/0"} and gateway:
            return DefaultRoute(gateway=gateway, iface=iface)
    return None


def parse_resolv_conf(text: str) -> list[str]:
    servers: list[str] = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) >= 2 and parts[0] == "nameserver":
            host_name = parts[1].strip()
            if host_name and host_name not in servers:
                servers.append(host_name)
    return servers[:8]


def parse_netdev(text: str) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for line in (text or "").splitlines():
        if ":" not in line or line.strip().startswith("Inter") or line.strip().startswith("face"):
            continue
        name, rest = line.split(":", 1)
        iface = name.strip()
        cols = rest.split()
        if len(cols) < 9:
            continue
        try:
            out[iface] = (int(cols[0]), int(cols[8]))
        except ValueError:
            continue
    return out


def rates_from_samples(
    before: dict[str, tuple[int, int]],
    after: dict[str, tuple[int, int]],
    elapsed: float,
) -> dict[str, tuple[float, float]]:
    dt = elapsed if elapsed > 0 else 1.0
    out: dict[str, tuple[float, float]] = {}
    for name, (rx2, tx2) in after.items():
        rx1, tx1 = before.get(name, (rx2, tx2))
        out[name] = (max(rx2 - rx1, 0) / dt, max(tx2 - tx1, 0) / dt)
    return out


def format_bytes(value: int) -> str:
    size = float(max(value, 0))
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TiB"


def format_bps(value: float) -> str:
    return f"{format_bytes(int(max(value, 0)))}/s"


def _read_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def _ip_json(args: list[str]) -> str:
    if host.which("ip") is None:
        return "[]"
    try:
        completed = host.run(
            ["ip", "-j", *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, TimeoutError):
        return "[]"
    return completed.stdout or "[]"


def collect_snapshot(
    *,
    addr_json: str | None = None,
    route_json: str | None = None,
    resolv_text: str | None = None,
    netdev_text: str | None = None,
    prev_counters: dict[str, tuple[int, int]] | None = None,
    elapsed: float = 0.0,
) -> AdapterSnapshot:
    rows = parse_addr_json(addr_json if addr_json is not None else _ip_json(["addr"]))
    route = parse_default_route(
        route_json if route_json is not None else _ip_json(["route", "show", "default"])
    )
    dns = parse_resolv_conf(resolv_text if resolv_text is not None else _read_text("/etc/resolv.conf"))
    counters = parse_netdev(netdev_text if netdev_text is not None else _read_text("/proc/net/dev"))
    rates = rates_from_samples(prev_counters or {}, counters, elapsed) if prev_counters else {}
    for row in rows:
        rx, tx = counters.get(row.name, (0, 0))
        row.rx_bytes = rx
        row.tx_bytes = tx
        row.rx_bps, row.tx_bps = rates.get(row.name, (0.0, 0.0))
    return AdapterSnapshot(
        adapters=rows,
        gateway=route.gateway if route else "",
        default_iface=route.iface if route else "",
        dns=dns,
    )


def snapshot(**kwargs: Any) -> AdapterSnapshot:
    return collect_snapshot(**kwargs)
