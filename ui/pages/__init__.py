# SPDX-License-Identifier: GPL-3.0-or-later
"""Lazy page registry — builders live on MainWindow; pages load on first visit."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

PAGE_KEYS: tuple[str, ...] = (
    "home",
    "network",
    "fleet",
    "network_diag",
    "vpn",
)

_BUILD_ATTR = {
    "home": "_build_home_page",
    "network": "_build_network_page",
    "fleet": "_build_fleet",
    "network_diag": "_build_network_diag_page",
    "vpn": "_build_vpn_page",
}


def builders_for(win: Any) -> dict[str, Callable[[], Any]]:
    """Return page key → zero-arg builder bound to ``win``."""
    out: dict[str, Callable[[], Any]] = {}
    for key, attr in _BUILD_ATTR.items():
        method = getattr(win, attr)
        out[key] = method
    return out
