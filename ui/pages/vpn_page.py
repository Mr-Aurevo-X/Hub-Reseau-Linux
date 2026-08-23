# SPDX-License-Identifier: GPL-3.0-or-later
"""VPN / proxy — list NetworkManager profiles and toggle up/down."""

from __future__ import annotations

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk  # noqa: E402

from core import i18n, vpn_ctl
from ui.components import run_in_thread, show_toast


def build(win: Any) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_top(16)
    box.set_margin_start(16)
    box.set_margin_end(16)
    title = Gtk.Label(label=i18n.t("vpn"), xalign=0)
    title.add_css_class("title-1")
    hint = Gtk.Label(label=i18n.t("vpn_hint"), xalign=0, wrap=True)
    hint.add_css_class("dim-label")
    bar = Gtk.Box(spacing=8)
    refresh = Gtk.Button(label=i18n.t("refresh"))
    refresh.connect("clicked", lambda *_: reload(win))
    bar.append(refresh)
    win._vpn_status = Gtk.Label(label="", xalign=0, wrap=True)
    win._vpn_status.add_css_class("dim-label")
    win._vpn_list = Gtk.ListBox()
    win._vpn_list.add_css_class("boxed-list")
    win._vpn_list.set_selection_mode(Gtk.SelectionMode.NONE)
    proxy_title = Gtk.Label(label=i18n.t("vpn_proxy"), xalign=0)
    proxy_title.add_css_class("heading")
    win._vpn_proxy = Gtk.Label(label="", xalign=0, wrap=True)
    scroll = Gtk.ScrolledWindow(vexpand=True)
    scroll.set_child(win._vpn_list)
    box.append(title)
    box.append(hint)
    box.append(bar)
    box.append(win._vpn_status)
    box.append(scroll)
    box.append(proxy_title)
    box.append(win._vpn_proxy)
    win._vpn_reload = lambda: reload(win)
    reload(win)
    return box


def _clear_list(listbox: Gtk.ListBox) -> None:
    while (row := listbox.get_row_at_index(0)) is not None:
        listbox.remove(row)


def reload(win: Any) -> None:
    setter = getattr(win, "_set_busy", None)
    if callable(setter):
        setter(True)

    def work() -> tuple[dict[str, Any], dict[str, str]]:
        return vpn_ctl.list_connections(), vpn_ctl.list_proxy()

    def done(result: Any, error: BaseException | None) -> None:
        if callable(setter):
            setter(False)
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("vpn_error", detail=str(error)))
            return
        data, proxy = result
        _render_connections(win, data)
        _render_proxy(win, proxy)

    run_in_thread(work, done)


def _render_connections(win: Any, data: dict[str, Any]) -> None:
    _clear_list(win._vpn_list)
    if not data.get("available"):
        win._vpn_status.set_text(i18n.t("vpn_no_nmcli"))
        return
    message = str(data.get("message") or "")
    rows = list(data.get("connections") or [])
    if message:
        win._vpn_status.set_text(message)
    elif not rows:
        win._vpn_status.set_text(i18n.t("vpn_empty"))
    else:
        win._vpn_status.set_text("")
    for item in rows:
        row = Adw.ActionRow()
        row.set_title(item.name or item.uuid)
        state = i18n.t("vpn_active") if item.active else i18n.t("vpn_inactive")
        row.set_subtitle(f"{item.kind} · {state}")
        btn = Gtk.Button(label=i18n.t("vpn_deactivate" if item.active else "vpn_activate"))
        btn.connect(
            "clicked",
            lambda *_a, uid=item.uuid, active=item.active, name=item.name: toggle(win, uid, not active, name),
        )
        row.add_suffix(btn)
        win._vpn_list.append(row)


def _render_proxy(win: Any, proxy: dict[str, str]) -> None:
    lines: list[str] = []
    mode = (proxy.get("mode") or "").strip()
    if mode:
        lines.append(i18n.t("vpn_proxy_mode", mode=mode))
    for key, label in (("http", "HTTP_PROXY"), ("https", "HTTPS_PROXY"), ("all", "ALL_PROXY"), ("no", "NO_PROXY")):
        value = (proxy.get(key) or "").strip()
        if value:
            lines.append(f"{label}={value}")
    win._vpn_proxy.set_text("\n".join(lines) if lines else i18n.t("vpn_proxy_none"))


def toggle(win: Any, uuid: str, active: bool, name: str) -> None:
    setter = getattr(win, "_set_busy", None)
    if callable(setter):
        setter(True)

    def work() -> None:
        vpn_ctl.set_active(uuid, active)

    def done(_result: Any, error: BaseException | None) -> None:
        if callable(setter):
            setter(False)
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("vpn_error", detail=str(error)))
            reload(win)
            return
        state = i18n.t("vpn_active") if active else i18n.t("vpn_inactive")
        show_toast(win._toast_overlay, i18n.t("vpn_done", name=name, state=state))
        reload(win)

    run_in_thread(work, done)
