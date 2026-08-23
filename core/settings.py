# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistent hub settings."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from core.paths import settings_path

DEFAULTS: dict[str, Any] = {
    "language": "fr",
    "language_chosen": False,
    "auto_update_on_startup": True,
    "connection_allowlist": [],
    "nav_groups_expanded": {},
}


def coerce_language(value: object) -> str:
    raw = str(value or "fr").strip().lower().replace("_", "-")
    code = raw.split("-", 1)[0]
    return code if code in {"fr", "en"} else "fr"


def needs_language_prompt(settings: dict[str, Any] | None = None) -> bool:
    if settings is None:
        return True
    return not bool(settings.get("language_chosen"))


def load_settings() -> dict[str, Any]:
    path = settings_path()
    data = deepcopy(DEFAULTS)
    raw: dict[str, Any] | None = None
    if path.exists():
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                raw = parsed
                data.update({k: v for k, v in parsed.items() if k in DEFAULTS})
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    data["language"] = coerce_language(data.get("language"))
    if raw is None:
        data["language_chosen"] = False
    else:
        data["language_chosen"] = bool(raw.get("language_chosen", False))
    if not isinstance(data.get("connection_allowlist"), list):
        data["connection_allowlist"] = []
    if not isinstance(data.get("nav_groups_expanded"), dict):
        data["nav_groups_expanded"] = {}
    return data


def save_settings(settings: dict[str, Any]) -> None:
    merged = deepcopy(DEFAULTS)
    merged.update({k: v for k, v in settings.items() if k in DEFAULTS})
    merged["language"] = coerce_language(merged.get("language"))
    merged["language_chosen"] = bool(merged.get("language_chosen"))
    if not isinstance(merged.get("nav_groups_expanded"), dict):
        merged["nav_groups_expanded"] = {}
    if not isinstance(merged.get("connection_allowlist"), list):
        merged["connection_allowlist"] = []
    path = settings_path()
    path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
