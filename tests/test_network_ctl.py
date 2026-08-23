# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import subprocess

import pytest

from core import home_summary, network_ctl


def test_parse_wifi_radio_disabled_without_hardware() -> None:
    available, enabled = network_ctl.parse_wifi_radio("disabled:missing")
    assert available is False
    assert enabled is False


def test_parse_wifi_radio_french_desactive() -> None:
    available, enabled = network_ctl.parse_wifi_radio("désactivé:activé")
    assert available is True
    assert enabled is False


def test_wifi_status_radio_off_ignores_stale_active(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_which(name: str) -> str | None:
        return f"/usr/bin/{name}" if name == "nmcli" else None

    def fake_run(cmd: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        if "general" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="disabled:enabled\n", stderr="")
        if "list" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="yes:Home:80:WPA2\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="disabled\n", stderr="")

    monkeypatch.setattr(network_ctl.host, "which", fake_which)
    monkeypatch.setattr(network_ctl.host, "run", fake_run)
    status = network_ctl.wifi_status()
    assert status["enabled"] is False
    assert status["available"] is True
    assert status["connections"] == []


def test_home_summary_off_when_radio_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        network_ctl,
        "wifi_status",
        lambda: {
            "available": True,
            "enabled": False,
            "connections": [{"active": True, "ssid": "Home", "signal": "80"}],
            "message": "",
        },
    )
    monkeypatch.setattr(home_summary.fleet, "load_fleet", lambda: {"machines": []})
    monkeypatch.setattr(
        home_summary.adapters,
        "snapshot",
        lambda: home_summary.adapters.AdapterSnapshot(adapters=[], gateway="", default_iface="", dns=[]),
    )
    monkeypatch.setattr(
        home_summary.vpn_ctl,
        "list_connections",
        lambda: {"available": True, "connections": []},
    )
    monkeypatch.setattr(home_summary.lan_scan, "load_last_scan", lambda: None)
    lines = home_summary.summary_lines()
    joined = "\n".join(lines)
    assert "Home" not in joined
    assert "on" not in joined.lower()
    assert any("off" in line.lower() or "désactiv" in line.lower() for line in lines)


def test_wifi_rescan_calls_nmcli(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_which(name: str) -> str | None:
        return f"/usr/bin/{name}" if name == "nmcli" else None

    def fake_run(cmd: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        if cmd[:3] == ["nmcli", "radio", "wifi"]:
            return subprocess.CompletedProcess(cmd, 0, stdout="enabled\n", stderr="")
        if "list" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="yes:Home:80:WPA2\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(network_ctl.host, "which", fake_which)
    monkeypatch.setattr(network_ctl.host, "run", fake_run)
    status = network_ctl.wifi_rescan()
    assert any(cmd[:4] == ["nmcli", "dev", "wifi", "rescan"] for cmd in calls)
    assert status["available"] is True
    assert status["connections"][0]["ssid"] == "Home"


def test_wifi_rescan_requires_nmcli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(network_ctl.host, "which", lambda _name: None)
    with pytest.raises(network_ctl.NetworkCtlError):
        network_ctl.wifi_rescan()
