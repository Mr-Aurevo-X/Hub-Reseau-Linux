<!-- lang:fr -->
# Mentions légales — Hub Réseau

**Copyright © 2026 Mr-Aurevo-X.** Tous droits réservés sur le nom, les marques et les visuels.

Le code source est un logiciel libre sous licence [GPL-3.0-or-later](LICENSE).

## Conditions d’utilisation (CGU)

1. Hub Réseau est un utilitaire réseau **local-first** pour Linux (GTK 4 / libadwaita).
2. Le logiciel est fourni « en l’état », sans garantie d’aucune sorte (GPL §15–16).
3. Vous êtes seul responsable des sondes, pings et diagnostics que vous lancez.
4. Usage autorisé : personnel ou professionnel sur des systèmes que vous administrez légitimement.
5. Toute copie ou redistribution doit respecter la GPL-3.0-or-later.
6. Pas d’installation automatique : la vérif. GitHub n’affiche que des commandes à copier-coller.

## Vie privée (RGPD)

Mr-Aurevo-X **ne collecte aucune donnée personnelle**. Pas de compte, pas de télémétrie, pas de publicité, pas de revente.

- Stockage local : `~/.config/Mr-Aurevo-X/hubs/reseau/` (préférences, parc).
- **Vérif. versions au démarrage** (Préférences, activée par défaut, désactivable) : GET `api.github.com/repos/Mr-Aurevo-X/Hub-Reseau-Linux/releases` (lecture seule). GitHub peut voir IP / User-Agent selon **sa** politique.
- **Connexions :** lecture locale de la table de sockets (`ss`). Adresses et ports restent sur votre disque. **Aucun envoi**, pas de reverse DNS, pas de réputation en ligne.
- **Diag :** au chargement de la page, ping (défaut `1.1.1.1`), DNS (`github.com`, `flathub.org`) et traceroute / mtr depuis cette machine.
- **Parc :** machines que **vous** saisissez. Sondes TCP / ICMP sur action. Pas de mot de passe stocké, pas d’agent distant.
- Dons : Discord / PayPal / Revolut, sur clic.

Droit belge.

Contact : dépôt `Mr-Aurevo-X/Hub-Reseau-Linux`.

<!-- lang:en -->
# Legal notice — Hub Réseau

**Copyright © 2026 Mr-Aurevo-X.** All rights reserved on the name, marks, and artwork.

Source code is free software under [GPL-3.0-or-later](LICENSE).

## Terms of use

1. Hub Réseau is a **local-first** Linux network utility (GTK 4 / libadwaita).
2. The software is provided “as is”, without warranty of any kind (GPL §§15–16).
3. You are solely responsible for the probes, pings, and diagnostics you run.
4. Permitted use: personal or professional on systems you legitimately administer.
5. Any copy or redistribution must follow GPL-3.0-or-later.
6. No automatic installer: the GitHub check only shows copy-paste commands.

## Privacy (GDPR)

Mr-Aurevo-X **collects no personal data**. No account, no telemetry, no ads, no resale.

- Local storage: `~/.config/Mr-Aurevo-X/hubs/reseau/`
- **Startup version check** (Preferences, on by default, can be disabled): GET `api.github.com/repos/Mr-Aurevo-X/Hub-Reseau-Linux/releases` (read-only). GitHub may see IP / User-Agent under **its** policy.
- **Connections:** local read of this machine’s socket table (`ss`). No upload, no reverse DNS, no online reputation.
- **Diag:** on page load, ping (default `1.1.1.1`), DNS (`github.com`, `flathub.org`), and traceroute / mtr from this machine.
- **Fleet:** machines **you** enter. TCP / ICMP probes on action. No stored passwords, no remote agent.
- Donate links on click.

Belgian law.

Contact: repo `Mr-Aurevo-X/Hub-Reseau-Linux`.
