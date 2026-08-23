# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

import pytest

from core import updater


def test_update_channel_is_flatpak_only() -> None:
    assert updater.update_channel() == "flatpak"
    url = updater.public_download_url("1.4.11")
    assert url.endswith("org.mraurevox.HubReseau.flatpak")
    assert "Hub-Reseau-Linux/releases/download/v" in url
    assert "linux-flatpak-releases" not in url
    assert "linux-releases" not in url
    assert "Gest_Linux_Pro" not in url


def test_flatpak_install_block_includes_menu_shortcut() -> None:
    info = {"version": "2.2.3", "channel": "flatpak"}
    block = updater.flatpak_install_block(info)
    assert "INSTALLER-RACCOURCI-FLATPAK.sh" in block
    assert "bash ./INSTALLER-RACCOURCI-FLATPAK.sh" in block
    assert "rm -f org.mraurevox.HubReseau.flatpak" in block
    assert "wget --no-continue -O org.mraurevox.HubReseau.flatpak" in block
    assert updater.SHORTCUT_DIRECT.format(version="2.2.3") in block


def test_native_commands_are_install_script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert "install.sh" in updater.format_update_dialog_commands({"channel": "native", "version": "1.3.0"})
    monkeypatch.setattr(updater, "updates_dir", lambda: tmp_path)
    text = updater.write_update_script({"channel": "native", "version": "1.3.0"}).read_text(
        encoding="utf-8"
    )
    assert "bash install.sh --skip-deps" in text
    assert "tar " not in text
    assert "Gest_Linux" not in text


def test_update_urls_allow_hub_repo_only() -> None:
    gest_native = (
        "https://github.com/Mr-Aurevo-X/linux-releases/releases/download/"
        "Gest_Linux_Pro-v1.4.4/Gest_Linux_Pro-1.4.4.tar.gz"
    )
    ok_flatpak = (
        "https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/"
        "v1.4.4/org.mraurevox.HubReseau.flatpak"
    )
    ok_cdn = "https://release-assets.githubusercontent.com/github-production-release-asset/abc"
    with pytest.raises(updater.UpdateError):
        updater._require_allowed_url(gest_native, kind="download")
    assert updater._require_allowed_url(ok_flatpak, kind="download") == ok_flatpak
    assert updater._require_allowed_url(ok_cdn, kind="any") == ok_cdn
    with pytest.raises(updater.UpdateError):
        updater._require_allowed_url(ok_cdn, kind="download")
    with pytest.raises(updater.UpdateError):
        updater._require_allowed_url(
            "https://api.github.com/repos/Mr-Aurevo-X/linux-releases/releases",
            kind="api",
        )
    assert updater._require_allowed_url(updater.FLATPAK_RELEASES_API, kind="api") == updater.FLATPAK_RELEASES_API


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases",
        "https://evil.example/malware.tar.gz",
        "https://github.com/evil/malware/releases/download/x/x.tar.gz",
        "https://api.github.com/repos/evil/malware/releases",
        "file:///etc/passwd",
        "https://user:pass@github.com/Mr-Aurevo-X/Hub-Reseau-Linux/x",
        "https://github.com:8443/Mr-Aurevo-X/Hub-Reseau-Linux/x",
        "javascript:alert(1)",
        "https://github.com/Mr-Aurevo-X/linux-releases/releases/download/x/x.tar.gz",
    ],
)
def test_update_urls_reject_backdoors(url: str) -> None:
    with pytest.raises(updater.UpdateError):
        updater._require_allowed_url(url, kind="any")


def test_write_update_script_prefers_wget(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updater, "updates_dir", lambda: tmp_path)
    url = (
        "https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/"
        "v1.4.8/org.mraurevox.HubReseau.flatpak"
    )
    path = updater.write_update_script(
        {"download_url": url, "channel": "flatpak", "version": "1.4.8"}
    )
    text = path.read_text(encoding="utf-8")
    assert "command -v wget" in text
    assert text.find("command -v wget") < text.find("command -v curl")
    assert "*curl" not in text
    assert "sudo apt install wget" in text


def test_asset_url_ignores_foreign_download() -> None:
    item = {
        "assets": [
            {
                "name": "org.mraurevox.HubReseau.flatpak",
                "browser_download_url": "https://evil.example/backdoor.flatpak",
            }
        ]
    }
    url = updater._asset_url(item, "1.4.4", "flatpak")
    assert url == updater.public_download_url("1.4.4", "flatpak")
    updater._require_allowed_url(url, kind="download")
