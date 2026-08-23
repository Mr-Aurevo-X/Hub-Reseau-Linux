# SPDX-License-Identifier: GPL-3.0-or-later
"""Home dashboard — live network cards, no Gest metrics."""

from __future__ import annotations

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk  # noqa: E402

from core import home_summary, i18n


def build(win: Any) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    box.set_margin_top(24)
    box.set_margin_start(24)
    box.set_margin_end(24)
    title = Gtk.Label(label=i18n.t("hub_home_title"), xalign=0)
    title.add_css_class("title-1")
    lede = Gtk.Label(label=i18n.t("hub_home_reseau"), wrap=True, xalign=0)
    lede.add_css_class("dim-label")
    box.append(title)
    box.append(lede)
    listbox = Gtk.ListBox()
    listbox.add_css_class("boxed-list")
    win._home_summary_list = listbox

    def reload_home() -> None:
        while (row := listbox.get_row_at_index(0)) is not None:
            listbox.remove(row)
        dash = home_summary.dashboard()
        for card in dash.cards:
            if card.key == "host":
                row = Adw.ActionRow()
                row.set_title(card.title)
                row.set_subtitle(card.body)
                listbox.append(row)
                continue
            row = Adw.ActionRow()
            row.set_title(card.title)
            row.set_subtitle(card.body)
            listbox.append(row)

    reload_home()
    win._refresh_home = reload_home
    box.append(listbox)
    actions = Gtk.Box(spacing=8)
    for key, label_key in (
        ("network", "network"),
        ("fleet", "fleet"),
        ("lan_scan", "lan_scan"),
        ("network_diag", "network_diag"),
    ):
        btn = Gtk.Button(label=i18n.t(label_key))
        btn.connect("clicked", lambda *_a, k=key: win._show_page(k))
        actions.append(btn)
    box.append(actions)
    return box


def refresh(win: Any) -> None:
    reload = getattr(win, "_refresh_home", None)
    if callable(reload):
        reload()
