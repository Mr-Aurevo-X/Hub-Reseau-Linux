# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import subprocess

import pytest

from core import network_ctl


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
