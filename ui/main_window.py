# SPDX-License-Identifier: GPL-3.0-or-later
"""Main application window with sidebar navigation."""

from __future__ import annotations

import time
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk  # noqa: E402

from core import (
    compat,
    i18n,
    settings as app_settings,
    updater,
)
from ui import pages as ui_pages
from ui.adw_compat import (
    make_message_dialog,
    make_spin_row,
    make_switch_row,
    response_appearance,
)
from ui.components import (
    ActionListRow,
    apply_app_css,
    make_spinner,
    run_in_thread,
    show_toast,
)
from ui.nav import NavSidebar, page_titles
from ui.search import present as present_search
from ui_kit.shell import ShellLayout, build_main_layout
from ui_kit.strings import t as kit_t


def _nav_items() -> list[tuple[str, str, str]]:
    return i18n.nav_items()


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application) -> None:
        display = updater.app_display_name()
        super().__init__(application=application, title=display)
        self.add_css_class("uni-window")
        self.set_default_size(1200, 780)
        apply_app_css()

        self._settings = app_settings.load_settings()
        i18n.set_language(app_settings.coerce_language(self._settings.get("language")))
        self._nav_items = _nav_items()
        self._layout: ShellLayout | None = None

        self._current_page = "home"
        self._network_chip = "adapters"
        self._connection_items: list[dict[str, Any]] = []
        self._busy_ops = 0
        self._privileged_buttons: list[Gtk.Widget] = []
        self._update_in_progress = False

        self._toast_overlay = Adw.ToastOverlay()
        self.set_content(self._toast_overlay)

        self._build_ui()
        self._install_actions()
        self._show_page("home")
        GLib.timeout_add(700, self._check_startup_compatibility)
        if not app_settings.needs_language_prompt(self._settings):
            GLib.timeout_add(2000, self._maybe_check_updates)
        self._logged_mapped = False
        self.connect("map", self._on_window_mapped)
        self.connect("close-request", self._on_close)

    def _on_window_mapped(self, *_args: object) -> None:
        if self._logged_mapped:
            return
        self._logged_mapped = True
        print("fenêtre ouverte", flush=True)
        if app_settings.needs_language_prompt(self._settings):
            GLib.idle_add(self._prompt_language)

    def _install_actions(self) -> None:
        refresh = Gio.SimpleAction.new("refresh", None)
        refresh.connect("activate", lambda *_: self._refresh_current_page())
        self.add_action(refresh)

        prefs = Gio.SimpleAction.new("preferences", None)
        prefs.connect("activate", lambda *_: self._open_preferences())
        self.add_action(prefs)

        about = Gio.SimpleAction.new("about", None)
        about.connect("activate", lambda *_: self._open_legal_kit())
        self.add_action(about)

        search = Gio.SimpleAction.new("search", None)
        search.connect("activate", lambda *_: present_search(self))
        self.add_action(search)

        for idx, (key, _label, _icon) in enumerate(self._nav_items, start=1):
            action = Gio.SimpleAction.new(f"page{idx}", None)
            action.connect("activate", lambda *_a, k=key: self._goto_page(k))
            self.add_action(action)

        app = self.get_application()
        if app is not None:
            app.set_accels_for_action("win.refresh", ["F5"])
            app.set_accels_for_action("win.preferences", ["<Control>comma"])
            app.set_accels_for_action("win.search", ["<Control>k"])
            app.set_accels_for_action("app.quit", ["<Control>q"])
            for idx in range(1, min(10, len(self._nav_items) + 1)):
                app.set_accels_for_action(f"win.page{idx}", [f"<Control>{idx}"])

    def _goto_page(self, key: str) -> None:
        if hasattr(self, "_nav_sidebar"):
            self._nav_sidebar.select_page(key, notify=True)

    def _on_nav_page_selected(self, key: str) -> None:
        self._show_page(key)

    def _on_nav_groups_changed(self, expanded: dict[str, bool]) -> None:
        self._settings["nav_groups_expanded"] = expanded
        app_settings.save_settings(self._settings)

    def _refresh_current_page(self) -> None:
        key = self._current_page
        if key == "fleet":
            self._refresh_fleet(show_spinner=True)
        elif key == "network":
            self._refresh_network(show_spinner=True)
        elif key == "home":
            self._refresh_home()
        elif key == "lan_scan":
            from ui.pages import scan_page

            scan_page.refresh(self)
        elif key == "vpn":
            reload_vpn = getattr(self, "_vpn_reload", None)
            if callable(reload_vpn):
                reload_vpn()
        elif key == "network_diag":
            from ui.pages import diag_page

            diag_page.refresh(self)

    def _set_busy(self, busy: bool) -> None:
        self._busy_ops = max(0, self._busy_ops + (1 if busy else -1))
        enabled = self._busy_ops == 0
        for widget in self._privileged_buttons:
            widget.set_sensitive(enabled)
        if hasattr(self, "_header_spinner"):
            self._header_spinner.set_visible(self._busy_ops > 0)

    def _track_privileged(self, widget: Gtk.Widget) -> Gtk.Widget:
        self._privileged_buttons.append(widget)
        return widget

    def _build_ui(self) -> None:
        self._nav_sidebar = NavSidebar(
            settings=self._settings,
            on_page_selected=self._on_nav_page_selected,
            on_groups_changed=self._on_nav_groups_changed,
        )
        nav_scroll = self._nav_sidebar.widget

        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.set_transition_duration(180)
        self._stack.set_hexpand(True)
        self._stack.set_vexpand(True)

        self._page_builders = ui_pages.builders_for(self)
        self._built_pages: set[str] = set()
        self._ensure_page("home")

        layout = build_main_layout(
            nav_scroll,
            self._stack,
            page_title=page_titles().get("home", i18n.t("home")),
            lang=i18n.get_language(),
        )
        self._header_spinner = make_spinner(size=18)
        self._header_spinner.set_visible(False)
        layout.content_header.pack_end(self._header_spinner)

        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        self._refresh_header_btn = refresh_btn
        refresh_btn.set_tooltip_text(f"{i18n.t('refresh')} (F5)")
        refresh_btn.connect("clicked", lambda *_: self._refresh_current_page())
        layout.content_header.pack_end(refresh_btn)

        layout.attach_chrome_buttons(
            self,
            on_check_updates=self._chrome_check_updates,
            on_language_toggle=self._apply_language,
            current_language=i18n.get_language(),
            settings_snapshot=self._settings,
            current_version=updater.local_version(),
            on_settings_save=self._save_prefs_from_kit,
            on_open_preferences=self._open_preferences,
        )
        self._layout = layout
        self._toast_overlay.set_child(layout.widget)
        self._nav_sidebar.select_page("home", notify=False)

    def _ensure_page(self, key: str) -> Gtk.Widget:
        child = self._stack.get_child_by_name(key)
        if child is not None:
            return child
        builder = self._page_builders.get(key)
        if builder is None:
            raise KeyError(key)
        widget = builder()
        self._stack.add_named(widget, key)
        self._built_pages.add(key)
        return widget

    def _show_page(self, key: str) -> None:
        self._current_page = key
        titles = page_titles()
        if self._layout is not None:
            self._layout.set_page_title(titles.get(key, key))
        if hasattr(self, "_nav_sidebar"):
            self._nav_sidebar.select_page(key, notify=False)
        self._ensure_page(key)
        self._stack.set_visible_child_name(key)
        if key == "fleet":
            self._refresh_fleet()
        elif key == "network":
            self._refresh_network()
        elif key == "home":
            self._refresh_home()

    def _open_preferences(self) -> None:
        from ui_kit.dialogs import settings as kit_settings

        win = Adw.PreferencesWindow()
        win.set_transient_for(self)
        win.set_modal(True)
        win.set_title(i18n.t("preferences"))

        page = Adw.PreferencesPage()
        page.set_title(i18n.t("preferences"))
        page.set_icon_name("preferences-system-symbolic")

        general = Adw.PreferencesGroup()
        general.set_title(i18n.t("general"))

        alerts_row = make_switch_row()
        alerts_row.set_title(i18n.t("alerts"))
        alerts_row.set_active(bool(self._settings.get("alerts_enabled", True)))
        general.add(alerts_row)
        page.add(general)

        appearance = Adw.PreferencesGroup()
        appearance.set_title(kit_t("appearance", i18n.get_language()))
        appearance.set_description(kit_t("appearance_sub", i18n.get_language()))
        theme_row = ActionListRow(
            kit_t("theme_preset", i18n.get_language()),
            kit_t("appearance_sub", i18n.get_language()),
            button_label=kit_t("preferences", i18n.get_language()),
            button_css="flat",
            on_clicked=lambda: kit_settings.present(
                self,
                self._settings,
                current_version=updater.local_version(),
                lang=i18n.get_language(),
                on_save=self._save_prefs_from_kit,
            ),
        )
        appearance.add(theme_row)
        page.add(appearance)

        updates = Adw.PreferencesGroup()
        updates.set_title(i18n.t("updates"))
        updates.set_description(i18n.t("updates_group_desc"))

        update_row = make_switch_row()
        update_row.set_title(i18n.t("auto_update"))
        update_row.set_subtitle(i18n.t("auto_update_subtitle"))
        update_row.set_active(bool(self._settings.get("auto_update_on_startup", True)))

        def on_auto_update_toggle(_row: Gtk.Widget, *_args: object) -> None:
            self._set_auto_update_enabled(update_row.get_active())

        update_row.connect("notify::active", on_auto_update_toggle)
        updates.add(update_row)
        page.add(updates)

        thresholds = Adw.PreferencesGroup()
        thresholds.set_title(i18n.t("alert_thresholds"))
        th = dict(self._settings.get("thresholds") or app_settings.DEFAULTS["thresholds"])

        def _spin_row(title: str, value: float, *, upper: float = 100.0) -> Gtk.Widget:
            adj = Gtk.Adjustment(
                value=float(value),
                lower=1.0,
                upper=upper,
                step_increment=1.0,
                page_increment=5.0,
            )
            row = make_spin_row(adjustment=adj, digits=0)
            row.set_title(title)
            return row

        cpu_row = _spin_row(i18n.t("cpu_pct"), float(th.get("cpu_percent", 90)))
        ram_row = _spin_row(i18n.t("ram_pct"), float(th.get("ram_percent", 90)))
        temp_row = _spin_row(i18n.t("temp_c"), float(th.get("temp_celsius", 85)), upper=120.0)
        disk_row = _spin_row(i18n.t("disk_pct"), float(th.get("disk_percent", 90)))
        for row in (cpu_row, ram_row, temp_row, disk_row):
            thresholds.add(row)
        page.add(thresholds)

        save_group = Adw.PreferencesGroup()
        save_btn = Gtk.Button(label=i18n.t("save"))
        save_btn.add_css_class("suggested-action")
        save_btn.set_halign(Gtk.Align.END)
        save_btn.set_margin_top(8)
        save_btn.set_margin_bottom(8)

        def on_save(*_a: object) -> None:
            new_settings = dict(self._settings)
            new_settings.update(
                {
                    "alerts_enabled": alerts_row.get_active(),
                    "auto_update_on_startup": update_row.get_active(),
                    "thresholds": {
                        "cpu_percent": float(cpu_row.get_value()),
                        "ram_percent": float(ram_row.get_value()),
                        "temp_celsius": float(temp_row.get_value()),
                        "disk_percent": float(disk_row.get_value()),
                    },
                }
            )
            app_settings.save_settings(new_settings)
            self._settings = app_settings.load_settings()
            show_toast(self._toast_overlay, i18n.t("prefs_saved"))
            win.close()

        save_btn.connect("clicked", on_save)
        save_group.add(save_btn)
        page.add(save_group)

        win.add(page)
        win.present()

    def _open_legal_kit(self) -> None:
        from ui_kit.dialogs import legal as legal_dialog

        legal_dialog.present(self, i18n.get_language())

    def _save_prefs_from_kit(self, _settings: dict[str, Any]) -> None:
        show_toast(self._toast_overlay, i18n.t("prefs_saved"))

    def _chrome_check_updates(self) -> None:
        self._manual_check_updates()

    def _relabel_sidebar(self) -> None:
        if hasattr(self, "_nav_sidebar"):
            self._nav_sidebar.update_settings(self._settings)
            self._nav_sidebar.relabel()
        titles = page_titles()
        if self._layout is not None:
            self._layout.set_page_title(titles.get(self._current_page, self._current_page))

    def _relabel_header(self) -> None:
        if hasattr(self, "_refresh_header_btn"):
            self._refresh_header_btn.set_tooltip_text(f"{i18n.t('refresh')} (F5)")

    def _prompt_language(self) -> bool:
        if not app_settings.needs_language_prompt(self._settings):
            return False
        dialog = make_message_dialog(self, i18n.t("welcome_lang"), i18n.t("welcome_lang_body"))
        dialog.add_response("fr", "Français")
        dialog.add_response("en", "English")
        dialog.set_response_appearance("fr", response_appearance("SUGGESTED"))

        def on_response(_d: object, response: str) -> None:
            if response not in {"fr", "en"}:
                return
            self._apply_language(response)
            GLib.timeout_add(400, self._maybe_check_updates)

        dialog.connect("response", on_response)
        dialog.present(self)
        return False

    def _apply_language(self, lang: object) -> None:
        code = app_settings.coerce_language(lang)
        same_ui = i18n.get_language() == code and str(self._settings.get("language") or "") == code
        self._settings["language"] = code
        self._settings["language_chosen"] = True
        app_settings.save_settings(self._settings)
        self._settings = app_settings.load_settings()
        if same_ui:
            return
        i18n.set_language(code)
        self._rebuild_pages()
        if self._layout is not None:
            self._layout.update_language_button(code)

    def _rebuild_pages(self) -> None:
        current = self._current_page
        for name in list(self._built_pages):
            child = self._stack.get_child_by_name(name)
            if child is not None:
                self._stack.remove(child)
        self._built_pages.clear()
        self._privileged_buttons.clear()
        self._nav_items = _nav_items()
        self._relabel_sidebar()
        self._relabel_header()
        self._ensure_page(current)
        self._show_page(current)

    def _build_fleet(self) -> Gtk.Widget:
        from ui.pages import fleet as fleet_page

        return fleet_page.build(self)

    def _build_lan_scan_page(self) -> Gtk.Widget:
        from ui.pages import scan_page

        return scan_page.build(self)

    def _build_vpn_page(self) -> Gtk.Widget:
        from ui.pages import vpn_page

        return vpn_page.build(self)

    def _build_home_page(self) -> Gtk.Widget:
        from ui.pages import home_page

        return home_page.build(self)

    def _build_network_page(self) -> Gtk.Widget:
        from ui.pages import network_page

        return network_page.build(self)

    def _build_network_diag_page(self) -> Gtk.Widget:
        from ui.pages import diag_page

        return diag_page.build(self)

    def _refresh_fleet(self, *, show_spinner: bool = False) -> None:
        from ui.pages import fleet as fleet_page

        fleet_page.refresh(self, show_spinner=show_spinner)

    def _refresh_network(self, *, show_spinner: bool = False, privileged: bool = False) -> None:
        from ui.pages import network_page

        network_page.refresh(self, show_spinner=show_spinner, privileged=privileged)

    def _refresh_home(self) -> None:
        from ui.pages import home_page

        home_page.refresh(self)

    def _set_auto_update_enabled(self, enabled: bool) -> None:
        self._settings["auto_update_on_startup"] = bool(enabled)
        app_settings.save_settings(self._settings)
        self._settings = app_settings.load_settings()

    def _manual_check_updates(self, row: ActionListRow | None = None) -> None:
        if row is not None:
            row.set_busy(True)
        show_toast(self._toast_overlay, i18n.t("update_checking"), timeout=4)

        def work() -> dict[str, Any] | None:
            return updater.check_for_update(raise_on_error=True)

        def done(result: Any, error: BaseException | None) -> None:
            if row is not None:
                row.set_busy(False)
            if error is not None:
                show_toast(
                    self._toast_overlay,
                    i18n.t("update_check_failed", detail=str(error)),
                    timeout=8,
                )
                return
            if not isinstance(result, dict):
                show_toast(
                    self._toast_overlay,
                    i18n.t("update_up_to_date", version=updater.local_version()),
                    timeout=5,
                )
                return
            self._show_update_dialog(result)

        run_in_thread(work, done)

    def _poll_update_proceed_flag(self) -> bool:
        flag = updater.updates_dir() / "proceed-install"
        if flag.is_file():
            try:
                flag.unlink(missing_ok=True)
            except OSError:
                pass
            return self._quit_for_update()
        deadline = float(getattr(self, "_update_poll_deadline", 0.0) or 0.0)
        if deadline and time.monotonic() > deadline:
            self._update_in_progress = False
            return False
        if not self._update_in_progress:
            return False
        return True

    def _maybe_check_updates(self) -> bool:
        if not bool(self._settings.get("auto_update_on_startup", True)):
            return False

        def work() -> dict[str, Any] | None:
            return updater.check_for_update()

        def done(result: Any, error: BaseException | None) -> None:
            if error is not None or not isinstance(result, dict):
                return
            self._show_update_dialog(result)

        run_in_thread(work, done)
        return False

    def _check_startup_compatibility(self) -> bool:
        def work() -> dict[str, Any]:
            return compat.collect_startup_compatibility()

        def done(result: Any, error: BaseException | None) -> None:
            if error is not None or not isinstance(result, dict):
                return
            warnings = result.get("warnings") or []
            if not warnings:
                return
            first = str(warnings[0])
            show_toast(
                self._toast_overlay,
                i18n.t("compat_degraded", detail=first),
                timeout=8,
            )

        run_in_thread(work, done)
        return False

    def _show_update_dialog(self, info: dict[str, Any]) -> None:
        from ui_kit.dialogs.update import present as present_update_dialog

        latest = str(info.get("version") or "?")
        present_update_dialog(
            self,
            i18n.t("update_available"),
            updater.format_update_dialog_body(info),
            updater.format_update_dialog_commands(info),
            new_version=latest,
            lang=i18n.get_language(),
        )

    def _quit_for_update(self) -> bool:
        app = self.get_application()
        if app is not None:
            app.quit()
        return False

    def _show_update_restart_dialog(self) -> None:
        dialog = make_message_dialog(
            self,
            i18n.t("update_installed"),
            i18n.t("update_restart_body", command=updater.restart_hint()),
        )
        dialog.add_response("close", i18n.t("update_close"))
        dialog.add_response("quit", i18n.t("update_quit"))
        dialog.set_response_appearance("quit", response_appearance("SUGGESTED"))
        dialog.set_default_response("quit")
        dialog.set_close_response("close")

        def on_response(_dialog: object, response: str) -> None:
            if response == "quit":
                app = self.get_application()
                if app is not None:
                    app.quit()

        dialog.connect("response", on_response)
        dialog.present(self)

    def _on_close(self, *_args: Any) -> bool:
        return False
