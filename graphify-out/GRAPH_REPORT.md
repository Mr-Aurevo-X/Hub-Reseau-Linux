# Graph Report - Hub-Reseau  (2026-08-23)

## Corpus Check
- 102 files · ~37,616 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 950 nodes · 2214 edges · 40 communities (31 shown, 9 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2b9f00c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- shell.py
- updater.py
- main_window.py
- dialogs/settings.py
- core/fleet.py
- lan_scan.py
- t
- main.py
- connections.py
- which
- adapters.py
- vpn_ctl.py
- adw_compat.py
- install.sh
- CircularGauge
- core/legal.py
- MainWindow
- build-flatpak.sh
- LANCER.sh
- build-deb.sh
- sync-public-readmes.sh
- add_status_class
- manifest.json
- publish-flatpak-release.sh
- INSTALLER-RACCOURCI.sh
- INSTALLER-RACCOURCI-FLATPAK.sh
- uninstall.sh
- Hub Réseau 2.0 — design
- Conditions d'utilisation — Hub Réseau
- Français
- Global Constraints
- Vie privée / RGPD — Hub Réseau
- FLATHUB.md
- COMPAT.md
- public-legal-notes.md
- packaging/README.md
- licenses.md

## God Nodes (most connected - your core abstractions)
1. `t()` - 58 edges
2. `MainWindow` - 46 edges
3. `show_toast()` - 40 edges
4. `run_in_thread()` - 34 edges
5. `which()` - 27 edges
6. `run()` - 23 edges
7. `new_machine()` - 19 edges
8. `run_scan()` - 17 edges
9. `make_message_dialog()` - 17 edges
10. `build()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `make_switch_row()` --indirect_call--> `set_active()`  [INFERRED]
  ui/adw_compat.py → core/vpn_ctl.py
- `HubReseauApp` --uses--> `MainWindow`  [INFERRED]
  main.py → ui/main_window.py
- `main()` --uses--> `HubReseauApp`  [INFERRED]
  tests/gtk_smoke.py → main.py
- `MainWindow` --uses--> `ShellLayout`  [INFERRED]
  ui/main_window.py → ui_kit/shell.py
- `_set_css_class()` --calls--> `toggle()`  [INFERRED]
  ui_kit/shell.py → ui/pages/vpn_page.py

## Import Cycles
- None detected.

## Communities (40 total, 9 thin omitted)

### Community 0 - "shell.py"
Cohesion: 0.06
Nodes (48): HeaderBar, open_external_uri(), present_startup_error(), Any, Widget, Show a modal error when the app fails before the main window exists., set_bin_child(), set_split_sidebar_visible() (+40 more)

### Community 1 - "updater.py"
Cohesion: 0.07
Nodes (69): Channel, app_display_name(), apply_update(), _as_release_list(), _asset_name(), _asset_url(), _BlockHttpHandler, check_for_update() (+61 more)

### Community 2 - "main_window.py"
Cohesion: 0.06
Nodes (50): get_language(), nav_items(), normalize_language(), set_language(), _copy_fleet_from_gest(), _copy_legacy_tree(), Path, run_first_launch_migration() (+42 more)

### Community 4 - "dialogs/settings.py"
Cohesion: 0.21
Nodes (23): RGBA, choose_rgba(), present_alert(), Window, present(), Any, Window, apply_theme() (+15 more)

### Community 5 - "core/fleet.py"
Cohesion: 0.09
Nodes (53): apply_probe(), default_export_path(), delete_machine(), empty_store(), export_store_json(), fleet_path(), FleetError, _icmp_denied() (+45 more)

### Community 8 - "lan_scan.py"
Cohesion: 0.09
Nodes (45): _add_source(), _as_ipv4(), clamp_network(), default_export_path(), _default_ping(), _ensure_host(), _ip_addr_json(), is_scan_ipv4() (+37 more)

### Community 10 - "t"
Cohesion: 0.05
Nodes (109): Clamp, Any, t(), FlowBox, FlowBoxChild, SearchEntry, ToggleButton, make_message_dialog() (+101 more)

### Community 11 - "main.py"
Cohesion: 0.09
Nodes (26): apply_safe_display_env(), cairo_display_env(), host_needs_map_hold(), _host_os_release(), _host_product_name(), needs_cairo_gsk(), needs_map_hold(), Path (+18 more)

### Community 14 - "connections.py"
Cohesion: 0.11
Nodes (30): add_allowlist_entry(), classify(), ConnectionError, endpoint_ip(), _ip_in_allow_entry(), _is_known_ip(), list_connections(), _looks_bare_ip() (+22 more)

### Community 16 - "which"
Cohesion: 0.06
Nodes (69): collect_startup_compatibility(), _host_shell_works(), Any, Path, Return non-fatal compatibility findings used at startup., _read_os_release(), _which_many(), _effective_host_cwd() (+61 more)

### Community 19 - "adapters.py"
Cohesion: 0.08
Nodes (49): Adapter, AdapterSnapshot, collect_snapshot(), DefaultRoute, format_bps(), format_bytes(), _ip_json(), _is_stub_dns() (+41 more)

### Community 20 - "vpn_ctl.py"
Cohesion: 0.11
Nodes (29): check_ok(), ExecError, CompletedProcess, Exception, Raised when a command fails or cannot be started., Run ``cmd`` as argv list (never through a shell)., Run ``pkexec [env …] <args>`` without ``bash -c``., Return stdout on success; raise ExecError with stderr/stdout on failure. (+21 more)

### Community 21 - "adw_compat.py"
Cohesion: 0.10
Nodes (24): Adjustment, test_call_if_present_true_and_false_branches(), test_first_attr_falls_back_when_modern_missing(), test_first_attr_prefers_modern_name(), CompatDialog, make_spin_row(), make_switch_row(), make_toolbar() (+16 more)

### Community 23 - "install.sh"
Cohesion: 0.25
Nodes (17): detect_pkg_family(), ensure_path_hint(), flatpak_hint(), install_app_files(), install_deps_apk(), install_deps_apt(), install_deps_dnf(), install_deps_pacman() (+9 more)

### Community 29 - "CircularGauge"
Cohesion: 0.08
Nodes (10): DrawingArea, CircularGauge, CoreBars, MetricRow, Any, Compact per-core CPU usage bars., Simple sparkline chart for recent metric history., Simple key/value metric row. (+2 more)

### Community 38 - "core/legal.py"
Cohesion: 0.36
Nodes (7): copyright_line(), _extract_lang(), legal_markdown(), _legal_paths(), Path, test_copyright_line(), test_legal_markdown_fr_en()

### Community 44 - "MainWindow"
Cohesion: 0.07
Nodes (8): Application, ActionListRow, apply_app_css(), Button, Adw.ActionRow with a trailing action button., MainWindow, Any, Widget

### Community 46 - "build-flatpak.sh"
Cohesion: 0.48
Nodes (5): builder(), need(), run_builder(), build-flatpak.sh script, validate_metadata()

### Community 47 - "LANCER.sh"
Cohesion: 0.53
Nodes (5): need_pkg(), pause(), PYTHONPATH, PYTHONUNBUFFERED, LANCER.sh script

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

### Community 64 - "Hub Réseau 2.0 — design"
Cohesion: 0.22
Nodes (8): 1. Console live in-app (paquets), 2. Cliché avant le risque, 3. Score santé, 4. Flathub, Fichiers, Hors 2.0.0, Hub Réseau 2.0 — design, Non-négociable

### Community 65 - "Conditions d'utilisation — Hub Réseau"
Cohesion: 0.25
Nodes (7): 1. Objet, 2. Licence, 3. Aucune installation automatique, 4. Responsabilité, 5. Soutien facultatif, 6. Droit applicable, Conditions d'utilisation — Hub Réseau

### Community 66 - "Français"
Cohesion: 0.11
Nodes (17): Conditions d’utilisation (CGU), Legal notice — Hub Réseau, Mentions légales — Hub Réseau, Privacy (GDPR), Terms of use, Vie privée (RGPD), Ce que ça fait, Ce que ça ne fait pas (+9 more)

### Community 69 - "Global Constraints"
Cohesion: 0.33
Nodes (5): Global Constraints, Hub Réseau 2.0 Implementation Plan, Task 1: health + jobs (tests d’abord), Task 2: job console + wire packages + snapshot + dashboard, Task 3: docs + 2.0.0 ship

### Community 70 - "Vie privée / RGPD — Hub Réseau"
Cohesion: 0.33
Nodes (5): Collecte par l'éditeur, Données locales, Droit applicable, Réseau, Vie privée / RGPD — Hub Réseau

## Knowledge Gaps
- **45 isolated node(s):** `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH`, `PYTHONUNBUFFERED`, `version` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MainWindow` connect `MainWindow` to `shell.py`, `t`, `main_window.py`, `main.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Why does `t()` connect `t` to `which`, `main_window.py`, `adapters.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `show_toast()` connect `t` to `main_window.py`, `adapters.py`, `MainWindow`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MainWindow` (e.g. with `HubReseauApp` and `ActionListRow`) actually correct?**
  _`MainWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `INSTALLER-RACCOURCI-FLATPAK.sh script`, `INSTALLER-RACCOURCI.sh script`, `PYTHONPATH` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `shell.py` be split into smaller, more focused modules?**
  _Cohesion score 0.061971830985915494 - nodes in this community are weakly interconnected._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07219548315438726 - nodes in this community are weakly interconnected._