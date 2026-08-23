# SPDX-License-Identifier: GPL-3.0-or-later
"""Network diagnostic page — run on demand, never on load."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, Gtk  # noqa: E402

from core import i18n, network_diag
from ui.components import run_in_thread, show_toast


def build(win: Any) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_top(16)
    box.set_margin_start(16)
    box.set_margin_end(16)
    title = Gtk.Label(label=i18n.t("network_diag"), xalign=0)
    title.add_css_class("title-1")
    host_row = Gtk.Box(spacing=8)
    host_entry = Gtk.Entry(placeholder_text="1.1.1.1")
    host_entry.set_text("1.1.1.1")
    host_entry.set_hexpand(True)
    run_btn = Gtk.Button(label=i18n.t("diag_run"))
    run_btn.add_css_class("suggested-action")
    export_btn = Gtk.Button(label=i18n.t("export"))
    host_row.append(host_entry)
    host_row.append(run_btn)
    host_row.append(export_btn)
    status = Gtk.Label(label=i18n.t("diag_idle"), xalign=0, wrap=True)
    status.add_css_class("dim-label")
    listbox = Gtk.ListBox()
    listbox.add_css_class("boxed-list")
    win._diag_entry = host_entry
    win._diag_status = status
    win._diag_list = listbox

    def fill_lines(lines: list[str]) -> None:
        while (row := listbox.get_row_at_index(0)) is not None:
            listbox.remove(row)
        for line in lines:
            row = Gtk.ListBoxRow()
            row.set_child(Gtk.Label(label=line, xalign=0, wrap=True))
            listbox.append(row)

    def reload() -> None:
        target = host_entry.get_text().strip() or "1.1.1.1"
        status.set_text(i18n.t("diag_running"))
        setter = getattr(win, "_set_busy", None)
        if callable(setter):
            setter(True)

        def work() -> list[str]:
            return network_diag.quick_report(target)

        def done(result: Any, error: BaseException | None) -> None:
            if callable(setter):
                setter(False)
            if error is not None:
                status.set_text(str(error))
                show_toast(win._toast_overlay, str(error))
                return
            status.set_text("")
            fill_lines(list(result or []))

        run_in_thread(work, done)

    def export_report() -> None:
        target = host_entry.get_text().strip() or "1.1.1.1"
        setter = getattr(win, "_set_busy", None)
        if callable(setter):
            setter(True)

        def work() -> tuple[str, Path]:
            text = network_diag.export_report(target)
            path = network_diag.write_export(target, text=text)
            return text, path

        def done(result: Any, error: BaseException | None) -> None:
            if callable(setter):
                setter(False)
            if error is not None:
                show_toast(win._toast_overlay, str(error))
                return
            text, path = result
            display = Gdk.Display.get_default() if hasattr(Gdk, "Display") else None
            getter = getattr(display, "get_clipboard", None) if display is not None else None
            clipboard = getter() if callable(getter) else None
            setter_clip = getattr(clipboard, "set", None)
            if callable(setter_clip):
                setter_clip(text)
                show_toast(win._toast_overlay, i18n.t("diag_copied"))
            show_toast(win._toast_overlay, i18n.t("diag_exported", path=str(path)))

        run_in_thread(work, done)

    run_btn.connect("clicked", lambda *_: reload())
    export_btn.connect("clicked", lambda *_: export_report())
    win._network_diag_reload = reload
    box.append(title)
    box.append(host_row)
    box.append(status)
    box.append(Gtk.ScrolledWindow(vexpand=True, child=listbox))
    return box


def refresh(win: Any) -> None:
    reload = getattr(win, "_network_diag_reload", None)
    if callable(reload):
        reload()
