# SPDX-License-Identifier: GPL-3.0-or-later
"""Fleet page — manual workshop machines + TCP/ICMP probe."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, GLib, Gtk  # noqa: E402

from core import fleet, i18n
from ui.adw_compat import make_message_dialog, set_placeholder_text
from ui.components import confirm_dialog, run_in_thread, show_toast

_CSS = b"""
.fleet-tile {
  min-width: 128px;
  max-width: 168px;
  padding: 10px 8px;
  border-radius: 12px;
}
.fleet-tile:hover {
  background-color: alpha(currentColor, 0.08);
}
.fleet-tile.online {
  background-color: alpha(#6ee7a8, 0.12);
}
.fleet-root-header {
  margin-top: 8px;
  margin-bottom: 4px;
}
.fleet-tile-name {
  font-weight: 600;
}
.fleet-tile-meta {
  opacity: 0.75;
  font-size: 0.85em;
}
"""


def _ensure_css() -> None:
    display = Gdk.Display.get_default()
    if display is None:
        return
    provider = Gtk.CssProvider()
    provider.load_from_data(_CSS)
    Gtk.StyleContext.add_provider_for_display(
        display,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

_PROBE_IDS = ("tcp:22", "tcp:3389", "tcp:445", "icmp")
_PROBE_KEYS = (
    "fleet_probe_tcp22",
    "fleet_probe_tcp3389",
    "fleet_probe_tcp445",
    "fleet_probe_icmp",
)


def _status_label(machine: dict[str, Any]) -> str:
    online = machine.get("last_online")
    if online is True:
        return i18n.t("fleet_online")
    if online is False:
        return i18n.t("fleet_offline")
    return i18n.t("fleet_unknown")


def build(win: Any) -> Gtk.Widget:
    _ensure_css()
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    bar.add_css_class("page-toolbar")
    win._fleet_spinner = Gtk.Spinner()
    win._fleet_spinner.set_visible(False)
    add_btn = Gtk.Button(label=i18n.t("fleet_add"))
    add_btn.add_css_class("suggested-action")
    add_btn.connect("clicked", lambda *_: open_editor(win))
    edit_btn = Gtk.Button(label=i18n.t("fleet_edit"))
    edit_btn.connect("clicked", lambda *_: edit_selected(win))
    del_btn = Gtk.Button(label=i18n.t("fleet_delete"))
    del_btn.add_css_class("destructive-action")
    del_btn.connect("clicked", lambda *_: delete_selected(win))
    ping_btn = Gtk.Button(label=i18n.t("fleet_ping"))
    ping_btn.connect("clicked", lambda *_: ping_selected(win))
    ping_all_btn = Gtk.Button(label=i18n.t("fleet_ping_all"))
    ping_all_btn.connect("clicked", lambda *_: ping_all(win))
    export_btn = Gtk.Button(label=i18n.t("fleet_export"))
    export_btn.connect("clicked", lambda *_: export_csv(win))
    export_json_btn = Gtk.Button(label=i18n.t("fleet_export_json"))
    export_json_btn.connect("clicked", lambda *_: export_json(win))
    import_btn = Gtk.Button(label=i18n.t("fleet_import"))
    import_btn.connect("clicked", lambda *_: import_json(win))
    for widget in (
        add_btn,
        edit_btn,
        del_btn,
        ping_btn,
        ping_all_btn,
        export_btn,
        export_json_btn,
        import_btn,
        win._fleet_spinner,
    ):
        bar.append(widget)
    root.append(bar)

    win._fleet_explorer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    clamp = Adw.Clamp(maximum_size=1100)
    clamp.set_margin_start(12)
    clamp.set_margin_end(12)
    clamp.set_margin_bottom(16)
    clamp.set_child(win._fleet_explorer)
    scroll.set_child(clamp)
    root.append(scroll)
    if not hasattr(win, "_fleet_store") or not isinstance(getattr(win, "_fleet_store", None), dict):
        win._fleet_store = fleet.load_fleet()
    win._fleet_selected_id = ""
    render(win)
    return root


def _clear_box(box: Gtk.Box) -> None:
    child = box.get_first_child()
    while child is not None:
        nxt = child.get_next_sibling()
        box.remove(child)
        child = nxt


def _on_tile_selected(win: Any, flow: Gtk.FlowBox) -> None:
    children = flow.get_selected_children()
    if not children:
        return
    widget = children[0].get_child()
    if widget is None:
        return
    win._fleet_selected_id = str(widget.get_name() or "")


def _on_tile_activated(win: Any, _flow: Gtk.FlowBox, child: Gtk.FlowBoxChild) -> None:
    widget = child.get_child()
    if widget is None:
        return
    win._fleet_selected_id = str(widget.get_name() or "")
    ping_selected(win)


def _selected(win: Any) -> dict[str, Any] | None:
    mid = str(getattr(win, "_fleet_selected_id", "") or "")
    for item in (win._fleet_store.get("machines") or []):
        if item.get("id") == mid:
            return item
    return None


def persist(win: Any) -> None:
    fleet.save_fleet(win._fleet_store)


def _make_machine_tile(item: dict[str, Any]) -> Gtk.Widget:
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
    box.add_css_class("fleet-tile")
    if item.get("last_online") is True:
        box.add_css_class("online")
    icon = Gtk.Image.new_from_icon_name("network-server-symbolic")
    icon.set_pixel_size(40)
    icon.set_halign(Gtk.Align.CENTER)
    name = Gtk.Label(label=str(item.get("name") or "?"), wrap=True, justify=Gtk.Justification.CENTER)
    name.add_css_class("fleet-tile-name")
    name.set_max_width_chars(16)
    meta = Gtk.Label(
        label=f"{item.get('os') or '—'} · {item.get('address') or '—'} · {_status_label(item)}",
        wrap=True,
        justify=Gtk.Justification.CENTER,
    )
    meta.add_css_class("fleet-tile-meta")
    box.append(icon)
    box.append(name)
    box.append(meta)
    box.set_name(str(item.get("id") or ""))
    return box


def render(win: Any) -> None:
    selected = str(getattr(win, "_fleet_selected_id", "") or "")
    _clear_box(win._fleet_explorer)
    machines = list(win._fleet_store.get("machines") or [])
    if not machines:
        empty = Gtk.Label(label=i18n.t("fleet_empty"), xalign=0, wrap=True)
        empty.add_css_class("dim-label")
        win._fleet_explorer.append(empty)
        return
    restore_flow = None
    restore_child = None
    for label, rows in fleet.machines_grouped(machines):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.add_css_class("fleet-root-header")
        icon = Gtk.Image.new_from_icon_name("network-workgroup-symbolic")
        icon.set_pixel_size(18)
        title = Gtk.Label(label=label or i18n.t("fleet_ungrouped"), xalign=0, hexpand=True)
        title.add_css_class("heading")
        header.append(icon)
        header.append(title)
        win._fleet_explorer.append(header)
        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.SINGLE)
        flow.set_min_children_per_line(2)
        flow.set_max_children_per_line(8)
        flow.set_homogeneous(True)
        flow.connect("selected-children-changed", lambda fb, w=win: _on_tile_selected(w, fb))
        flow.connect("child-activated", lambda fb, child, w=win: _on_tile_activated(w, fb, child))
        for item in rows:
            tile = _make_machine_tile(item)
            flow.append(tile)
            if item.get("id") == selected:
                restore_flow = flow
                restore_child = tile
        win._fleet_explorer.append(flow)
    if restore_flow is not None and restore_child is not None:
        child = restore_flow.get_first_child()
        while child is not None:
            if child.get_child() is restore_child:
                restore_flow.select_child(child)
                break
            child = child.get_next_sibling()


def refresh(win: Any, *, show_spinner: bool = False) -> None:
    win._fleet_store = fleet.load_fleet()
    render(win)


def _entry(placeholder: str, text: str = "") -> Gtk.Entry:
    entry = Gtk.Entry()
    entry.set_text(text)
    set_placeholder_text(entry, placeholder)
    entry.set_hexpand(True)
    return entry


def open_editor(win: Any, machine: dict[str, Any] | None = None) -> None:
    form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    name_e = _entry(i18n.t("fleet_name"), str((machine or {}).get("name") or ""))
    os_e = _entry(i18n.t("fleet_os"), str((machine or {}).get("os") or ""))
    addr_e = _entry(i18n.t("fleet_address"), str((machine or {}).get("address") or ""))
    note_e = _entry(i18n.t("fleet_note"), str((machine or {}).get("note") or ""))
    loc_e = _entry(i18n.t("fleet_location"), str((machine or {}).get("location") or ""))
    tags_raw = (machine or {}).get("tags") or []
    tags_e = _entry(
        i18n.t("fleet_tags"),
        ", ".join(str(t) for t in tags_raw) if isinstance(tags_raw, list) else "",
    )
    probe = Gtk.ComboBoxText()
    current = str((machine or {}).get("probe") or "tcp:22")
    selected = 0
    for idx, (pid, key) in enumerate(zip(_PROBE_IDS, _PROBE_KEYS)):
        probe.append(pid, i18n.t(key))
        if pid == current:
            selected = idx
    probe.set_active(selected)
    for label, widget in (
        (i18n.t("fleet_name"), name_e),
        (i18n.t("fleet_os"), os_e),
        (i18n.t("fleet_address"), addr_e),
        (i18n.t("fleet_probe"), probe),
        (i18n.t("fleet_note"), note_e),
        (i18n.t("fleet_location"), loc_e),
        (i18n.t("fleet_tags"), tags_e),
    ):
        lbl = Gtk.Label(label=label, xalign=0)
        lbl.add_css_class("caption")
        form.append(lbl)
        form.append(widget)
    heading = i18n.t("fleet_editor_edit") if machine else i18n.t("fleet_editor_add")
    dialog = make_message_dialog(win, heading, "", extra_child=form)
    dialog.add_response("cancel", i18n.t("cancel"))
    dialog.add_response("confirm", i18n.t("save"))
    dialog.set_default_response("confirm")
    dialog.set_close_response("cancel")

    def on_response(_dialog: object, response: str) -> None:
        if response != "confirm":
            return
        try:
            row = fleet.new_machine(
                name=name_e.get_text(),
                os_name=os_e.get_text(),
                address=addr_e.get_text(),
                probe=probe.get_active_id() or "tcp:22",
                note=note_e.get_text(),
                location=loc_e.get_text(),
                tags=tags_e.get_text(),
                machine_id=str((machine or {}).get("id") or ""),
            )
            if machine:
                row["last_online"] = machine.get("last_online")
                row["last_probe_at"] = machine.get("last_probe_at") or ""
                row["last_method"] = machine.get("last_method") or ""
                row["last_error"] = machine.get("last_error") or ""
            win._fleet_store = fleet.upsert_machine(win._fleet_store, row)
            persist(win)
            win._fleet_selected_id = row["id"]
            render(win)
            show_toast(win._toast_overlay, i18n.t("fleet_saved"))
        except fleet.FleetError as exc:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(exc)))

    dialog.connect("response", on_response)
    dialog.present(win)


def edit_selected(win: Any) -> None:
    machine = _selected(win)
    if machine is None:
        show_toast(win._toast_overlay, i18n.t("fleet_no_selection"))
        return
    open_editor(win, machine)


def delete_selected(win: Any) -> None:
    machine = _selected(win)
    if machine is None:
        show_toast(win._toast_overlay, i18n.t("fleet_no_selection"))
        return

    def do_delete() -> None:
        try:
            win._fleet_store = fleet.delete_machine(win._fleet_store, str(machine.get("id") or ""))
            persist(win)
            win._fleet_selected_id = ""
            render(win)
            show_toast(win._toast_overlay, i18n.t("fleet_saved"))
        except fleet.FleetError as exc:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(exc)))

    confirm_dialog(
        win,
        i18n.t("fleet_delete_title"),
        i18n.t("fleet_delete_body", name=machine.get("name") or "?"),
        confirm_label=i18n.t("fleet_delete"),
        destructive=True,
        on_confirm=do_delete,
    )


def _set_busy(win: Any, busy: bool) -> None:
    if busy:
        win._fleet_spinner.set_visible(True)
        win._fleet_spinner.start()
    else:
        win._fleet_spinner.stop()
        win._fleet_spinner.set_visible(False)


def ping_selected(win: Any) -> None:
    machine = _selected(win)
    if machine is None:
        show_toast(win._toast_overlay, i18n.t("fleet_no_selection"))
        return
    show_toast(win._toast_overlay, i18n.t("fleet_pinging", name=machine.get("name") or ""), timeout=2)
    _set_busy(win, True)

    def work() -> dict[str, Any]:
        return fleet.probe_machine(machine)

    def done(result: Any, error: BaseException | None) -> None:
        _set_busy(win, False)
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(error)))
            return
        updated = fleet.apply_probe(machine, result or {})
        win._fleet_store = fleet.upsert_machine(win._fleet_store, updated)
        persist(win)
        render(win)
        if result and result.get("fallback"):
            show_toast(win._toast_overlay, str(result.get("error") or i18n.t("fleet_error", detail="ICMP")))
        elif result and result.get("online"):
            show_toast(win._toast_overlay, i18n.t("fleet_online"))
        else:
            show_toast(win._toast_overlay, i18n.t("fleet_offline"))

    run_in_thread(work, done)


def ping_all(win: Any) -> None:
    machines = list(win._fleet_store.get("machines") or [])
    if not machines:
        show_toast(win._toast_overlay, i18n.t("fleet_empty"))
        return
    _set_busy(win, True)

    def work() -> list[dict[str, Any]]:
        updated: list[dict[str, Any]] = []
        for item in machines:
            result = fleet.probe_machine(item)
            updated.append(fleet.apply_probe(item, result))
        return updated

    def done(result: Any, error: BaseException | None) -> None:
        _set_busy(win, False)
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(error)))
            return
        store = fleet.empty_store()
        for item in result or []:
            store = fleet.upsert_machine(store, item)
        win._fleet_store = store
        persist(win)
        render(win)
        online = sum(1 for item in store["machines"] if item.get("last_online") is True)
        show_toast(
            win._toast_overlay,
            i18n.t("fleet_ping_all_done", online=online, total=len(store["machines"])),
        )

    run_in_thread(work, done)


def export_json(win: Any) -> None:
    machines = list(win._fleet_store.get("machines") or [])
    if not machines:
        show_toast(win._toast_overlay, i18n.t("conn_no_export"))
        return
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = Path.home() / "Documents" / f"hub-reseau-parc-{stamp}.json"
    payload = fleet.export_store_json(win._fleet_store)

    def work() -> Any:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        return path

    def done(result: Any, error: BaseException | None) -> None:
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(error)))
            return
        show_toast(win._toast_overlay, i18n.t("fleet_exported", path=str(result)))

    run_in_thread(work, done)


def import_json(win: Any) -> None:
    dialog = Gtk.FileDialog(title=i18n.t("fleet_import"))
    filters = Gtk.FileFilter()
    filters.add_pattern("*.json")
    filters.set_name("JSON")
    dialog.set_default_filter(filters)

    def on_done(_source: object, result: object) -> None:
        try:
            gfile = dialog.open_finish(result)
        except GLib.Error:
            return
        path = gfile.get_path()
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8")
            imported = fleet.import_store_from_json(text)
            win._fleet_store = fleet.merge_import(win._fleet_store, imported)
            persist(win)
            render(win)
            show_toast(
                win._toast_overlay,
                i18n.t(
                    "fleet_import_ok",
                    count=len(win._fleet_store.get("machines") or []),
                ),
            )
        except fleet.FleetError as exc:
            show_toast(win._toast_overlay, i18n.t("fleet_import_error", detail=str(exc)))

    dialog.open(win, None, on_done)


def export_csv(win: Any) -> None:
    machines = list(win._fleet_store.get("machines") or [])
    if not machines:
        show_toast(win._toast_overlay, i18n.t("conn_no_export"))
        return
    path = fleet.default_export_path()
    payload = fleet.to_csv(machines)

    def work() -> Any:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
        return path

    def done(result: Any, error: BaseException | None) -> None:
        if error is not None:
            show_toast(win._toast_overlay, i18n.t("fleet_error", detail=str(error)))
            return
        show_toast(win._toast_overlay, i18n.t("fleet_exported", path=str(result)))

    run_in_thread(work, done)
