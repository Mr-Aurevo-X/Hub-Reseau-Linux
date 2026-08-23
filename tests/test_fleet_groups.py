# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from core import fleet


def test_machines_grouped_by_location_then_subnet() -> None:
    lan = fleet.new_machine(name="NAS", os_name="Linux", address="192.168.1.10", location="Atelier")
    same = fleet.new_machine(name="Pi", os_name="Linux", address="192.168.1.20", location="Atelier")
    other = fleet.new_machine(name="Box", os_name="Linux", address="10.0.0.2")
    host = fleet.new_machine(name="Host", os_name="Linux", address="hub.lan")
    groups = fleet.machines_grouped([lan, same, other, host])
    labels = [label for label, _rows in groups]
    assert labels[0] == "Atelier"
    assert {m["name"] for m in groups[0][1]} == {"NAS", "Pi"}
    assert "10.0.0.0/24" in labels
    assert "" in labels or any(label.startswith("hub") for label in labels)
