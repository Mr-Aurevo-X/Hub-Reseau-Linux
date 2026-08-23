# Vie privée / RGPD — Hub Réseau

Éditeur : Mr-Aurevo-X  
Produit : Hub Réseau

## Collecte par l'éditeur

Aucune. Pas de télémétrie, pas de compte, pas de tracker. Mr-Aurevo-X ne reçoit aucune donnée personnelle via cette application.

## Données locales

Préférences et caches : `~/.config/Mr-Aurevo-X/hubs/reseau/`

Vous pouvez supprimer ce dossier à tout moment.

## Réseau

- **Vérif. versions au démarrage** (Préférences, **activée par défaut**, désactivable) : GET `api.github.com/repos/Mr-Aurevo-X/Hub-Reseau-Linux/releases` (lecture seule). GitHub peut voir IP / User-Agent selon sa politique.
- **Page Diag** : au chargement, ping (hôte par défaut `1.1.1.1`), DNS (`github.com`, `flathub.org`) et traceroute / mtr. Ce n'est pas de la télémétrie éditeur : les paquets partent de votre machine vers ces hôtes.
- **Parc** : sondes TCP / ICMP vers les adresses que **vous** saisissez, sur action (ping tuile / barre).
- **Page Connexions** : lecture locale de la table de sockets (`ss`). Pas d'envoi, pas de reverse DNS, pas de réputation en ligne.
- **Dons / liens externes** : uniquement sur clic.

Pas de cookies posés par l'éditeur.

## Droit applicable

RGPD et droit belge.
