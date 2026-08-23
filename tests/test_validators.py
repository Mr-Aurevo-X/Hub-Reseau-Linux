# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from core import i18n


def test_i18n_key_parity() -> None:
    fr = set(i18n._STRINGS["fr"])
    en = set(i18n._STRINGS["en"])
    assert fr == en, f"missing in en: {fr - en}; missing in fr: {en - fr}"


def test_i18n_t_format() -> None:
    i18n.set_language("fr")
    text = i18n.t("update_up_to_date", version="1.2.3")
    assert "1.2.3" in text
    i18n.set_language("en")
    text = i18n.t("update_up_to_date", version="1.2.3")
    assert "1.2.3" in text
