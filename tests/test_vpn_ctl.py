# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import subprocess

import pytest

from core import vpn_ctl


_NMCLI = "\n".join(
    [
        "HomeWiFi:11111111-1111-1111-1111-111111111111:802-11-wireless:wlan0:yes",
        "OfficeVPN:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee:vpn::no",
        "WG-Home:12345678-1234-1234-1234-1234567890ab:wireguard:wg0:yes",
        "Wired:99999999-9999-9999-9999-999999999999:802-3-ethernet:eth0:yes",
    ]
)


def test_parse_connections_keeps_vpn_and_wireguard_only() -> None:
    rows = vpn_ctl.parse_connections(_NMCLI)
    names = [row.name for row in rows]
    assert names == ["OfficeVPN", "WG-Home"]
    assert rows[0].uuid == "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert rows[0].kind == "vpn"
    assert rows[0].active is False
    assert rows[1].kind == "wireguard"
    assert rows[1].active is True


def test_validate_uuid_rejects_garbage() -> None:
    with pytest.raises(vpn_ctl.VpnError):
        vpn_ctl.validate_uuid("not-a-uuid")
    with pytest.raises(vpn_ctl.VpnError):
        vpn_ctl.validate_uuid("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee; reboot")
    assert vpn_ctl.validate_uuid("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee") == (
        "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    )


def test_set_active_does_not_run_on_bad_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def boom(cmd: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(vpn_ctl.host, "run", boom)
    monkeypatch.setattr(vpn_ctl.executil, "run_pkexec", lambda args, **_k: boom(list(args)))
    with pytest.raises(vpn_ctl.VpnError):
        vpn_ctl.set_active("bad", True)
    assert calls == []


def test_set_active_uses_session_nmcli_first(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def ok(cmd: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")

    pkexec_calls: list[list[str]] = []

    def pkexec(args: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        pkexec_calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(vpn_ctl.host, "run", ok)
    monkeypatch.setattr(vpn_ctl.host, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(vpn_ctl.executil, "run_pkexec", pkexec)
    vpn_ctl.set_active("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", True)
    assert calls
    assert calls[0][:3] == ["nmcli", "connection", "up"]
    assert "uuid" in calls[0]
    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" in calls[0]
    assert pkexec_calls == []


def test_set_active_falls_back_to_pkexec(monkeypatch: pytest.MonkeyPatch) -> None:
    def denied(cmd: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="Error: Insufficient privileges")

    pkexec_calls: list[list[str]] = []

    def pkexec(args: list[str], **_k: object) -> subprocess.CompletedProcess[str]:
        pkexec_calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(vpn_ctl.host, "run", denied)
    monkeypatch.setattr(vpn_ctl.host, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(vpn_ctl.executil, "run_pkexec", pkexec)
    vpn_ctl.set_active("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", False)
    assert pkexec_calls
    assert pkexec_calls[0][:3] == ["nmcli", "connection", "down"]
    assert "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee" in pkexec_calls[0]


def test_list_proxy_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:8080")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:8080")
    monkeypatch.delenv("ALL_PROXY", raising=False)
    monkeypatch.delenv("NO_PROXY", raising=False)
    monkeypatch.setattr(vpn_ctl, "_gsettings_proxy_mode", lambda: "manual")
    info = vpn_ctl.list_proxy()
    assert info["http"] == "http://127.0.0.1:8080"
    assert info["https"] == "http://127.0.0.1:8080"
    assert info["mode"] == "manual"
