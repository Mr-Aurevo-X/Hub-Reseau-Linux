# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from core import i18n, network_diag
from ui.pages import PAGE_KEYS, _BUILD_ATTR

_UNAVAILABLE = "traceroute/mtr indisponible"
_ROOT = Path(__file__).resolve().parents[1]


def test_traceroute_lines_when_binaries_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(network_diag.shutil, "which", lambda _name: None)
    assert network_diag.traceroute_lines("1.1.1.1") == [_UNAVAILABLE]


def test_traceroute_lines_prefers_mtr(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_which(name: str) -> str | None:
        return "/usr/bin/mtr" if name == "mtr" else None

    def fake_run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="1. 9.9.9.9\n2. 1.1.1.1\n", stderr="")

    monkeypatch.setattr(network_diag.shutil, "which", fake_which)
    monkeypatch.setattr(network_diag.subprocess, "run", fake_run)
    lines = network_diag.traceroute_lines("example.test")
    assert calls, "mtr should be invoked"
    assert calls[0][0] == "mtr"
    assert "-n" in calls[0]
    assert "-c" in calls[0]
    assert "1" in calls[0]
    assert calls[0][-1] == "example.test"
    assert lines == ["1. 9.9.9.9", "2. 1.1.1.1"]


def test_traceroute_lines_falls_back_to_traceroute(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_which(name: str) -> str | None:
        return "/usr/bin/traceroute" if name == "traceroute" else None

    def fake_run(cmd: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="hop 1\n", stderr="")

    monkeypatch.setattr(network_diag.shutil, "which", fake_which)
    monkeypatch.setattr(network_diag.subprocess, "run", fake_run)
    lines = network_diag.traceroute_lines("192.0.2.1")
    assert calls[0][:6] == ["traceroute", "-n", "-w", "2", "-m", "12"]
    assert calls[0][-1] == "192.0.2.1"
    assert lines == ["hop 1"]


def test_traceroute_lines_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(network_diag.shutil, "which", lambda name: "/usr/bin/mtr" if name == "mtr" else None)

    def boom(*_a: object, **_k: object) -> object:
        raise OSError("no exec")

    monkeypatch.setattr(network_diag.subprocess, "run", boom)
    assert network_diag.traceroute_lines("1.1.1.1") == [_UNAVAILABLE]


def test_quick_report_includes_traceroute_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(network_diag.shutil, "which", lambda _name: None)
    monkeypatch.setattr(network_diag.socket, "gethostname", lambda: "testhost")
    monkeypatch.setattr(network_diag.socket, "getaddrinfo", lambda *_a, **_k: [])
    monkeypatch.setattr(network_diag, "traceroute_lines", lambda host: [f"TR {host}"])
    lines = network_diag.quick_report("8.8.8.8")
    assert "TR 8.8.8.8" in lines
    assert any(line.startswith("Hostname:") for line in lines)


def test_export_report_joins_quick_report(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(network_diag, "quick_report", lambda host: ["alpha", "beta", host])
    assert network_diag.export_report("host.lan") == "alpha\nbeta\nhost.lan"


def test_vpn_i18n_fr_en() -> None:
    previous = i18n.get_language()
    try:
        i18n.set_language("fr")
        assert i18n.t("vpn") != "vpn"
        assert i18n.t("vpn_hint") == "À venir — VPN / proxy système (lecture locale plus tard)"
        i18n.set_language("en")
        assert i18n.t("vpn") != "vpn"
        hint = i18n.t("vpn_hint")
        assert hint != "vpn_hint"
        assert hint != "À venir — VPN / proxy système (lecture locale plus tard)"
        assert "VPN" in hint
    finally:
        i18n.set_language(previous)


def test_vpn_page_registered() -> None:
    assert "vpn" in PAGE_KEYS
    assert _BUILD_ATTR["vpn"] == "_build_vpn_page"


def test_vpn_page_module_is_placeholder() -> None:
    from ui.pages import vpn_page

    assert callable(vpn_page.build)
    src = (_ROOT / "ui" / "pages" / "vpn_page.py").read_text(encoding="utf-8")
    assert "vpn_hint" in src
    assert "Switch" not in src
    assert "ToggleButton" not in src


def test_diag_ui_exports_and_vpn_builder() -> None:
    text = (_ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")
    assert "def _build_vpn_page" in text
    assert "network_diag.export_report" in text
    assert "get_clipboard" in text
