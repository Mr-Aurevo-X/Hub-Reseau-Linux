# SPDX-License-Identifier: GPL-3.0-or-later
"""Network hub home summary lines."""

from __future__ import annotations

import socket
from typing import Any

from core import fleet, network_ctl


def summary_lines() -> list[str]:
    lines: list[str] = []
    try:
        host = socket.gethostname()
        lines.append(f"Hostname: {host}")
    except OSError as exc:
        lines.append(f"Hostname: {exc}")

    wifi = network_ctl.wifi_status()
    if wifi.get("available"):
        state = "on" if wifi.get("enabled") else "off"
        active = next((c for c in wifi.get("connections", []) if c.get("active")), None)
        if active:
            lines.append(f"Wi-Fi: {active.get('ssid')} ({active.get('signal')}%)")
        else:
            lines.append(f"Wi-Fi: {state}")
    else:
        lines.append(str(wifi.get("message") or "Wi-Fi: nmcli indisponible"))

    try:
        data = fleet.load_fleet()
        machines = list(data.get("machines") or [])
        online = sum(1 for m in machines if m.get("last_online") or m.get("online"))
        lines.append(f"Parc: {online}/{len(machines)} en ligne")
    except (OSError, TypeError, ValueError):
        lines.append("Parc: —")

    return lines
