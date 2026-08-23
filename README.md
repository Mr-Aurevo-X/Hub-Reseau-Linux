# Hub Réseau

> **WIP** — encore en développement. Pas une release publique.  
> **WIP** — still in development. Not a public release.

Hub réseau **local-first** pour Linux (GTK 4 / libadwaita).  
Interfaces, trafic, parc d’atelier, scan LAN privé, diagnostic à la demande, VPN / WireGuard NetworkManager.

**1.3.0** — [releases](https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases)

---

## Français

### Installer (Flatpak)

Prérequis : [Flatpak](https://flatpak.org/setup/) + runtime GNOME 49 (installé automatiquement depuis Flathub au premier `flatpak install`).

```bash
wget -O org.mraurevox.HubReseau.flatpak \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/latest/download/org.mraurevox.HubReseau.flatpak
flatpak install --user -y --reinstall ./org.mraurevox.HubReseau.flatpak
wget -O INSTALLER-RACCOURCI-FLATPAK.sh \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/latest/download/INSTALLER-RACCOURCI-FLATPAK.sh
bash ./INSTALLER-RACCOURCI-FLATPAK.sh
flatpak run org.mraurevox.HubReseau
```

### Installer (natif, clone)

```bash
bash install.sh --skip-deps
hub-reseau
```

Dev sans installer : `bash LANCER.sh`

### Ce que ça fait

- Adaptateurs, route, DNS (stub systemd vs serveurs amont)
- Wi-Fi / Bluetooth / table des connexions (`ss`)
- Parc : machines que vous saisissez, sondes TCP / ICMP
- Scan LAN **privé** (voisins, passerelle, MAC ; option ping /24)
- Diagnostic à la demande (ping, DNS, traceroute / mtr)
- VPN / WireGuard : activer ou couper un profil NetworkManager existant

### Ce que ça ne fait pas

Pas de nmap, pas de Wake-on-LAN, pas de création de profil VPN, pas de télémétrie, pas d’install automatique.  
Pas de publication Flathub : le canal, c’est **cette** release GitHub.

### Confidentialité

Local-first. Données dans `~/.config/Mr-Aurevo-X/hubs/reseau/`.  
Vérif. versions GitHub au démarrage (désactivable). Scan / diag / parc : trafic seulement quand vous cliquez.  
Texte : [LEGAL.md](LEGAL.md) — dans l’app : mentions légales du kit.

---

## English

Local-first Linux network hub (GTK 4 / libadwaita): adapters, fleet, private LAN scan, on-demand diagnostics, NetworkManager VPN / WireGuard up/down.

### Install (Flatpak)

```bash
wget -O org.mraurevox.HubReseau.flatpak \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/latest/download/org.mraurevox.HubReseau.flatpak
flatpak install --user -y --reinstall ./org.mraurevox.HubReseau.flatpak
wget -O INSTALLER-RACCOURCI-FLATPAK.sh \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/latest/download/INSTALLER-RACCOURCI-FLATPAK.sh
bash ./INSTALLER-RACCOURCI-FLATPAK.sh
flatpak run org.mraurevox.HubReseau
```

### Install (native clone)

```bash
bash install.sh --skip-deps
hub-reseau
```

Dev without install: `bash LANCER.sh`

No nmap, no WOL, no VPN profile creation, no telemetry, no auto-install.  
Not on Flathub — GitHub Releases only.

Privacy: local-first. Data under `~/.config/Mr-Aurevo-X/hubs/reseau/`. Startup GitHub version check (can be disabled). See [LEGAL.md](LEGAL.md).

---

Copyright © 2026 Mr-Aurevo-X — GPL-3.0-or-later
