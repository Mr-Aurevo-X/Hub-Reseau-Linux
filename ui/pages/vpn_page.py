# SPDX-License-Identifier: GPL-3.0-or-later
"""VPN / proxy placeholder — local system read later."""

from __future__ import annotations

from typing import Any

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402

from core import i18n


def build(win: Any) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_top(16)
    box.set_margin_start(16)
    box.set_margin_end(16)
    title = Gtk.Label(label=i18n.t("vpn"), xalign=0)
    title.add_css_class("title-1")
    hint = Gtk.Label(label=i18n.t("vpn_hint"), xalign=0, wrap=True)
    hint.set_wrap(True)
    box.append(title)
    box.append(hint)
    return box
