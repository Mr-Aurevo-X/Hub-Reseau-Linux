# Graph Report - Hub-Reseau  (2026-08-23)

## Corpus Check
- 127 files · ~57,750 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1366 nodes · 3104 edges · 78 communities (65 shown, 13 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5bff45fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main_window.py
- updater.py
- i18n.py
- backup.py
- MainWindow
- core/fleet.py
- cleaner.py
- t
- lan_scan.py
- packages.py
- run_in_thread
- main.py
- host_probe.py
- machine_sheet.py
- connections.py
- monitoring.py
- test_features.py
- which
- jobs.py
- dialogs/settings.py
- vpn_ctl.py
- adw_compat.py
- is_flatpak
- install.sh
- ui_kit/compat.py
- firewall.py
- host.py
- timers.py
- ._render_packages
- CircularGauge
- Any
- evaluate
- logs.py
- autostart.py
- ActionListRow
- disk_usage.py
- smart.py
- Any
- core/legal.py
- list_sessions
- plugins.py
- collect_startup_compatibility
- users.py
- write_update_script
- ._build_network_page
- t
- build-flatpak.sh
- LANCER.sh
- alerts.py
- build-deb.sh
- sync-public-readmes.sh
- add_status_class
- manifest.json
- builders_for
- publish-flatpak-release.sh
- INSTALLER-RACCOURCI.sh
- INSTALLER-RACCOURCI-FLATPAK.sh
- uninstall.sh
- test_network_ctl.py
- updates_dir
- test_packages_terminal.py
- Hub Réseau 2.0 — design
- Conditions d'utilisation — Hub Réseau
- Legal notice — Hub Réseau
- Hub Réseau (Linux)
- Global Constraints
- Vie privée / RGPD — Hub Réseau
- test_update_safety.py
- ._refresh_logs
- Flathub (futur)
- COMPAT.md
- public-legal-notes.md
- packaging/README.md
- licenses.md

## God Nodes (most connected - your core abstractions)
1. `MainWindow` - 131 edges
2. `run_in_thread()` - 55 edges
3. `show_toast()` - 45 edges
4. `t()` - 37 edges
5. `which()` - 29 edges
6. `run()` - 24 edges
7. `confirm_dialog()` - 20 edges
8. `new_machine()` - 19 edges
9. `assemble_sheet()` - 18 edges
10. `make_message_dialog()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `test_validate_pkg_id()` --calls--> `_validate_pkg_id()`  [EXTRACTED]
  tests/test_validators.py → core/packages.py
- `test_update_urls_allow_our_github_only()` --calls--> `_require_allowed_url()`  [EXTRACTED]
  tests/test_update_safety.py → core/updater.py
- `test_flatpak_install_block_includes_menu_shortcut()` --calls--> `flatpak_install_block()`  [EXTRACTED]
  tests/test_update_safety.py → core/updater.py
- `make_switch_row()` --indirect_call--> `set_active()`  [INFERRED]
  ui/adw_compat.py → core/vpn_ctl.py
- `HubReseauApp` --uses--> `MainWindow`  [INFERRED]
  main.py → ui/main_window.py

## Import Cycles
- None detected.

## Communities (78 total, 13 thin omitted)

### Community 0 - "main_window.py"
Cohesion: 0.13
Nodes (18): HeaderBar, apply_app_css(), build_main_layout(), content_title_parts(), format_app_line(), _new_update_button(), Any, Button (+10 more)

### Community 1 - "updater.py"
Cohesion: 0.20
Nodes (25): Channel, app_display_name(), apply_update(), _asset_name(), _asset_url(), check_for_update(), _find_extract_root(), flatpak_install_block() (+17 more)

### Community 2 - "i18n.py"
Cohesion: 0.06
Nodes (49): get_language(), nav_items(), normalize_language(), set_language(), _copy_fleet_from_gest(), _copy_legacy_tree(), Path, run_first_launch_migration() (+41 more)

### Community 3 - "backup.py"
Cohesion: 0.08
Nodes (55): BackupError, create_snapshot(), delete_snapshot(), detect_backend(), is_available(), list_snapshots(), _list_timeshift(), _needs_root() (+47 more)

### Community 5 - "core/fleet.py"
Cohesion: 0.10
Nodes (51): apply_probe(), default_export_path(), delete_machine(), empty_store(), export_store_json(), fleet_path(), FleetError, _icmp_denied() (+43 more)

### Community 6 - "cleaner.py"
Cohesion: 0.07
Nodes (49): _browser_cache_paths(), clean(), CleanerError, _dir_size(), _home(), _human_mib(), _is_under_whitelist(), Any (+41 more)

### Community 7 - "t"
Cohesion: 0.06
Nodes (72): Clamp, Any, t(), FlowBox, FlowBoxChild, SearchEntry, Gtk.SearchEntry.set_placeholder_text exists only since GTK 4.10., set_placeholder_text() (+64 more)

### Community 8 - "lan_scan.py"
Cohesion: 0.09
Nodes (41): _add_source(), _as_ipv4(), clamp_network(), default_export_path(), _default_ping(), _ensure_host(), _ip_addr_json(), _ip_neigh_text() (+33 more)

### Community 9 - "packages.py"
Cohesion: 0.20
Nodes (23): apply_updates(), available_managers(), check_updates(), flatpak_permissions(), _list_apt(), _list_dnf(), _list_flatpak(), list_packages() (+15 more)

### Community 10 - "run_in_thread"
Cohesion: 0.08
Nodes (8): confirm_dialog(), BaseException, ToastOverlay, Window, Run ``fn`` in a worker thread and deliver result on the GTK main loop., run_in_thread(), show_toast(), Path

### Community 11 - "main.py"
Cohesion: 0.09
Nodes (26): apply_safe_display_env(), cairo_display_env(), host_needs_map_hold(), _host_os_release(), _host_product_name(), needs_cairo_gsk(), needs_map_hold(), Path (+18 more)

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

### Community 16 - "test_features.py"
Cohesion: 0.18
Nodes (17): default_export_path(), export_report(), _listening_ports(), Path, quick_report(), traceroute_lines(), write_export(), MonkeyPatch (+9 more)

### Community 17 - "which"
Cohesion: 0.23
Nodes (19): Locate a host executable. ``command -v`` is a shell builtin, not a binary., which(), bluetooth_status(), NetworkCtlError, _nmcli_c_env(), Any, CompletedProcess, Exception (+11 more)

### Community 18 - "jobs.py"
Cohesion: 0.14
Nodes (20): JobError, Exception, Path, Raised when a host job cannot start., Allow only ``*.sh`` files written under ``updater.updates_dir()``., Argv for the host: util-linux ``script`` PTY when available, else bash., Start the script on the host; caller reads ``stdout`` (merged stderr)., script_argv() (+12 more)

### Community 19 - "dialogs/settings.py"
Cohesion: 0.24
Nodes (21): RGBA, choose_rgba(), present(), Any, Window, apply_theme(), build_css(), _css_for_merged() (+13 more)

### Community 20 - "vpn_ctl.py"
Cohesion: 0.18
Nodes (19): _env_proxy(), _gsettings_proxy_mode(), list_connections(), list_proxy(), parse_connections(), Any, Exception, Invalid VPN operation or missing tooling. (+11 more)

### Community 21 - "adw_compat.py"
Cohesion: 0.09
Nodes (26): Adjustment, test_call_if_present_true_and_false_branches(), test_first_attr_falls_back_when_modern_missing(), test_first_attr_prefers_modern_name(), CompatDialog, make_message_dialog(), make_spin_row(), make_switch_row() (+18 more)

### Community 22 - "is_flatpak"
Cohesion: 0.20
Nodes (15): is_flatpak(), kill_process(), list_processes(), process_details(), process_tree(), ProcessError, Any, Exception (+7 more)

### Community 23 - "install.sh"
Cohesion: 0.25
Nodes (17): detect_pkg_family(), ensure_path_hint(), flatpak_hint(), install_app_files(), install_deps_apk(), install_deps_apt(), install_deps_dnf(), install_deps_pacman() (+9 more)

### Community 24 - "ui_kit/compat.py"
Cohesion: 0.14
Nodes (21): open_external_uri(), present_alert(), present_startup_error(), Any, Widget, Window, Show a modal error when the app fails before the main window exists., set_bin_child() (+13 more)

### Community 25 - "firewall.py"
Cohesion: 0.25
Nodes (15): detect_backend(), _extract_rules(), _firewalld_status(), FirewallError, is_available(), _needs_root(), _parse_active(), Any (+7 more)

### Community 26 - "host.py"
Cohesion: 0.21
Nodes (21): collect_inventory(), collect_metrics(), _effective_host_cwd(), host_cwd(), _host_probe(), install_flatpak_host_bridge(), _is_sandbox_path(), kill_process() (+13 more)

### Community 27 - "timers.py"
Cohesion: 0.23
Nodes (14): control_timer(), list_timers(), parse_list_timers_output(), Any, CompletedProcess, Exception, Raised when a systemd timer operation fails., Parse ``systemctl list-timers --all`` legend output. (+6 more)

### Community 29 - "CircularGauge"
Cohesion: 0.07
Nodes (11): DrawingArea, CircularGauge, CoreBars, MetricRow, Any, Compact per-core CPU usage bars., Simple sparkline chart for recent metric history., Simple key/value metric row. (+3 more)

### Community 31 - "evaluate"
Cohesion: 0.33
Nodes (11): _cpu_temp_c(), evaluate(), _f(), _item(), Any, Return score 0–100, grade A–D, items and failing recommendations., _root_disk_percent(), _metrics() (+3 more)

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

### Community 37 - "Any"
Cohesion: 0.16
Nodes (16): _BlockHttpHandler, download_bundle(), _http_json(), _opener(), Any, Exception, Raised when download or install fails after an update was offered., Reject anything that is not HTTPS GitHub (API, our repos, or release CDN). (+8 more)

### Community 38 - "core/legal.py"
Cohesion: 0.36
Nodes (7): copyright_line(), _extract_lang(), legal_markdown(), _legal_paths(), Path, test_copyright_line(), test_legal_markdown_fr_en()

### Community 39 - "list_sessions"
Cohesion: 0.36
Nodes (8): list_sessions(), Any, CompletedProcess, Exception, Raised when session listing fails., _run(), SessionError, _who_fallback()

### Community 40 - "plugins.py"
Cohesion: 0.25
Nodes (15): ensure_example_plugin(), list_plugins(), PluginError, plugins_dir(), Any, Exception, Path, Raised when a plugin fails. (+7 more)

### Community 41 - "collect_startup_compatibility"
Cohesion: 0.36
Nodes (7): collect_startup_compatibility(), _host_shell_works(), Any, Path, Return non-fatal compatibility findings used at startup., _read_os_release(), _which_many()

### Community 42 - "users.py"
Cohesion: 0.32
Nodes (7): list_groups(), list_users(), lock_user(), Any, Exception, Raised when user operations fail., UsersError

### Community 43 - "write_update_script"
Cohesion: 0.17
Nodes (15): launch_check_terminal(), launch_update_terminal(), _maybe_host(), open_terminal_script(), wget first (Mint 21 often has no curl), then curl. Never emit a glob like *curl., Terminal script that shows the update-check result (and optional install)., Write a visible bash updater that downloads, installs, then relaunches., Open Konsole (or another terminal) running the script; do not wait for exit. (+7 more)

### Community 45 - "t"
Cohesion: 0.25
Nodes (12): present(), Window, _assemble_window(), _build_footer(), build_title(), _copy_text(), present(), Widget (+4 more)

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

### Community 53 - "builders_for"
Cohesion: 0.50
Nodes (3): builders_for(), Any, Return page key → zero-arg builder bound to ``win``.

### Community 61 - "test_network_ctl.py"
Cohesion: 0.24
Nodes (10): summary_lines(), parse_wifi_radio(), Return ``(available, enabled)`` from ``WIFI:WIFI-HW`` or ``nmcli radio wifi``., MonkeyPatch, test_home_summary_off_when_radio_disabled(), test_parse_wifi_radio_disabled_without_hardware(), test_parse_wifi_radio_french_desactive(), test_wifi_rescan_calls_nmcli() (+2 more)

### Community 62 - "updates_dir"
Cohesion: 0.29
Nodes (12): launch_apply_updates_terminal(), launch_check_updates_terminal(), _pkg_lock_preamble(), pkg_terminal_done_path(), Path, Host terminal script: live check (no capture). ``set -u``, not ``set -e``., Host terminal script: live upgrade. ``set -u``, not ``set -e``., write_apply_updates_script() (+4 more)

### Community 63 - "test_packages_terminal.py"
Cohesion: 0.33
Nodes (8): host_manager_labels(), Managers the apply script will actually run (Flatpak-aware ``which``)., _assert_pkg_lock(), Path, test_host_manager_labels_with_pkexec_includes_pacman(), test_host_manager_labels_without_pkexec_skips_pacman(), test_package_apply_script_is_live(), test_package_check_script_is_live()

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

### Community 71 - "test_update_safety.py"
Cohesion: 0.40
Nodes (4): parametrize, test_flatpak_install_block_includes_menu_shortcut(), test_update_urls_allow_our_github_only(), test_update_urls_reject_backdoors()

### Community 73 - "Flathub (futur)"
Cohesion: 0.50
Nodes (3): Flathub (futur), Prérequis Flathub (quand soumis), Source correspondante

## Knowledge Gaps
- **41 isolated node(s):** `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH`, `PYTHONUNBUFFERED`, `version` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `MainWindow` to `main_window.py`, `ActionListRow`, `i18n.py`, `._refresh_logs`, `run_in_thread`, `main.py`, `._build_network_page`, `adw_compat.py`, `._render_packages`, `CircularGauge`, `Any`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `run_in_thread()` connect `run_in_thread` to `main_window.py`, `ActionListRow`, `MainWindow`, `t`, `._refresh_logs`, `._build_network_page`, `._render_packages`, `CircularGauge`, `Any`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `ui_kit/compat.py`, `main_window.py`, `dialogs/settings.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `MainWindow` (e.g. with `HubReseauApp` and `ActionListRow`) actually correct?**
  _`MainWindow` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main_window.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1310344827586207 - nodes in this community are weakly interconnected._
- **Should `i18n.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061457418788410885 - nodes in this community are weakly interconnected._