# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json

from core import adapters


_ADDR = json.dumps(
    [
        {
            "ifname": "lo",
            "operstate": "UNKNOWN",
            "address": "00:00:00:00:00:00",
            "flags": ["LOOPBACK", "UP"],
            "addr_info": [{"family": "inet", "local": "127.0.0.1", "prefixlen": 8}],
        },
        {
            "ifname": "enp37s0",
            "operstate": "UP",
            "address": "d8:43:ae:c1:db:02",
            "flags": ["BROADCAST", "UP"],
            "addr_info": [{"family": "inet", "local": "192.168.129.2", "prefixlen": 24}],
        },
        {
            "ifname": "docker0",
            "operstate": "DOWN",
            "address": "9a:b4:bb:b4:4f:a5",
            "flags": ["BROADCAST"],
            "addr_info": [{"family": "inet", "local": "172.17.0.1", "prefixlen": 16}],
        },
    ]
)

_ROUTE = json.dumps(
    [{"dst": "default", "gateway": "192.168.128.1", "dev": "enp37s0", "protocol": "dhcp"}]
)

_NETDEV = """\
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo: 1000 1 0 0 0 0 0 0 1000 1 0 0 0 0 0 0
enp37s0: 5000 10 0 0 0 0 0 0 2000 8 0 0 0 0 0 0
"""


def test_parse_addr_skips_loopback_for_up_list() -> None:
    rows = adapters.parse_addr_json(_ADDR)
    names = [r.name for r in rows]
    assert names == ["lo", "enp37s0", "docker0"]
    up = adapters.up_nics(rows)
    assert [r.name for r in up] == ["enp37s0"]
    nic = next(r for r in rows if r.name == "enp37s0")
    assert nic.ipv4 == ["192.168.129.2"]
    assert nic.mac == "d8:43:ae:c1:db:02"
    assert nic.is_up is True
    assert nic.is_loopback is False


def test_parse_default_route() -> None:
    route = adapters.parse_default_route(_ROUTE)
    assert route is not None
    assert route.gateway == "192.168.128.1"
    assert route.iface == "enp37s0"


def test_parse_resolv_nameservers() -> None:
    text = "# Generated\nsearch home\nnameserver 127.0.0.53\nnameserver 1.1.1.1\n"
    assert adapters.parse_resolv_conf(text) == ["127.0.0.53", "1.1.1.1"]


def test_parse_netdev_bytes() -> None:
    counters = adapters.parse_netdev(_NETDEV)
    assert counters["enp37s0"] == (5000, 2000)
    rates = adapters.rates_from_samples(
        {"enp37s0": (5000, 2000)},
        {"enp37s0": (15000, 4000)},
        elapsed=2.0,
    )
    assert rates["enp37s0"] == (5000.0, 1000.0)


def test_snapshot_merges_route_and_counters() -> None:
    snap = adapters.snapshot(
        addr_json=_ADDR,
        route_json=_ROUTE,
        resolv_text="nameserver 9.9.9.9\n",
        netdev_text=_NETDEV,
    )
    assert snap.gateway == "192.168.128.1"
    assert snap.dns == ["9.9.9.9"]
    nic = next(r for r in snap.adapters if r.name == "enp37s0")
    assert nic.rx_bytes == 5000
    assert nic.tx_bytes == 2000
    assert snap.default_iface == "enp37s0"
