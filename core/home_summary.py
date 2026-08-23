# SPDX-License-Identifier: GPL-3.0-or-later
"""Network hub home dashboard cards."""

from __future__ import annotations

import socket
from dataclasses import dataclass, field

from core import adapters, fleet, i18n, lan_scan, network_ctl, vpn_ctl

CARD_PAGES: dict[str, tuple[str, str]] = {
    "ifaces": ("network", "adapters"),
    "route": ("network", "adapters"),
    "dns": ("network", "adapters"),
    "wifi": ("network", "wifi"),
    "vpn": ("vpn", ""),
    "fleet": ("fleet", ""),
    "scan": ("lan_scan", ""),
}


def card_target(key: str) -> tuple[str, str] | None:
    return CARD_PAGES.get(key)


@dataclass
class HomeCard:
    key: str
    title: str
    body: str
    detail: str = ""


@dataclass
class HomeDashboard:
    hostname: str
    cards: list[HomeCard] = field(default_factory=list)


def _wifi_card() -> HomeCard:
    wifi = network_ctl.wifi_status()
    if wifi.get("available") and wifi.get("enabled"):
        active = next((c for c in wifi.get("connections", []) if c.get("active")), None)
        if active:
            body = i18n.t(
                "home_wifi",
                ssid=active.get("ssid") or "—",
                signal=active.get("signal") or "0",
            )
        else:
            body = i18n.t("home_wifi_state", state=i18n.t("wifi_state_on"))
    elif wifi.get("available"):
        body = i18n.t("home_wifi_state", state=i18n.t("wifi_state_off"))
    elif wifi.get("message"):
        body = str(wifi.get("message"))
    else:
        body = i18n.t("wifi_hw_missing")
    return HomeCard(key="wifi", title=i18n.t("home_card_wifi"), body=body)


def _iface_card(snap: adapters.AdapterSnapshot) -> HomeCard:
    nics = adapters.up_nics(snap.adapters)
    if not nics:
        return HomeCard(key="ifaces", title=i18n.t("home_card_ifaces"), body=i18n.t("home_ifaces_none"))
    bits = []
    for nic in nics:
        ip = nic.ipv4[0] if nic.ipv4 else "—"
        bits.append(f"{nic.name} {ip}")
    return HomeCard(
        key="ifaces",
        title=i18n.t("home_card_ifaces"),
        body=" · ".join(bits),
        detail=", ".join(nic.mac for nic in nics if nic.mac),
    )


def _route_card(snap: adapters.AdapterSnapshot) -> HomeCard:
    if not snap.gateway:
        return HomeCard(key="route", title=i18n.t("home_card_route"), body="—")
    via = f" · {snap.default_iface}" if snap.default_iface else ""
    return HomeCard(
        key="route",
        title=i18n.t("home_card_route"),
        body=i18n.t("home_route", gateway=snap.gateway, iface=snap.default_iface or "—")
        if snap.default_iface
        else snap.gateway,
        detail=via.strip(" ·"),
    )


def _dns_card(snap: adapters.AdapterSnapshot) -> HomeCard:
    if not snap.dns:
        return HomeCard(key="dns", title=i18n.t("home_card_dns"), body="—")
    servers = ", ".join(snap.dns)
    if snap.dns_stub:
        body = i18n.t("home_dns_stub", servers=servers, stub=", ".join(snap.dns_stub))
    else:
        body = i18n.t("home_dns", servers=servers)
    return HomeCard(key="dns", title=i18n.t("home_card_dns"), body=body)


def _vpn_card() -> HomeCard:
    data = vpn_ctl.list_connections()
    rows = list(data.get("connections") or [])
    active = [row.name for row in rows if getattr(row, "active", False)]
    if active:
        body = i18n.t("home_vpn", names=", ".join(active))
    elif rows:
        body = i18n.t("home_vpn_inactive")
    else:
        body = i18n.t("home_vpn_none")
    return HomeCard(key="vpn", title=i18n.t("home_card_vpn"), body=body)


def _fleet_card() -> HomeCard:
    try:
        data = fleet.load_fleet()
        machines = list(data.get("machines") or [])
        online = sum(1 for m in machines if m.get("last_online") or m.get("online"))
        body = i18n.t("home_fleet", online=online, total=len(machines))
    except (OSError, TypeError, ValueError):
        body = i18n.t("home_fleet_none")
    return HomeCard(key="fleet", title=i18n.t("home_card_fleet"), body=body)


def _scan_card() -> HomeCard:
    last = lan_scan.load_last_scan()
    if not last:
        return HomeCard(key="scan", title=i18n.t("home_card_scan"), body=i18n.t("home_last_scan_none"))
    at = str(last.get("at") or "—").replace("T", " ")
    count = int(last.get("count") or 0)
    return HomeCard(
        key="scan",
        title=i18n.t("home_card_scan"),
        body=i18n.t("home_last_scan", count=count, at=at),
    )


def dashboard() -> HomeDashboard:
    try:
        host_name = socket.gethostname()
    except OSError as exc:
        host_name = str(exc)
    snap = adapters.snapshot()
    cards = [
        HomeCard(key="host", title=i18n.t("diag_hostname", name=host_name), body=host_name),
        _iface_card(snap),
        _route_card(snap),
        _dns_card(snap),
        _wifi_card(),
        _vpn_card(),
        _fleet_card(),
        _scan_card(),
    ]
    return HomeDashboard(hostname=host_name, cards=cards)


def summary_lines() -> list[str]:
    dash = dashboard()
    lines = [i18n.t("diag_hostname", name=dash.hostname)]
    for card in dash.cards:
        if card.key == "host":
            continue
        lines.append(card.body)
    return lines
