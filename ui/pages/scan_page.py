# SPDX-License-Identifier: GPL-3.0-or-later
"""LAN scan page — private subnet discovery, no auto-run."""

from __future__ import annotations

import threading
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk  # noqa: E402

from core import fleet, i18n, lan_scan
from ui.components import run_in_thread, show_toast


def build(win: Any) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_top(16)
    box.set_margin_start(16)
    box.set_margin_end(16)
    title = Gtk.Label(label=i18n.t("lan_scan"), xalign=0)
    title.add_css_class("title-1")
    hint = Gtk.Label(label=i18n.t("lan_scan_hint"), xalign=0, wrap=True)
    hint.add_css_class("dim-label")
    win._lan_scan_subnet = Gtk.Label(label="—", xalign=0, wrap=True)
    bar = Gtk.Box(spacing=8)
    win._lan_scan_start = Gtk.Button(label=i18n.t("lan_scan_start"))
    win._lan_scan_start.add_css_class("suggested-action")
    win._lan_scan_cancel = Gtk.Button(label=i18n.t("lan_scan_cancel"))
    win._lan_scan_cancel.set_sensitive(False)
    add_btn = Gtk.Button(label=i18n.t("lan_scan_add_fleet"))
    export_btn = Gtk.Button(label=i18n.t("export"))
    bar.append(win._lan_scan_start)
    bar.append(win._lan_scan_cancel)
    bar.append(add_btn)
    bar.append(export_btn)
    win._lan_scan_progress = Gtk.ProgressBar()
    win._lan_scan_progress.set_show_text(True)
    win._lan_scan_status = Gtk.Label(label=i18n.t("lan_scan_empty"), xalign=0, wrap=True)
    win._lan_scan_list = Gtk.ListBox()
    win._lan_scan_list.add_css_class("boxed-list")
    win._lan_scan_list.set_selection_mode(Gtk.SelectionMode.NONE)
    scroll = Gtk.ScrolledWindow(vexpand=True)
    scroll.set_child(win._lan_scan_list)

    win._lan_scan_hosts = []
    win._lan_scan_selected: set[str] = set()
    win._lan_scan_running = False
    win._lan_scan_cancel_event = threading.Event()
    win._lan_scan_checks: dict[str, Gtk.CheckButton] = {}

    win._lan_scan_start.connect("clicked", lambda *_: start_scan(win))
    win._lan_scan_cancel.connect("clicked", lambda *_: cancel_scan(win))
    add_btn.connect("clicked", lambda *_: add_selected(win))
    export_btn.connect("clicked", lambda *_: export_csv(win))

    box.append(title)
    box.append(hint)
    box.append(win._lan_scan_subnet)
    box.append(bar)
    box.append(win._lan_scan_progress)
    box.append(win._lan_scan_status)
    box.append(scroll)
    _refresh_subnet_label(win)
    render(win)
    return box


def _refresh_subnet_label(win: Any) -> None:
    targets = lan_scan.local_targets()
    if not targets:
        win._lan_scan_subnet.set_text(i18n.t("lan_scan_no_target"))
        return
    first = targets[0]
    win._lan_scan_subnet.set_text(
        i18n.t("lan_scan_subnet", iface=first.iface or "—", network=first.network)
    )


def _clear_list(listbox: Gtk.ListBox) -> None:
    while (row := listbox.get_row_at_index(0)) is not None:
        listbox.remove(row)


def render(win: Any) -> None:
    _clear_list(win._lan_scan_list)
    win._lan_scan_checks = {}
    hosts: list[lan_scan.ScanHost] = list(getattr(win, "_lan_scan_hosts", []) or [])
    if not hosts:
        empty = Gtk.ListBoxRow()
        empty.set_child(Gtk.Label(label=i18n.t("lan_scan_empty"), xalign=0, wrap=True))
        win._lan_scan_list.append(empty)
        return
    selected = getattr(win, "_lan_scan_selected", set())
    for host_row in hosts:
        row = Adw.ActionRow()
        title = host_row.ip
        if host_row.is_self:
            title = f"{host_row.ip} ({i18n.t('lan_scan_self')})"
        row.set_title(title)
        bits = [host_row.name] if host_row.name else []
        if host_row.rtt_ms is not None:
            bits.append(f"{host_row.rtt_ms:.1f} ms")
        if host_row.ports:
            bits.append(",".join(str(p) for p in host_row.ports))
        if host_row.sources:
            bits.append("+".join(host_row.sources))
        row.set_subtitle(" · ".join(bits) or "—")
        check = Gtk.CheckButton()
        check.set_sensitive(not host_row.is_self)
        check.set_active(host_row.ip in selected and not host_row.is_self)
        check.connect("toggled", lambda btn, ip=host_row.ip: _toggle(win, ip, btn.get_active()))
        row.add_prefix(check)
        win._lan_scan_checks[host_row.ip] = check
        win._lan_scan_list.append(row)


def _toggle(win: Any, ip: str, active: bool) -> None:
    selected = getattr(win, "_lan_scan_selected", set())
    if active:
        selected.add(ip)
    else:
        selected.discard(ip)
    win._lan_scan_selected = selected


def _set_running(win: Any, running: bool) -> None:
    win._lan_scan_running = running
    if hasattr(win, "_lan_scan_start"):
        win._lan_scan_start.set_sensitive(not running)
    if hasattr(win, "_lan_scan_cancel"):
        win._lan_scan_cancel.set_sensitive(running)
    setter = getattr(win, "_set_busy", None)
    if callable(setter):
        setter(running)


def start_scan(win: Any) -> None:
    if getattr(win, "_lan_scan_running", False):
        return
    _refresh_subnet_label(win)
    win._lan_scan_cancel_event = threading.Event()
    win._lan_scan_selected = set()
    win._lan_scan_progress.set_fraction(0)
    win._lan_scan_status.set_text(i18n.t("lan_scan_running"))
    _set_running(win, True)

    cancel = win._lan_scan_cancel_event

    def on_progress(done: int, total: int) -> None:
        frac = 0.0 if total <= 0 else min(done / total, 1.0)

        def tick() -> bool:
            win._lan_scan_progress.set_fraction(frac)
            win._lan_scan_progress.set_text(f"{done}/{total}")
            return False

        GLib.idle_add(tick)

    def work() -> list[lan_scan.ScanHost]:
        return lan_scan.run_scan(cancel=cancel, on_progress=on_progress)

    def done(result: Any, error: BaseException | None) -> None:
        _set_running(win, False)
        if error is not None:
            show_toast(win._toast_overlay, str(error))
            win._lan_scan_status.set_text(str(error))
            return
        hosts = list(result or [])
        win._lan_scan_hosts = hosts
        win._lan_scan_progress.set_fraction(1.0)
        win._lan_scan_status.set_text(i18n.t("lan_scan_done", count=len(hosts)))
        render(win)

    run_in_thread(work, done)


def cancel_scan(win: Any) -> None:
    event = getattr(win, "_lan_scan_cancel_event", None)
    if event is not None:
        event.set()


def refresh(win: Any) -> None:
    if getattr(win, "_lan_scan_running", False):
        render(win)
        return
    start_scan(win)


def add_selected(win: Any) -> None:
    selected = set(getattr(win, "_lan_scan_selected", set()) or [])
    hosts = [h for h in getattr(win, "_lan_scan_hosts", []) if h.ip in selected and not h.is_self]
    if not hosts:
        show_toast(win._toast_overlay, i18n.t("lan_scan_none_selected"))
        return
    store = getattr(win, "_fleet_store", None)
    if not isinstance(store, dict):
        store = fleet.load_fleet()
    existing = {str(item.get("address") or "") for item in store.get("machines") or []}
    added = 0
    for host_row in hosts:
        if host_row.ip in existing:
            continue
        probe = "icmp"
        if 22 in host_row.ports:
            probe = "tcp:22"
        elif 3389 in host_row.ports:
            probe = "tcp:3389"
        elif 445 in host_row.ports:
            probe = "tcp:445"
        try:
            machine = fleet.new_machine(
                name=host_row.name or host_row.ip,
                os_name="—",
                address=host_row.ip,
                probe=probe,
                tags=["scan"],
            )
            store = fleet.upsert_machine(store, machine)
            existing.add(host_row.ip)
            added += 1
        except fleet.FleetError as exc:
            show_toast(win._toast_overlay, str(exc))
            if "limité" in str(exc) or "limit" in str(exc).lower():
                show_toast(win._toast_overlay, i18n.t("lan_scan_fleet_full", max=fleet.MAX_MACHINES))
            break
    win._fleet_store = store
    try:
        fleet.save_fleet(store)
    except OSError as exc:
        show_toast(win._toast_overlay, str(exc))
        return
    if added:
        show_toast(win._toast_overlay, i18n.t("lan_scan_added", added=added))
    elif not added:
        show_toast(win._toast_overlay, i18n.t("lan_scan_none_selected"))
    if hasattr(win, "_fleet_explorer"):
        from ui.pages import fleet as fleet_page

        fleet_page.render(win)


def export_csv(win: Any) -> None:
    hosts = list(getattr(win, "_lan_scan_hosts", []) or [])
    if not hosts:
        show_toast(win._toast_overlay, i18n.t("lan_scan_empty"))
        return
    try:
        path = lan_scan.write_export(hosts)
    except OSError as exc:
        show_toast(win._toast_overlay, str(exc))
        return
    show_toast(win._toast_overlay, i18n.t("lan_scan_exported", path=str(path)))
