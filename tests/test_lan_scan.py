# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import ipaddress
import json
import threading
from pathlib import Path

import pytest

from core import lan_scan


def test_clamp_public_ipv4_raises() -> None:
    with pytest.raises(lan_scan.LanScanError):
        lan_scan.clamp_network("8.8.8.8", 24)


def test_clamp_wide_prefix_to_slash24() -> None:
    net = lan_scan.clamp_network("192.168.40.12", 16)
    assert str(net) == "192.168.40.0/24"
    assert net.prefixlen == 24


def test_clamp_keeps_slash24_or_narrower() -> None:
    net = lan_scan.clamp_network("10.1.2.9", 24)
    assert str(net) == "10.1.2.0/24"
    net25 = lan_scan.clamp_network("10.1.2.9", 25)
    assert str(net25) == "10.1.2.0/25"


def test_local_targets_skips_public_and_loopback() -> None:
    payload = json.dumps(
        [
            {
                "ifname": "lo",
                "addr_info": [{"family": "inet", "local": "127.0.0.1", "prefixlen": 8}],
            },
            {
                "ifname": "wan0",
                "addr_info": [{"family": "inet", "local": "203.0.113.8", "prefixlen": 24}],
            },
            {
                "ifname": "wlan0",
                "addr_info": [{"family": "inet", "local": "192.168.1.40", "prefixlen": 16}],
            },
        ]
    )
    targets = lan_scan.local_targets(ip_json=payload)
    assert len(targets) == 1
    assert targets[0].iface == "wlan0"
    assert targets[0].ip == "192.168.1.40"
    assert targets[0].network == "192.168.1.0/24"


def test_parse_neighbors_filters_states() -> None:
    text = "\n".join(
        [
            "192.168.1.1 dev wlan0 lladdr aa:bb:cc:dd:ee:ff REACHABLE",
            "192.168.1.2 dev wlan0 lladdr 11:22:33:44:55:66 STALE",
            "192.168.1.3 dev wlan0 FAILED",
            "fe80::1 dev wlan0 lladdr aa:bb:cc:dd:ee:01 DELAY",
            "10.0.0.9 dev eth0 lladdr aa:bb:cc:dd:ee:02 PROBE",
        ]
    )
    rows = lan_scan.parse_neighbors(text)
    ips = {row.ip for row in rows}
    assert ips == {"192.168.1.1", "192.168.1.2", "10.0.0.9"}
    assert all(row.source == "neigh" for row in rows)


def test_run_scan_marks_self_excludes_network_broadcast_and_honors_cancel() -> None:
    payload = json.dumps(
        [
            {
                "ifname": "eth0",
                "addr_info": [{"family": "inet", "local": "192.168.1.10", "prefixlen": 24}],
            }
        ]
    )
    seen: list[str] = []
    cancel = threading.Event()

    def ping(address: str) -> dict[str, object]:
        seen.append(address)
        if address == "192.168.1.20":
            cancel.set()
            return {"online": True, "rtt_ms": 4.0}
        return {"online": False, "rtt_ms": None}

    def tcp(_address: str, _port: int, **_k: object) -> dict[str, object]:
        return {"online": False}

    hosts = lan_scan.run_scan(
        ip_json=payload,
        neigh_text="192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE\n",
        ping_fn=ping,
        tcp_fn=tcp,
        cancel=cancel,
        resolve_name=lambda _ip: "",
    )
    ips = {h.ip for h in hosts}
    assert "192.168.1.10" in ips
    self_host = next(h for h in hosts if h.ip == "192.168.1.10")
    assert self_host.is_self is True
    assert "self" in self_host.sources
    assert "192.168.1.0" not in ips
    assert "192.168.1.255" not in ips
    assert "192.168.1.1" in ips
    assert "192.168.1.20" in seen
    assert len(seen) < 250


def test_run_scan_probes_common_ports_on_live_hosts() -> None:
    payload = json.dumps(
        [
            {
                "ifname": "eth0",
                "addr_info": [{"family": "inet", "local": "10.0.0.2", "prefixlen": 30}],
            }
        ]
    )
    probed: list[tuple[str, int]] = []

    def ping(address: str) -> dict[str, object]:
        return {"online": address == "10.0.0.1", "rtt_ms": 1.5 if address == "10.0.0.1" else None}

    def tcp(address: str, port: int, **_k: object) -> dict[str, object]:
        probed.append((address, port))
        return {"online": port in (22, 443)}

    hosts = lan_scan.run_scan(
        ip_json=payload,
        neigh_text="",
        ping_fn=ping,
        tcp_fn=tcp,
        cancel=threading.Event(),
        resolve_name=lambda ip: "gw.lan" if ip == "10.0.0.1" else "",
    )
    live = next(h for h in hosts if h.ip == "10.0.0.1")
    assert live.ports == [22, 443]
    assert live.name == "gw.lan"
    assert live.rtt_ms == 1.5
    assert "ping" in live.sources
    assert {p for _ip, p in probed} == set(lan_scan.COMMON_PORTS)
    assert all(ip == "10.0.0.1" for ip, _p in probed)


def test_to_csv_and_default_export_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lan_scan.Path, "home", classmethod(lambda cls: tmp_path))
    host = lan_scan.ScanHost(
        ip="192.168.1.4",
        name="nas",
        rtt_ms=2.2,
        ports=[22, 445],
        sources=["neigh", "ping"],
        is_self=False,
    )
    text = lan_scan.to_csv([host])
    assert text.splitlines()[0] == "ip,name,rtt_ms,ports,sources,self"
    assert "192.168.1.4" in text
    assert "22;445" in text
    path = lan_scan.default_export_path()
    assert path.parent == tmp_path / "Documents"
    assert path.name.startswith("hub-reseau-scan-")
    assert path.suffix == ".csv"
