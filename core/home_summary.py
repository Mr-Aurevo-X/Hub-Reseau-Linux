# SPDX-License-Identifier: GPL-3.0-or-later
"""Network hub home summary lines."""

from __future__ import annotations

import socket

from core import fleet, i18n, network_ctl


def summary_lines() -> list[str]:
    lines: list[str] = []
    try:
        host_name = socket.gethostname()
        lines.append(i18n.t("diag_hostname", name=host_name))
    except OSError as exc:
        lines.append(i18n.t("diag_hostname", name=str(exc)))

    wifi = network_ctl.wifi_status()
    if wifi.get("available") and wifi.get("enabled"):
        active = next((c for c in wifi.get("connections", []) if c.get("active")), None)
        if active:
            lines.append(
                i18n.t("home_wifi", ssid=active.get("ssid") or "—", signal=active.get("signal") or "0")
            )
        else:
            lines.append(i18n.t("home_wifi_state", state=i18n.t("wifi_state_on")))
    elif wifi.get("available"):
        lines.append(i18n.t("home_wifi_state", state=i18n.t("wifi_state_off")))
    elif wifi.get("message"):
        lines.append(str(wifi.get("message")))
    else:
        lines.append(i18n.t("wifi_hw_missing"))

    try:
        data = fleet.load_fleet()
        machines = list(data.get("machines") or [])
        online = sum(1 for m in machines if m.get("last_online") or m.get("online"))
        lines.append(i18n.t("home_fleet", online=online, total=len(machines)))
    except (OSError, TypeError, ValueError):
        lines.append(i18n.t("home_fleet_none"))

    return lines
