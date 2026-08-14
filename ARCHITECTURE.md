# Architecture

Site personnel de Benbb96 : un projet **Django 5.2** monolithique qui regroupe plusieurs
mini-applications indépendantes. Bilingue **FR/EN**, sans étape de build front, déployé sur
PythonAnywhere.

## Stack

- **Backend** : Django 5.2, Python 3.13 (prod), **SQLite** (dev et prod).
- **Front** : **design system CSS maison** (custom properties, flexbox/grid, `<dialog>`, `:has()`) —
  **sans framework** (pas de Bootstrap) ni **jQuery**, pas de bundler. Dark mode complet.
- **JS** : vanilla. [Tom Select](https://tom-select.js.org/) (selects searchable), Chart.js v4
  (graphes), un helper `fetch`+CSRF maison (`window.http`). Dates via `Intl` natif.
- **Images** : `ImageField` Django + [`django-storages`](https://django-storages.readthedocs.io/)
  sur **Google Cloud Storage** ; optimisation Pillow (redimensionnement + WebP) à l'upload.
- **API** : Django REST Framework + SimpleJWT (consommée par des clients externes — app mobile,
  front Vue).
- **Outillage** : [`uv`](https://docs.astral.sh/uv/) (deps + venv, `pyproject.toml` + `uv.lock`),
  `ruff` (lint + format), `pre-commit`.
- **Déploiement** : push sur `main` → GitHub Actions (SSH) → `git pull` + `uv sync --frozen --no-dev`
  + `migrate` + `collectstatic` + reload WSGI. Aucune étape de build front.

## Applications

| App | Rôle |
|-----|------|
| `base` | Socle partagé : home, profils, pages vitrines, jeu Labyrinthe (p5.js), modèles/mixins communs |
| `avis` | Avis sur produits & structures (géolocalisées), photos |
| `music` | Catalogue musical (artistes, titres, playlists), intégrations Spotify / SoundCloud / YouTube |
| `tracker` | Suivi de séries temporelles (événements/mesures), graphes ; **API DRF** (app mobile + front Vue) |
| `versus` | Suivi de parties entre joueurs, classements |
| `super_moite_moite` | Suivi de tâches en colocation ; **API DRF** + composant Vue.js embarqué |
| `kendama` | Tricks / combos / ladders de kendama, suivi de fréquence (historique) |
| `my_spot` | Carte de « spots » géolocalisés (Google Maps) |

### `base` : le socle
- `Profil` (extension `User`), `Projet` (cartes de la home + contrôle d'accès), `LienReseauSocial`.
- `PhotoAbstract` / `PhotoOptimizationMixin` (`base/models.py`, `base/image_utils.py`) : tout modèle
  porteur d'image redimensionne à 1280 px et réencode en WebP à l'upload.
- `base/context_processors.py` : injecte clés analytics/maps + liens réseaux sociaux dans tous les templates.

## Front-end : le design system

- **`assets/css/main.css`** : tokens en custom properties (couleurs, typo, espacements), reset,
  composants **namespacés `.ds-*`** (`.ds-btn`, `.ds-card`, `.ds-nav`, `.ds-alert`, `.ds-form`…).
  L'en-tête du fichier documente les sections et la direction visuelle.
- **Direction visuelle** : jaune de marque en **accent** (fond + texte foncé dessus), neutres chauds.
- **Dark mode** : via `[data-theme]` + `@media (prefers-color-scheme)`, toggle clair/sombre/auto dans
  la navbar (persisté en `localStorage`, script anti-FOUC inline).

## Réglages & environnements

`config/settings/` éclaté en `base.py` / `dev.py` / `prod.py`. Secrets dans `secrets.json`
(hors dépôt). En prod : stockage media sur GCS, Anymail/Mailgun, durcissement sécurité. En dev :
stockage fichiers local.

## Cas particulier : kendama

L'app `kendama` possède son **propre thème « paper »** autonome (polices manuscrites, layout dédié),
**volontairement préservé** et hors du design system `.ds-*` / du dark mode. Contrat de préservation :
[docs/kendama-a-preserver.md](docs/kendama-a-preserver.md).

## Contribuer / lancer en local

```bash
uv sync
export DJANGO_SETTINGS_MODULE=config.settings.dev
uv run python manage.py migrate
uv run python manage.py runserver
uv run python manage.py test smoke_tests   # suite de smoke tests
```

Un `secrets.json` à la racine est requis même en dev (voir `config/settings/base.py`).
</content>
