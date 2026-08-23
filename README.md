# Hub Réseau

> **WIP** — encore en développement.  
> **WIP** — still in development.

Hub réseau **local-first** pour Linux (GTK 4 / libadwaita).  
Interfaces, trafic, parc d’atelier, scan LAN privé, diagnostic à la demande, VPN / WireGuard NetworkManager.

**1.3.5** — [releases](https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases) · GPL-3.0-or-later · © 2026 Mr-Aurevo-X

---

## Français

### Installer (Flatpak)

Prérequis : [Flatpak](https://flatpak.org/setup/) + runtime GNOME 49 (installé automatiquement depuis Flathub au premier `flatpak install`).

```bash
rm -f org.mraurevox.HubReseau.flatpak
wget --no-continue -O org.mraurevox.HubReseau.flatpak \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/v1.3.5/org.mraurevox.HubReseau.flatpak
flatpak install --user -y --reinstall ./org.mraurevox.HubReseau.flatpak
wget --no-continue -O INSTALLER-RACCOURCI-FLATPAK.sh \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/v1.3.5/INSTALLER-RACCOURCI-FLATPAK.sh
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
rm -f org.mraurevox.HubReseau.flatpak
wget --no-continue -O org.mraurevox.HubReseau.flatpak \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/v1.3.5/org.mraurevox.HubReseau.flatpak
flatpak install --user -y --reinstall ./org.mraurevox.HubReseau.flatpak
wget --no-continue -O INSTALLER-RACCOURCI-FLATPAK.sh \
  https://github.com/Mr-Aurevo-X/Hub-Reseau-Linux/releases/download/v1.3.5/INSTALLER-RACCOURCI-FLATPAK.sh
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

## Soutien (optionnel) / Support (optional)

Si le boulot te plaît, un café — sinon profite.  
If you like the work, a coffee — otherwise just enjoy it.

[![Discord](https://img.shields.io/badge/Discord-Mr--Aurevo--X-5865F2?style=for-the-badge&logo=discord&logoColor=white&labelColor=050807)](https://discord.com/users/406891052516114442)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-39ff14?style=for-the-badge&logo=paypal&logoColor=00f0ff&labelColor=050807)](https://www.paypal.com/paypalme/aurevo1)
[![Revolut](https://img.shields.io/badge/Revolut-mr__aurevo__x-00f0ff?style=for-the-badge&logo=revolut&logoColor=39ff14&labelColor=050807)](https://revolut.me/mr_aurevo_x)

---

Copyright © 2026 Mr-Aurevo-X — GPL-3.0-or-later
