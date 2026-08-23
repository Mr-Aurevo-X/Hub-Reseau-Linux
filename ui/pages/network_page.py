# SPDX-License-Identifier: GPL-3.0-or-later
"""Network page — adapters first, then Wi-Fi / connections."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Adw, Gdk, Gtk  # noqa: E402

from core import adapters, connections, i18n, network_ctl, settings as app_settings
from ui.adw_compat import make_message_dialog, make_switch_row, response_appearance, set_placeholder_text
from ui.components import confirm_dialog, make_spinner, run_in_thread, show_toast
from ui.page_helpers import make_filter_chips


def _section(title: str, child: Gtk.Widget) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    label = Gtk.Label(label=title, xalign=0)
    label.add_css_class("title-4")
    box.append(label)
    box.append(child)
    return box


def _clear_listbox(listbox: Gtk.ListBox) -> None:
    while True:
        row = listbox.get_row_at_index(0)
        if row is None:
            break
        listbox.remove(row)


def build(win: Any) -> Gtk.Widget:
    if not getattr(win, "_network_chip", None):
        win._network_chip = "adapters"
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    bar.add_css_class("page-toolbar")
    title = Gtk.Label(label=i18n.t("network"), xalign=0)
    title.add_css_class("heading")
    title.set_hexpand(True)
    win._network_spinner = make_spinner(size=18)
    win._network_spinner.set_visible(False)
    refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
    refresh_btn.connect("clicked", lambda *_: refresh(win, show_spinner=True))
    scan_btn = Gtk.Button(label=i18n.t("wifi_scan"))
    scan_btn.connect("clicked", lambda *_: rescan_wifi(win))
    allow_btn = Gtk.Button(label=i18n.t("conn_allowlist_add"))
    allow_btn.connect("clicked", lambda *_: open_allowlist_dialog(win))
    bar.append(title)
    bar.append(win._network_spinner)
    bar.append(scan_btn)
    bar.append(allow_btn)
    bar.append(refresh_btn)
    root.append(bar)

    chips, win._network_chip_buttons = make_filter_chips(
        (
            ("adapters", i18n.t("adapters_chip")),
            ("wifi", i18n.t("wifi_chip")),
            ("conn", i18n.t("conn_chip")),
        ),
        active_key=win._network_chip,
        on_change=lambda key: set_chip(win, key),
    )
    root.append(chips)

    win._network_stack = Gtk.Stack()
    win._network_stack.set_vexpand(True)
    win._network_stack.set_hexpand(True)

    adapters_scrolled = Gtk.ScrolledWindow()
    adapters_scrolled.set_vexpand(True)
    adapters_clamp = Adw.Clamp(maximum_size=900)
    adapters_clamp.set_margin_start(12)
    adapters_clamp.set_margin_end(12)
    adapters_clamp.set_margin_bottom(12)
    adapters_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    win._adapters_summary = Gtk.Label(label="—", xalign=0, wrap=True)
    win._adapters_summary.add_css_class("dim-label")
    win._adapters_list = Gtk.ListBox()
    win._adapters_list.set_selection_mode(Gtk.SelectionMode.NONE)
    win._adapters_list.add_css_class("boxed-list")
    adapters_box.append(win._adapters_summary)
    adapters_box.append(_section(i18n.t("adapters"), win._adapters_list))
    adapters_clamp.set_child(adapters_box)
    adapters_scrolled.set_child(adapters_clamp)

    wifi_scrolled = Gtk.ScrolledWindow()
    wifi_scrolled.set_vexpand(True)
    wifi_clamp = Adw.Clamp(maximum_size=900)
    wifi_clamp.set_margin_start(12)
    wifi_clamp.set_margin_end(12)
    wifi_clamp.set_margin_bottom(12)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)

    wifi_group = Adw.PreferencesGroup()
    wifi_group.set_title("Wi-Fi")
    win._wifi_switch_row = make_switch_row()
    win._wifi_switch_row.set_title(i18n.t("wifi_radio"))
    win._wifi_switch_row.set_subtitle("—")
    win._wifi_switch_row.connect("notify::active", lambda row, *_: on_wifi_switch(win, row))
    win._wifi_switch_guard = False
    wifi_group.add(win._wifi_switch_row)
    box.append(wifi_group)

    win._wifi_list = Gtk.ListBox()
    win._wifi_list.set_selection_mode(Gtk.SelectionMode.NONE)
    win._wifi_list.add_css_class("boxed-list")
    box.append(_section(i18n.t("networks_found"), win._wifi_list))

    bt_group = Adw.PreferencesGroup()
    bt_group.set_title("Bluetooth")
    win._bt_switch_row = make_switch_row()
    win._bt_switch_row.set_title(i18n.t("bt_power"))
    win._bt_switch_row.set_subtitle("—")
    win._bt_switch_row.connect("notify::active", lambda row, *_: on_bt_switch(win, row))
    win._bt_switch_guard = False
    bt_group.add(win._bt_switch_row)
    box.append(bt_group)

    win._bt_list = Gtk.ListBox()
    win._bt_list.set_selection_mode(Gtk.SelectionMode.NONE)
    win._bt_list.add_css_class("boxed-list")
    box.append(_section(i18n.t("devices"), win._bt_list))

    wifi_clamp.set_child(box)
    wifi_scrolled.set_child(wifi_clamp)

    conn_root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    conn_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    conn_bar.set_margin_start(12)
    conn_bar.set_margin_end(12)
    conn_bar.set_margin_bottom(8)
    win._conn_status = Gtk.Label(label="—", xalign=0)
    win._conn_status.set_hexpand(True)
    win._conn_status.set_wrap(True)
    win._conn_status.add_css_class("dim-label")
    export_btn = Gtk.Button(label=i18n.t("conn_export"))
    export_btn.connect("clicked", lambda *_: export_connections(win))
    admin_btn = Gtk.Button(label=i18n.t("conn_load_admin"))
    admin_btn.connect("clicked", lambda *_: refresh_connections(win, show_spinner=True, privileged=True))
    track = getattr(win, "_track_privileged", None)
    if callable(track):
        track(admin_btn)
    conn_bar.append(win._conn_status)
    conn_bar.append(export_btn)
    conn_bar.append(admin_btn)
    conn_root.append(conn_bar)

    conn_scrolled = Gtk.ScrolledWindow()
    conn_scrolled.set_vexpand(True)
    conn_clamp = Adw.Clamp(maximum_size=900)
    conn_clamp.set_margin_start(12)
    conn_clamp.set_margin_end(12)
    conn_clamp.set_margin_bottom(12)
    win._conn_list = Gtk.ListBox()
    win._conn_list.set_selection_mode(Gtk.SelectionMode.NONE)
    win._conn_list.add_css_class("boxed-list")
    conn_clamp.set_child(win._conn_list)
    conn_scrolled.set_child(conn_clamp)
    conn_root.append(conn_scrolled)

    win._network_stack.add_named(adapters_scrolled, "adapters")
    win._network_stack.add_named(wifi_scrolled, "wifi")
    win._network_stack.add_named(conn_root, "conn")
    if win._network_chip not in {"adapters", "wifi", "conn"}:
        win._network_chip = "adapters"
    win._network_stack.set_visible_child_name(win._network_chip)
    root.append(win._network_stack)
    return root


def set_chip(win: Any, key: str) -> None:
    win._network_chip = key
    if hasattr(win, "_network_stack"):
        win._network_stack.set_visible_child_name(key)
    refresh(win, show_spinner=True)


def on_wifi_switch(win: Any, row: Gtk.Widget) -> None:
    if getattr(win, "_wifi_switch_guard", False):
        return
    enabled = row.get_active()
    win._set_busy(True)

    def work() -> None:
        network_ctl.set_wifi_enabled(enabled)

    def done(_result: Any, error: BaseException | None) -> None:
        win._set_busy(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            refresh(win)
            return
        show_toast(win._toast_overlay, i18n.t("wifi_on" if enabled else "wifi_off"))
        refresh(win)

    run_in_thread(work, done)


def on_bt_switch(win: Any, row: Gtk.Widget) -> None:
    if getattr(win, "_bt_switch_guard", False):
        return
    powered = row.get_active()
    win._set_busy(True)

    def work() -> None:
        network_ctl.set_bluetooth_powered(powered)

    def done(_result: Any, error: BaseException | None) -> None:
        win._set_busy(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            refresh(win)
            return
        show_toast(win._toast_overlay, i18n.t("bt_on" if powered else "bt_off"))
        refresh(win)

    run_in_thread(work, done)


def rescan_wifi(win: Any) -> None:
    win._set_busy(True)
    if hasattr(win, "_network_spinner"):
        win._network_spinner.set_visible(True)

    def work() -> dict[str, Any]:
        return network_ctl.wifi_rescan()

    def done(_result: Any, error: BaseException | None) -> None:
        win._set_busy(False)
        if hasattr(win, "_network_spinner"):
            win._network_spinner.set_visible(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
        refresh(win, show_spinner=True)

    run_in_thread(work, done)


def refresh(win: Any, *, show_spinner: bool = False, privileged: bool = False) -> None:
    chip = getattr(win, "_network_chip", "adapters")
    if chip == "conn":
        refresh_connections(win, show_spinner=show_spinner, privileged=privileged)
        return
    if chip == "adapters":
        refresh_adapters(win, show_spinner=show_spinner)
        return
    if show_spinner and hasattr(win, "_network_spinner"):
        win._network_spinner.set_visible(True)

    def work() -> tuple[dict[str, Any], dict[str, Any]]:
        return network_ctl.wifi_status(), network_ctl.bluetooth_status()

    def done(result: Any, error: BaseException | None) -> None:
        if hasattr(win, "_network_spinner"):
            win._network_spinner.set_visible(False)
        if error is not None:
            show_toast(win._toast_overlay, f"Réseau: {error}")
            return
        wifi, bt = result
        win._wifi_switch_guard = True
        win._wifi_switch_row.set_sensitive(bool(wifi.get("available")))
        win._wifi_switch_row.set_active(bool(wifi.get("available") and wifi.get("enabled")))
        if wifi.get("message"):
            wifi_sub = str(wifi.get("message"))
        elif not wifi.get("available"):
            wifi_sub = i18n.t("unavailable")
        elif wifi.get("enabled"):
            wifi_sub = i18n.t("available")
        else:
            wifi_sub = i18n.t("wifi_state_off")
        win._wifi_switch_row.set_subtitle(wifi_sub)
        win._wifi_switch_guard = False

        _clear_listbox(win._wifi_list)
        for conn in wifi.get("connections") or []:
            row = Adw.ActionRow()
            ssid = str(conn.get("ssid") or "")
            title = ssid or i18n.t("hidden_ssid")
            active = f" · {i18n.t('connected')}" if conn.get("active") else ""
            row.set_title(title)
            row.set_subtitle(f"{i18n.t('signal')} {conn.get('signal')}% · {conn.get('security')}{active}")
            if ssid and not conn.get("active"):
                conn_btn = Gtk.Button(label=i18n.t("connect"))
                conn_btn.add_css_class("suggested-action")
                conn_btn.set_valign(Gtk.Align.CENTER)
                conn_btn.connect("clicked", lambda *_a, s=ssid: wifi_connect(win, s))
                row.add_suffix(conn_btn)
            if ssid:
                forget_btn = Gtk.Button(label=i18n.t("forget"))
                forget_btn.set_valign(Gtk.Align.CENTER)
                forget_btn.connect("clicked", lambda *_a, s=ssid: wifi_forget(win, s))
                row.add_suffix(forget_btn)
            win._wifi_list.append(row)
        if not (wifi.get("connections") or []):
            empty = Adw.ActionRow(title=i18n.t("no_network"), subtitle=i18n.t("wifi_scan_hint"))
            win._wifi_list.append(empty)

        win._bt_switch_guard = True
        win._bt_switch_row.set_sensitive(bool(bt.get("available")))
        win._bt_switch_row.set_active(bool(bt.get("powered")))
        bt_msg = bt.get("message") or (i18n.t("available") if bt.get("available") else i18n.t("unavailable"))
        win._bt_switch_row.set_subtitle(str(bt_msg))
        win._bt_switch_guard = False

        _clear_listbox(win._bt_list)
        for dev in bt.get("devices") or []:
            row = Adw.ActionRow()
            row.set_title(str(dev.get("name") or "?"))
            row.set_subtitle(str(dev.get("mac") or ""))
            win._bt_list.append(row)
        if not (bt.get("devices") or []):
            win._bt_list.append(Adw.ActionRow(title=i18n.t("no_device"), subtitle="—"))

    run_in_thread(work, done)


def refresh_adapters(win: Any, *, show_spinner: bool = False) -> None:
    if show_spinner and hasattr(win, "_network_spinner"):
        win._network_spinner.set_visible(True)

    def work() -> adapters.AdapterSnapshot:
        first = adapters.snapshot()
        before = {row.name: (row.rx_bytes, row.tx_bytes) for row in first.adapters}
        time.sleep(0.4)
        return adapters.snapshot(prev_counters=before, elapsed=0.4)

    def done(result: Any, error: BaseException | None) -> None:
        if hasattr(win, "_network_spinner"):
            win._network_spinner.set_visible(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            return
        snap = result if isinstance(result, adapters.AdapterSnapshot) else adapters.AdapterSnapshot([])
        bits = []
        if snap.gateway:
            bits.append(i18n.t("adapters_gateway", gateway=snap.gateway))
            if snap.default_iface:
                bits.append(i18n.t("adapters_via", iface=snap.default_iface))
        if snap.dns:
            bits.append(i18n.t("adapters_dns", servers=", ".join(snap.dns)))
        win._adapters_summary.set_text(" · ".join(bits) if bits else "—")
        _clear_listbox(win._adapters_list)
        rows = [row for row in snap.adapters if not row.name.startswith("veth")]
        if not rows:
            win._adapters_list.append(Adw.ActionRow(title=i18n.t("adapters_empty"), subtitle="—"))
            return
        for nic in rows:
            row = Adw.ActionRow()
            ip = ", ".join(nic.ipv4) or "—"
            row.set_title(f"{nic.name} · {ip}")
            state = i18n.t("adapters_up" if nic.is_up else "adapters_down")
            meta = [state]
            if nic.mac and nic.mac != "00:00:00:00:00:00":
                meta.append(nic.mac)
            meta.append(f"↓ {adapters.format_bytes(nic.rx_bytes)}  ↑ {adapters.format_bytes(nic.tx_bytes)}")
            if nic.rx_bps or nic.tx_bps:
                meta.append(f"↓ {adapters.format_bps(nic.rx_bps)}  ↑ {adapters.format_bps(nic.tx_bps)}")
            if nic.name == snap.default_iface:
                meta.append(i18n.t("adapters_default"))
            row.set_subtitle(" · ".join(meta))
            win._adapters_list.append(row)

    run_in_thread(work, done)


def _conn_kind_label(kind: str) -> str:
    keys = {
        "known": "conn_kind_known",
        "unknown": "conn_kind_unknown",
        "listen": "conn_kind_listen",
    }
    return i18n.t(keys.get(kind, "conn_kind_unknown"))


def refresh_connections(win: Any, *, show_spinner: bool = False, privileged: bool = False) -> None:
    if show_spinner and hasattr(win, "_network_spinner"):
        win._network_spinner.set_visible(True)
    if privileged:
        show_toast(win._toast_overlay, i18n.t("conn_reading_admin"), timeout=4)

    def work() -> dict[str, Any]:
        allowlist = list(win._settings.get("connection_allowlist") or [])
        return connections.list_connections(privileged=privileged, allowlist=allowlist)

    def done(result: Any, error: BaseException | None) -> None:
        if hasattr(win, "_network_spinner"):
            win._network_spinner.set_visible(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            return
        data = result if isinstance(result, dict) else {}
        items = list(data.get("items") or [])
        win._connection_items = items
        render_connections(win, data)

    run_in_thread(work, done)


def render_connections(win: Any, data: dict[str, Any]) -> None:
    if not hasattr(win, "_conn_list"):
        return
    _clear_listbox(win._conn_list)
    available = bool(data.get("available"))
    message = str(data.get("message") or "").strip()
    needs_admin = bool(data.get("needs_elevation"))
    items = list(data.get("items") or [])
    status_bits: list[str] = []
    if not available:
        status_bits.append(message or i18n.t("conn_empty"))
    else:
        status_bits.append(f"{len(items)}")
        if needs_admin:
            status_bits.append(i18n.t("conn_needs_admin"))
        elif message:
            status_bits.append(message)
    win._conn_status.set_text(" · ".join(status_bits) if status_bits else "—")

    if not available:
        win._conn_list.append(Adw.ActionRow(title=i18n.t("conn_chip"), subtitle=message or i18n.t("conn_empty")))
        return
    if not items:
        win._conn_list.append(Adw.ActionRow(title=i18n.t("conn_empty"), subtitle="—"))
        return
    for item in items:
        row = Adw.ActionRow()
        comm = str(item.get("comm") or "?")
        pid = item.get("pid")
        title = f"{comm} · PID {pid}" if pid is not None else f"{comm} · PID —"
        row.set_title(title)
        kind = str(item.get("kind") or "unknown")
        proto = str(item.get("proto") or "")
        state = str(item.get("state") or "")
        local = str(item.get("local") or "")
        remote = str(item.get("remote") or "")
        row.set_subtitle(f"{proto} {state} {local} → {remote} · {_conn_kind_label(kind)}")
        row.set_activatable(True)
        row.connect("activated", lambda *_a, it=item: show_connection_detail(win, it))
        if kind == "unknown":
            mark_btn = Gtk.Button(label=i18n.t("conn_mark_known"))
            mark_btn.set_valign(Gtk.Align.CENTER)
            mark_btn.connect("clicked", lambda *_a, it=item: mark_connection_known(win, it))
            row.add_suffix(mark_btn)
        win._conn_list.append(row)


def show_connection_detail(win: Any, item: dict[str, Any]) -> None:
    raw = str(item.get("raw") or "").strip() or "—"
    remote = str(item.get("remote") or "")
    body = (
        f"{item.get('comm') or '?'}  PID {item.get('pid') if item.get('pid') is not None else '—'}\n"
        f"{item.get('proto') or ''} {item.get('state') or ''}\n"
        f"{item.get('local') or ''} → {remote}\n"
        f"{_conn_kind_label(str(item.get('kind') or ''))}\n\n"
        f"{raw}"
    )
    dialog = make_message_dialog(win, i18n.t("conn_detail"), body)
    dialog.add_response("close", i18n.t("cancel"))
    dialog.add_response("copy", i18n.t("conn_copy"))

    def on_response(_d: object, response: str) -> None:
        if response == "copy":
            copy_connection_dest(win, remote)

    dialog.connect("response", on_response)
    dialog.present(win)


def copy_connection_dest(win: Any, remote: str) -> None:
    display = Gdk.Display.get_default() if hasattr(Gdk, "Display") else None
    getter = getattr(display, "get_clipboard", None) if display is not None else None
    clipboard = getter() if callable(getter) else None
    setter = getattr(clipboard, "set", None)
    if not callable(setter):
        show_toast(win._toast_overlay, i18n.t("conn_no_clipboard"))
        return
    setter(remote)
    show_toast(win._toast_overlay, i18n.t("conn_copied"))


def export_connections(win: Any) -> None:
    items = list(getattr(win, "_connection_items", []) or [])
    if not items:
        show_toast(win._toast_overlay, i18n.t("conn_no_export"))
        return
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = Path.home() / "Documents" / f"hub-reseau-connexions-{stamp}.csv"

    def work() -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(connections.to_csv(items), encoding="utf-8")
        return path

    def done(result: Any, error: BaseException | None) -> None:
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            return
        show_toast(win._toast_overlay, i18n.t("conn_exported", path=str(result)))

    run_in_thread(work, done)


def mark_connection_known(win: Any, item: dict[str, Any]) -> None:
    ip_text = connections.endpoint_ip(str(item.get("remote") or ""))
    try:
        updated = connections.add_allowlist_entry(
            ip_text,
            list(win._settings.get("connection_allowlist") or []),
        )
    except connections.ConnectionError as exc:
        show_toast(win._toast_overlay, i18n.t("conn_allow_failed", detail=str(exc)))
        return
    win._settings["connection_allowlist"] = updated
    app_settings.save_settings(win._settings)
    show_toast(win._toast_overlay, i18n.t("conn_marked", ip=ip_text))
    refresh_connections(win, show_spinner=True)


def open_allowlist_dialog(win: Any) -> None:
    entry = Gtk.Entry()
    set_placeholder_text(entry, i18n.t("conn_allowlist_hint"))
    current = ", ".join(list(win._settings.get("connection_allowlist") or []))
    body = current or "—"
    dialog = make_message_dialog(win, i18n.t("conn_allowlist_title"), body, extra_child=entry)
    dialog.add_response("cancel", i18n.t("cancel"))
    dialog.add_response("add", i18n.t("save"))
    dialog.set_default_response("add")

    def on_response(_d: object, response: str) -> None:
        if response != "add":
            return
        try:
            updated = connections.add_allowlist_entry(
                entry.get_text(),
                list(win._settings.get("connection_allowlist") or []),
            )
        except connections.ConnectionError as exc:
            show_toast(win._toast_overlay, i18n.t("conn_allow_failed", detail=str(exc)))
            return
        win._settings["connection_allowlist"] = updated
        app_settings.save_settings(win._settings)
        show_toast(win._toast_overlay, i18n.t("conn_marked", ip=entry.get_text().strip()))
        refresh_connections(win, show_spinner=True)

    dialog.connect("response", on_response)
    dialog.present(win)


def wifi_connect(win: Any, ssid: str) -> None:
    entry = Gtk.PasswordEntry()
    call_if = getattr(entry, "set_show_peek_icon", None)
    if callable(call_if):
        call_if(True)
    set_placeholder_text(entry, i18n.t("wifi_password"))
    dialog = make_message_dialog(win, i18n.t("connect"), ssid, extra_child=entry)
    dialog.add_response("cancel", i18n.t("cancel"))
    dialog.add_response("ok", i18n.t("connect"))
    dialog.set_response_appearance("ok", response_appearance("SUGGESTED"))

    def on_response(_d: object, response: str) -> None:
        if response != "ok":
            return
        password = entry.get_text() or None
        win._set_busy(True)

        def work() -> None:
            network_ctl.wifi_connect(ssid, password)

        def done(_r: Any, error: BaseException | None) -> None:
            win._set_busy(False)
            if error is not None:
                show_toast(win._toast_overlay, str(error), timeout=8)
                return
            show_toast(win._toast_overlay, f"{i18n.t('connect')}: {ssid}")
            refresh(win, show_spinner=True)

        run_in_thread(work, done)

    dialog.connect("response", on_response)
    dialog.present(win)


def wifi_forget(win: Any, ssid: str) -> None:
    confirm_dialog(
        win,
        i18n.t("forget"),
        ssid,
        confirm_label=i18n.t("forget"),
        destructive=True,
        on_confirm=lambda: do_wifi_forget(win, ssid),
    )


def do_wifi_forget(win: Any, ssid: str) -> None:
    win._set_busy(True)

    def work() -> None:
        network_ctl.wifi_forget(ssid)

    def done(_r: Any, error: BaseException | None) -> None:
        win._set_busy(False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            return
        show_toast(win._toast_overlay, f"{i18n.t('forget')}: {ssid}")
        refresh(win, show_spinner=True)

    run_in_thread(work, done)
