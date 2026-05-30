# 04 — Nettoyage et mise à jour des dépendances

Audit dépendance par dépendance (`requirements/base.txt`, `dev.txt`, `prod.txt`). Statut :
**GARDER** / **RETIRER** / **METTRE À JOUR** / **REMPLACER**.

## requirements/base.txt

| Paquet | Version | Statut | Justification / action |
|--------|---------|--------|------------------------|
| `Django` | 5.2.14 | **GARDER** | Cœur. Suivre les patches de la série 5.2 LTS. |
| `django-admin-sortable` (fork git) | — | **GARDER** | `SortableMixin`/`SortableForeignKey` (music, tracker). ⚠️ C'est un **fork git** (`LEAGUEDORA`) → fragile. Surveiller, envisager une alternative maintenue (`django-admin-sortable2`). |
| `django-anymail` | 13.0 | **GARDER** | Backend Mailgun en prod (`prod.py`). |
| `django-autoslug` | 1.9.9 | **GARDER** | `AutoSlugField` (kendama, versus). |
| `django-avatar` | 8.0.1 | **RETIRER** | Non utilisé : `Profil.avatar` est un `ImageField` simple, aucune fonctionnalité avatar. |
| `django-bootstrap3` | 25.1 | **RETIRER** | Voir doc 2. À retirer **après** conversion des templates de formulaire (y compris kendama). |
| `django-colorfield` | 0.14.0 | **GARDER** | `ColorField` (tracker, smm, my_spot). |
| `django-cors-headers` | 4.7.0 | **GARDER** | CORS pour les frontends Vue externes. |
| `django-filter` | 25.1 | **GARDER** | `FilterView` (avis, music, kendama). |
| `django-fontawesome-6` | 1.0.0.0 | **GARDER** | `IconField` + icônes. Utile après suppression des glyphicons. |
| `django-geoposition-2` | 0.4.0 | **GARDER** | `GeopositionField` (avis.Structure, my_spot.Spot). Dépend de Google Maps JS. my_spot est conservé (effort minimal) → on garde. |
| `django-pandas` | 0.6.7 | **GARDER** | `read_frame` pour le resampling tracker. |
| `django-redis` | 5.2.0 | **RETIRER** | Aucun `CACHES` configuré, pas dans `INSTALLED_APPS`. Orphelin. |
| `django-select2` | 8.4.1 | **GARDER** | Widgets Select2 (versus, music, tracker, smm). Vérifier le fonctionnement sans jQuery global. |
| `django-simple-history` | 3.8.0 | **GARDER** | `HistoricalRecords` (music, kendama). Cœur de l'UX fréquence kendama. |
| `djangorestframework` | 3.16.0 | **GARDER** | API tracker + smm. |
| `djangorestframework-simplejwt` | 5.5.1 | **GARDER** | Auth JWT app mobile. |
| `google-api-python-client` | **1.12.11** | **METTRE À JOUR** | **2020, très vieux**. Utilisé pour l'API YouTube (`music/views.py`). Monter en 2.x et tester le fetch YouTube. |
| `pandas` | 2.2.3 | **GARDER** | Via django-pandas (tracker). Lourd mais nécessaire au resampling. |
| `Pillow` | 12.2.0 | **GARDER** | `ImageField` + **optimisation images** (doc 3). |
| `Pyrebase4` | 4.8.0 | **RETIRER** | Remplacé par `django-storages` + backend GCS (doc 3). Retirer après normalisation. |
| `django-storages[google]` | — | **AJOUTER** | Backend `GoogleCloudStorage` pour piloter le bucket Firebase existant (= bucket GCS). Tire `google-cloud-storage`. Voir doc 3. |
| `python-slugify` | 8.0.0 | **GARDER** | Slugs unicode (music). |
| `redis` | 4.5.4 | **GARDER** | ⚠️ Dépendance **transitive obligatoire de `spotipy`** (`Requires-Dist: redis>=3.5.3` ; `spotipy/cache_handler.py` fait `from redis import RedisError` à l'import). Le retirer casse l'import de `spotipy`. (Initialement listé « RETIRER » par erreur — corrigé Phase 1.) |
| `requests` | 2.33.0 | **GARDER** | Transitif (googleapiclient, spotipy) + utile au script de migration images. |
| `soundcloud` (fork git) | — | **REMPLACER / RETIRER (à terme)** | Fork git perso, **API SoundCloud dépréciée**. Évaluer si la fonctionnalité (followers, resolve) est encore utilisée/fonctionnelle ; sinon retirer. |
| `spotipy` | 2.25.2 | **GARDER** | OAuth + sync playlists Spotify (music). |
| `setuptools` | 80.9.0 | **GARDER** | Packaging. |
| `zipp` | >=3.21.0 | **GARDER** | Pin sécurité (Snyk). |
| `sqlparse` | >=0.5.0 | **GARDER** | Pin sécurité (Snyk). |
| `dnspython` | >=2.6.1 | **GARDER** | Pin sécurité (Snyk). |

## requirements/dev.txt

| Paquet | Statut | Action |
|--------|--------|--------|
| `coverage` 7.9.1 | **GARDER si on ajoute des tests** | Sinon retirer. Voir section tests ci-dessous. |
| `django-debug-toolbar` 5.2.0 | **GARDER** | Utile en dev (`dev.py`). |
| `pyright` | **GARDER si typage** | `pyrightconfig.json` présent. Sinon retirer. |

## Gains attendus

Retraits secs (sans risque) : `django-avatar`, `django-redis`. (`redis` finalement **conservé** :
dépendance transitive obligatoire de `spotipy`.)
Retraits après chantier : `django-bootstrap3` (doc 2), `Pyrebase4` (doc 3).
À évaluer : `soundcloud` (selon usage réel).

Cela retire des paquets et, surtout, **jQuery + Bootstrap CSS/JS** du front (doc 2) et le **SDK
Firebase JS** (doc 3) → c'est là que se trouve le plus gros gain de « bundle size ».

## Tests (recommandation transverse)

Les fichiers `tests.py` existent mais semblent quasi vides. Avant un gros refactor, il serait prudent
d'ajouter quelques **tests de smoke** (les vues principales renvoient 200, les API ne régressent pas).
`coverage` est déjà dans `dev.txt`. À discuter avec le propriétaire (hors périmètre strict mais
fortement conseillé pour sécuriser la refonte).

## Procédure de mise à jour sûre

1. Retraits secs d'abord (`django-avatar`, `django-redis`) + `pip install` + `check`. (`redis` est
   conservé : requis par `spotipy`.)
2. `google-api-python-client` → 2.x : tester le fetch YouTube de `music`.
3. Les retraits liés aux chantiers (bootstrap3, Pyrebase4) se font **dans** ces chantiers.
4. Mettre à jour `requirements/*.txt` ET, si besoin, `README.md` / `techstack.md` (obsolètes).
5. Re-générer un éventuel lock / vérifier le déploiement PythonAnywhere (`pip install -r prod.txt`).
</content>
