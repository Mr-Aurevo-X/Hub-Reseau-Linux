# SPDX-License-Identifier: GPL-3.0-or-later
"""NetworkManager VPN / WireGuard + local proxy env (no profile creation)."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from core import executil, host

_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_VPN_TYPES = frozenset({"vpn", "wireguard"})
_NMCLI_FIELDS = ["NAME", "UUID", "TYPE", "DEVICE", "ACTIVE"]


class VpnError(Exception):
    """Invalid VPN operation or missing tooling."""


@dataclass
class VpnConnection:
    name: str
    uuid: str
    kind: str
    device: str
    active: bool


def validate_uuid(raw: str) -> str:
    text = (raw or "").strip()
    if not _UUID_RE.fullmatch(text):
        raise VpnError("UUID VPN invalide")
    return text


def parse_connections(text: str) -> list[VpnConnection]:
    rows: list[VpnConnection] = []
    seen: set[str] = set()
    for line in (text or "").splitlines():
        parts = line.split(":")
        if len(parts) < 5:
            continue
        name, uuid, kind, device, active = parts[0], parts[1], parts[2], parts[3], parts[4]
        kind_l = kind.strip().lower()
        if kind_l not in _VPN_TYPES:
            continue
        try:
            uid = validate_uuid(uuid)
        except VpnError:
            continue
        if uid in seen:
            continue
        seen.add(uid)
        rows.append(
            VpnConnection(
                name=name,
                uuid=uid,
                kind=kind_l,
                device=device,
                active=active.strip().lower() == "yes",
            )
        )
    return rows


def list_connections() -> dict[str, Any]:
    if host.which("nmcli") is None:
        return {"available": False, "connections": [], "message": "nmcli introuvable"}
    try:
        completed = host.run(
            ["nmcli", "-t", "-f", ",".join(_NMCLI_FIELDS), "connection", "show"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, TimeoutError) as exc:
        return {"available": True, "connections": [], "message": str(exc)}
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "échec nmcli").strip()
        return {"available": True, "connections": [], "message": err}
    return {
        "available": True,
        "connections": parse_connections(completed.stdout or ""),
        "message": "",
    }


def _gsettings_proxy_mode() -> str:
    if host.which("gsettings") is None:
        return ""
    try:
        completed = host.run(
            ["gsettings", "get", "org.gnome.system.proxy", "mode"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, TimeoutError):
        return ""
    if completed.returncode != 0:
        return ""
    return (completed.stdout or "").strip().strip("'\"")


def _env_proxy(name: str) -> str:
    return (os.environ.get(name) or os.environ.get(name.lower()) or "").strip()


def list_proxy() -> dict[str, str]:
    return {
        "http": _env_proxy("HTTP_PROXY"),
        "https": _env_proxy("HTTPS_PROXY"),
        "all": _env_proxy("ALL_PROXY"),
        "no": _env_proxy("NO_PROXY"),
        "mode": _gsettings_proxy_mode(),
    }


def set_active(uuid: str, active: bool) -> None:
    uid = validate_uuid(uuid)
    if host.which("nmcli") is None:
        raise VpnError("nmcli introuvable")
    action = "up" if active else "down"
    cmd = ["nmcli", "connection", action, "uuid", uid]
    try:
        completed = host.run(cmd, check=False, capture_output=True, text=True, timeout=90)
    except (OSError, TimeoutError) as exc:
        completed = None
        session_err = str(exc)
    else:
        if completed.returncode == 0:
            return
        session_err = (completed.stderr or completed.stdout or f"nmcli {action} failed").strip()
    if host.which("pkexec") is None:
        raise VpnError(session_err)
    try:
        privileged = executil.run_pkexec(cmd, timeout=90)
    except executil.ExecError as exc:
        raise VpnError(str(exc)) from exc
    if privileged.returncode != 0:
        err = (privileged.stderr or privileged.stdout or session_err).strip()
        raise VpnError(err or session_err)
