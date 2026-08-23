# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from core import adapters, home_summary, i18n


def _snap() -> adapters.AdapterSnapshot:
    return adapters.AdapterSnapshot(
        adapters=[
            adapters.Adapter(
                name="enp37s0",
                ipv4=["192.168.129.2"],
                mac="d8:43:ae:c1:db:02",
                is_up=True,
            )
        ],
        gateway="192.168.128.1",
        default_iface="enp37s0",
        dns=["127.0.0.53"],
    )


def test_dashboard_cards(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(home_summary.adapters, "snapshot", _snap)
    monkeypatch.setattr(
        home_summary.network_ctl,
        "wifi_status",
        lambda: {"available": True, "enabled": False, "connections": [], "message": ""},
    )
    monkeypatch.setattr(
        home_summary.vpn_ctl,
        "list_connections",
        lambda: {"available": True, "connections": []},
    )
    monkeypatch.setattr(home_summary.fleet, "load_fleet", lambda: {"machines": [{"last_online": True}]})
    monkeypatch.setattr(
        home_summary.lan_scan,
        "load_last_scan",
        lambda: {"at": "2026-08-23T20:00:00", "count": 3},
    )
    previous = i18n.get_language()
    try:
        i18n.set_language("fr")
        dash = home_summary.dashboard()
        by_key = {card.key: card for card in dash.cards}
        assert "192.168.129.2" in by_key["ifaces"].body
        assert "192.168.128.1" in by_key["route"].body
        assert "127.0.0.53" in by_key["dns"].body
        assert "3" in by_key["scan"].body
        assert "1" in by_key["fleet"].body
    finally:
        i18n.set_language(previous)
