# SPDX-License-Identifier: GPL-3.0-or-later
"""Home dashboard — clickable network cards, collected off the GTK thread."""

from __future__ import annotations

from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk  # noqa: E402

from core import home_summary, i18n
from ui.components import run_in_thread, show_toast


def _clear_box(box: Gtk.Box) -> None:
    child = box.get_first_child()
    while child is not None:
        nxt = child.get_next_sibling()
        box.remove(child)
        child = nxt


def _open_card(win: Any, key: str) -> None:
    target = home_summary.card_target(key)
    if target is None:
        return
    page, chip = target
    if chip:
        win._network_chip = chip
        stack = getattr(win, "_network_stack", None)
        setter = getattr(stack, "set_visible_child_name", None)
        if callable(setter):
            try:
                setter(chip)
            except Exception:  # noqa: BLE001 — stack may not have the child yet
                pass
    win._show_page(page)


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
    cards = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    win._home_cards_box = cards
    box.append(cards)
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
    refresh(win)
    return box


def _render(win: Any, dash: home_summary.HomeDashboard) -> None:
    box = getattr(win, "_home_cards_box", None)
    if box is None:
        return
    _clear_box(box)
    for card in dash.cards:
        group = Adw.PreferencesGroup()
        group.set_title(card.title)
        row = Adw.ActionRow()
        row.set_title(card.body or "—")
        if card.detail:
            row.set_subtitle(card.detail)
        target = home_summary.card_target(card.key)
        if target is not None:
            row.set_activatable(True)
            row.connect("activated", lambda *_a, k=card.key: _open_card(win, k))
        group.add(row)
        box.append(group)


def refresh(win: Any) -> None:
    setter = getattr(win, "_set_busy", None)
    if callable(setter):
        setter(True)

    def work() -> home_summary.HomeDashboard:
        return home_summary.dashboard()

    def done(result: Any, error: BaseException | None) -> None:
        if callable(setter):
            setter(False)
        if error is not None:
            overlay = getattr(win, "_toast_overlay", None)
            if overlay is not None:
                show_toast(overlay, str(error))
            return
        if isinstance(result, home_summary.HomeDashboard):
            _render(win, result)

    run_in_thread(work, done)
