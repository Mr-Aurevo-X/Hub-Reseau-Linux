# Graph Report - Hub-Reseau  (2026-08-23)

## Corpus Check
- 133 files · ~56,700 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1355 nodes · 3090 edges · 72 communities (62 shown, 10 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `542c7576`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- dialogs/settings.py
- updater.py
- core/settings.py
- backup.py
- ._show_page
- core/fleet.py
- clean
- t
- lan_scan.py
- packages.py
- show_toast
- test_display_env.py
- host_probe.py
- machine_sheet.py
- connections.py
- monitoring.py
- run
- which
- jobs.py
- adapters.py
- vpn_ctl.py
- adw_compat.py
- is_flatpak
- install.sh
- NavSidebar
- firewall.py
- host.py
- timers.py
- scan_page.py
- CircularGauge
- vpn_page.py
- make_search_refresh_bar
- logs.py
- autostart.py
- ActionListRow
- disk_usage.py
- smart.py
- nav.py
- core/legal.py
- list_sessions
- ._rebuild_pages
- collect_startup_compatibility
- users.py
- make_clamped_list
- MainWindow
- build-flatpak.sh
- LANCER.sh
- alerts.py
- build-deb.sh
- sync-public-readmes.sh
- add_status_class
- manifest.json
- main_window.py
- publish-flatpak-release.sh
- INSTALLER-RACCOURCI.sh
- INSTALLER-RACCOURCI-FLATPAK.sh
- uninstall.sh
- test_network_ctl.py
- Hub Réseau 2.0 — design
- Conditions d'utilisation — Hub Réseau
- Legal notice — Hub Réseau
- Hub Réseau (Linux)
- Global Constraints
- Vie privée / RGPD — Hub Réseau
- Flathub (futur)
- COMPAT.md
- public-legal-notes.md
- packaging/README.md
- licenses.md

## God Nodes (most connected - your core abstractions)
1. `t()` - 60 edges
2. `MainWindow` - 46 edges
3. `show_toast()` - 38 edges
4. `run_in_thread()` - 32 edges
5. `which()` - 30 edges
6. `run()` - 25 edges
7. `new_machine()` - 19 edges
8. `assemble_sheet()` - 18 edges
9. `run_scan()` - 17 edges
10. `make_message_dialog()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_validate_pkg_id()` --calls--> `_validate_pkg_id()`  [EXTRACTED]
  tests/test_validators.py → core/packages.py
- `make_switch_row()` --indirect_call--> `set_active()`  [INFERRED]
  ui/adw_compat.py → core/vpn_ctl.py
- `HubReseauApp` --uses--> `MainWindow`  [INFERRED]
  main.py → ui/main_window.py
- `main()` --uses--> `HubReseauApp`  [INFERRED]
  tests/gtk_smoke.py → main.py
- `MainWindow` --uses--> `ShellLayout`  [INFERRED]
  ui/main_window.py → ui_kit/shell.py

## Import Cycles
- None detected.

## Communities (72 total, 10 thin omitted)

### Community 0 - "dialogs/settings.py"
Cohesion: 0.05
Nodes (71): HeaderBar, RGBA, choose_rgba(), open_external_uri(), present_alert(), present_startup_error(), Any, Widget (+63 more)

### Community 1 - "updater.py"
Cohesion: 0.06
Nodes (79): Channel, _pkg_lock_preamble(), pkg_terminal_done_path(), ensure_example_plugin(), list_plugins(), PluginError, plugins_dir(), Any (+71 more)

### Community 2 - "core/settings.py"
Cohesion: 0.07
Nodes (46): _cpu_temp_c(), evaluate(), _f(), _item(), Any, Return score 0–100, grade A–D, items and failing recommendations., _root_disk_percent(), get_language() (+38 more)

### Community 3 - "backup.py"
Cohesion: 0.08
Nodes (55): BackupError, create_snapshot(), delete_snapshot(), detect_backend(), is_available(), list_snapshots(), _list_timeshift(), _needs_root() (+47 more)

### Community 5 - "core/fleet.py"
Cohesion: 0.09
Nodes (53): apply_probe(), default_export_path(), delete_machine(), empty_store(), export_store_json(), fleet_path(), FleetError, _icmp_denied() (+45 more)

### Community 6 - "clean"
Cohesion: 0.07
Nodes (50): _browser_cache_paths(), clean(), CleanerError, _dir_size(), _home(), _human_mib(), _is_under_whitelist(), Any (+42 more)

### Community 7 - "t"
Cohesion: 0.20
Nodes (28): Any, t(), FlowBox, FlowBoxChild, build(), _clear_box(), delete_selected(), edit_selected() (+20 more)

### Community 8 - "lan_scan.py"
Cohesion: 0.09
Nodes (46): _add_source(), _as_ipv4(), clamp_network(), default_export_path(), _default_ping(), _ensure_host(), _ip_addr_json(), _ip_neigh_text() (+38 more)

### Community 9 - "packages.py"
Cohesion: 0.11
Nodes (39): apply_updates(), available_managers(), check_updates(), flatpak_permissions(), host_manager_labels(), launch_apply_updates_terminal(), launch_check_updates_terminal(), _list_apt() (+31 more)

### Community 10 - "show_toast"
Cohesion: 0.16
Nodes (34): make_switch_row(), Gtk.SearchEntry.set_placeholder_text exists only since GTK 4.10., set_placeholder_text(), make_spinner(), BaseException, ToastOverlay, Widget, Prefer Adw.Spinner (libadwaita ≥ 1.6), fall back to Gtk.Spinner. (+26 more)

### Community 11 - "test_display_env.py"
Cohesion: 0.18
Nodes (18): apply_safe_display_env(), cairo_display_env(), host_needs_map_hold(), _host_os_release(), _host_product_name(), needs_cairo_gsk(), needs_map_hold(), Path (+10 more)

### Community 12 - "host_probe.py"
Cohesion: 0.16
Nodes (37): _amd(), _battery(), _boot_time(), _cmdline(), collect_inventory_raw(), collect_metrics(), _cpu_counts(), _cpu_freq() (+29 more)

### Community 13 - "machine_sheet.py"
Cohesion: 0.12
Nodes (35): assemble_sheet(), collect_sheet(), default_export_path(), _format_uptime(), _hex_ipv4_le(), parse_apt_upgradable(), parse_cpuinfo(), parse_df_p() (+27 more)

### Community 14 - "connections.py"
Cohesion: 0.11
Nodes (30): add_allowlist_entry(), classify(), ConnectionError, endpoint_ip(), _ip_in_allow_entry(), _is_known_ip(), list_connections(), _looks_bare_ip() (+22 more)

### Community 15 - "monitoring.py"
Cohesion: 0.15
Nodes (28): _amd_gpu(), _battery_info(), collect_metrics(), _cpu_info(), _cpu_temperatures(), detailed_sensors(), _disk_info(), format_uptime() (+20 more)

### Community 16 - "run"
Cohesion: 0.15
Nodes (21): kill_process(), CompletedProcess, renice_process(), run(), default_export_path(), export_report(), _listening_ports(), Path (+13 more)

### Community 17 - "which"
Cohesion: 0.23
Nodes (19): Locate a host executable. ``command -v`` is a shell builtin, not a binary., which(), bluetooth_status(), NetworkCtlError, _nmcli_c_env(), Any, CompletedProcess, Exception (+11 more)

### Community 18 - "jobs.py"
Cohesion: 0.14
Nodes (20): JobError, Exception, Path, Raised when a host job cannot start., Allow only ``*.sh`` files written under ``updater.updates_dir()``., Argv for the host: util-linux ``script`` PTY when available, else bash., Start the script on the host; caller reads ``stdout`` (merged stderr)., script_argv() (+12 more)

### Community 19 - "adapters.py"
Cohesion: 0.12
Nodes (34): Adapter, AdapterSnapshot, collect_snapshot(), DefaultRoute, format_bps(), format_bytes(), _ip_json(), parse_addr_json() (+26 more)

### Community 20 - "vpn_ctl.py"
Cohesion: 0.18
Nodes (19): _env_proxy(), _gsettings_proxy_mode(), list_connections(), list_proxy(), parse_connections(), Any, Exception, Invalid VPN operation or missing tooling. (+11 more)

### Community 21 - "adw_compat.py"
Cohesion: 0.10
Nodes (23): Adjustment, test_call_if_present_true_and_false_branches(), test_first_attr_falls_back_when_modern_missing(), test_first_attr_prefers_modern_name(), CompatDialog, make_spin_row(), make_toolbar(), present_about() (+15 more)

### Community 22 - "is_flatpak"
Cohesion: 0.17
Nodes (17): install_flatpak_host_bridge(), is_flatpak(), Patch ``subprocess.run`` / ``shutil.which`` so system tools hit the host., kill_process(), list_processes(), process_details(), process_tree(), ProcessError (+9 more)

### Community 23 - "install.sh"
Cohesion: 0.25
Nodes (17): detect_pkg_family(), ensure_path_hint(), flatpak_hint(), install_app_files(), install_deps_apk(), install_deps_apt(), install_deps_dnf(), install_deps_pacman() (+9 more)

### Community 24 - "NavSidebar"
Cohesion: 0.18
Nodes (6): ListBoxRow, NavSidebar, Any, ListBox, Widget, Collapsible group sidebar with one ListBox per group.

### Community 25 - "firewall.py"
Cohesion: 0.25
Nodes (15): detect_backend(), _extract_rules(), _firewalld_status(), FirewallError, is_available(), _needs_root(), _parse_active(), Any (+7 more)

### Community 26 - "host.py"
Cohesion: 0.31
Nodes (15): collect_inventory(), collect_metrics(), _effective_host_cwd(), host_cwd(), _host_probe(), _is_sandbox_path(), list_processes(), popen() (+7 more)

### Community 27 - "timers.py"
Cohesion: 0.23
Nodes (14): control_timer(), list_timers(), parse_list_timers_output(), Any, CompletedProcess, Exception, Raised when a systemd timer operation fails., Parse ``systemctl list-timers --all`` legend output. (+6 more)

### Community 28 - "scan_page.py"
Cohesion: 0.32
Nodes (15): add_selected(), build(), cancel_scan(), _clear_list(), export_csv(), Any, ListBox, Widget (+7 more)

### Community 29 - "CircularGauge"
Cohesion: 0.08
Nodes (10): DrawingArea, CircularGauge, CoreBars, MetricRow, Any, Compact per-core CPU usage bars., Simple sparkline chart for recent metric history., Simple key/value metric row. (+2 more)

### Community 30 - "vpn_page.py"
Cohesion: 0.23
Nodes (13): build(), Any, Widget, refresh(), build(), _clear_list(), Any, ListBox (+5 more)

### Community 31 - "make_search_refresh_bar"
Cohesion: 0.15
Nodes (13): SearchEntry, ToggleButton, debounce(), Return a debounced callable that schedules ``callback`` after ``delay_ms``., make_filter_chips(), make_search_refresh_bar(), Any, BaseException (+5 more)

### Community 32 - "logs.py"
Cohesion: 0.21
Nodes (12): _clean_journal_text(), export_journal(), LogsError, _permission_issue(), Any, CompletedProcess, Exception, Path (+4 more)

### Community 33 - "autostart.py"
Cohesion: 0.29
Nodes (11): _autostart_dir(), AutostartError, list_all(), list_desktop_entries(), list_user_services(), Any, Exception, Path (+3 more)

### Community 34 - "ActionListRow"
Cohesion: 0.25
Nodes (3): ActionListRow, Button, Adw.ActionRow with a trailing action button.

### Community 35 - "disk_usage.py"
Cohesion: 0.25
Nodes (9): DiskUsageError, Any, CompletedProcess, Exception, Path, Raised when disk usage scan fails., _run(), scan_top() (+1 more)

### Community 36 - "smart.py"
Cohesion: 0.31
Nodes (10): is_available(), list_block_devices(), Any, CompletedProcess, Exception, query_device(), Raised when SMART query fails., _run() (+2 more)

### Community 37 - "nav.py"
Cohesion: 0.35
Nodes (11): test_flat_nav_starts_with_home(), test_flat_nav_unique_keys(), test_group_for_known_pages(), test_nav_registry_matches_pages(), flat_nav_items(), group_for_page(), nav_groups(), NavGroup (+3 more)

### Community 38 - "core/legal.py"
Cohesion: 0.36
Nodes (7): copyright_line(), _extract_lang(), legal_markdown(), _legal_paths(), Path, test_copyright_line(), test_legal_markdown_fr_en()

### Community 39 - "list_sessions"
Cohesion: 0.36
Nodes (8): list_sessions(), Any, CompletedProcess, Exception, Raised when session listing fails., _run(), SessionError, _who_fallback()

### Community 41 - "collect_startup_compatibility"
Cohesion: 0.36
Nodes (7): collect_startup_compatibility(), _host_shell_works(), Any, Path, Return non-fatal compatibility findings used at startup., _read_os_release(), _which_many()

### Community 42 - "users.py"
Cohesion: 0.32
Nodes (7): list_groups(), list_users(), lock_user(), Any, Exception, Raised when user operations fail., UsersError

### Community 43 - "make_clamped_list"
Cohesion: 0.67
Nodes (3): Clamp, make_clamped_list(), ListBox

### Community 44 - "MainWindow"
Cohesion: 0.14
Nodes (3): MainWindow, Any, Widget

### Community 46 - "build-flatpak.sh"
Cohesion: 0.48
Nodes (5): builder(), need(), run_builder(), build-flatpak.sh script, validate_metadata()

### Community 47 - "LANCER.sh"
Cohesion: 0.53
Nodes (5): need_pkg(), pause(), PYTHONPATH, PYTHONUNBUFFERED, LANCER.sh script

### Community 48 - "alerts.py"
Cohesion: 0.67
Nodes (3): append_history(), Any, send_desktop_notification()

### Community 49 - "build-deb.sh"
Cohesion: 0.83
Nodes (3): copy_tree(), need_cmd(), build-deb.sh script

### Community 50 - "sync-public-readmes.sh"
Cohesion: 0.83
Nodes (3): need(), put_legal_file(), sync-public-readmes.sh script

### Community 51 - "add_status_class"
Cohesion: 0.83
Nodes (3): StatusKind, add_status_class(), css_class()

### Community 52 - "manifest.json"
Cohesion: 0.50
Nodes (3): default, presets, version

### Community 53 - "main_window.py"
Cohesion: 0.14
Nodes (14): make_message_dialog(), response_appearance(), apply_app_css(), confirm_dialog(), Window, build(), Any, Widget (+6 more)

### Community 61 - "test_network_ctl.py"
Cohesion: 0.29
Nodes (9): parse_wifi_radio(), Return ``(available, enabled)`` from ``WIFI:WIFI-HW`` or ``nmcli radio wifi``., MonkeyPatch, test_home_summary_off_when_radio_disabled(), test_parse_wifi_radio_disabled_without_hardware(), test_parse_wifi_radio_french_desactive(), test_wifi_rescan_calls_nmcli(), test_wifi_rescan_requires_nmcli() (+1 more)

### Community 64 - "Hub Réseau 2.0 — design"
Cohesion: 0.22
Nodes (8): 1. Console live in-app (paquets), 2. Cliché avant le risque, 3. Score santé, 4. Flathub, Fichiers, Hors 2.0.0, Hub Réseau 2.0 — design, Non-négociable

### Community 65 - "Conditions d'utilisation — Hub Réseau"
Cohesion: 0.25
Nodes (7): 1. Objet, 2. Licence, 3. Aucune installation automatique, 4. Responsabilité, 5. Soutien facultatif, 6. Droit applicable, Conditions d'utilisation — Hub Réseau

### Community 66 - "Legal notice — Hub Réseau"
Cohesion: 0.29
Nodes (6): Conditions d’utilisation (CGU), Legal notice — Hub Réseau, Mentions légales — Hub Réseau, Privacy (GDPR), Terms of use, Vie privée (RGPD)

### Community 67 - "Hub Réseau (Linux)"
Cohesion: 0.29
Nodes (6): Confidentialité, English, Français, Hub Réseau (Linux), Installation / Install, Privacy

### Community 69 - "Global Constraints"
Cohesion: 0.33
Nodes (5): Global Constraints, Hub Réseau 2.0 Implementation Plan, Task 1: health + jobs (tests d’abord), Task 2: job console + wire packages + snapshot + dashboard, Task 3: docs + 2.0.0 ship

### Community 70 - "Vie privée / RGPD — Hub Réseau"
Cohesion: 0.33
Nodes (5): Collecte par l'éditeur, Données locales, Droit applicable, Réseau, Vie privée / RGPD — Hub Réseau

### Community 73 - "Flathub (futur)"
Cohesion: 0.50
Nodes (3): Flathub (futur), Prérequis Flathub (quand soumis), Source correspondante

## Knowledge Gaps
- **41 isolated node(s):** `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH`, `PYTHONUNBUFFERED`, `version` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `MainWindow` to `dialogs/settings.py`, `core/settings.py`, `ActionListRow`, `._show_page`, `._rebuild_pages`, `main_window.py`, `NavSidebar`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `core/settings.py`, `nav.py`, `clean`, `show_toast`, `run`, `jobs.py`, `adapters.py`, `main_window.py`, `scan_page.py`, `vpn_page.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `which()` connect `which` to `updater.py`, `lan_scan.py`, `collect_startup_compatibility`, `packages.py`, `connections.py`, `run`, `jobs.py`, `adapters.py`, `vpn_ctl.py`, `is_flatpak`, `host.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MainWindow` (e.g. with `HubReseauApp` and `ActionListRow`) actually correct?**
  _`MainWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `dialogs/settings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05049442457395329 - nodes in this community are weakly interconnected._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06282271944922548 - nodes in this community are weakly interconnected._