# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexte

Site personnel de Benbb96 (benbb96.com) : un projet Django 5.2 monolithique qui regroupe plusieurs
mini-applications indépendantes (avis, musique, trackers, kendama…). Le site est **bilingue FR/EN**
et l'UI comme les commentaires sont **en français** — écrire en français par défaut.

## Commandes

`manage.py` a `config.settings.prod` comme valeur par défaut : **toute commande locale doit forcer
les settings de dev**, sinon elle échoue sur `ImproperlyConfigured: Set the GCS_CREDENTIALS setting`.

```bash
export DJANGO_SETTINGS_MODULE=config.settings.dev   # ou en préfixe de chaque commande
uv sync                                             # installe .venv depuis uv.lock (prod + dev)
uv run python manage.py runserver
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run   # vérif de non-régression migrations
```

Un `secrets.json` à la racine est **obligatoire** même en dev (lu au chargement de
`config/settings/base.py`) : `SECRET_KEY`, `GOOGLE_API_KEY`, `SOUNDCLOUD_CLIENT_ID`,
`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`…

### Tests

Les `<app>/tests.py` sont des stubs vides. **Toute la suite est dans `smoke_tests.py`** à la racine
(27 tests : statuts 200 des vues publiques, redirections `login_required`, endpoints API tracker &
super_moite_moite, cycle JWT).

```bash
uv run python manage.py test smoke_tests                                   # toute la suite
uv run python manage.py test smoke_tests.TrackerAPITest                    # une classe
uv run python manage.py test smoke_tests.JWTAuthSmokeTest.test_token_obtain  # un test
```

### Qualité

```bash
uv run ruff check . --fix && uv run ruff format .   # lint + format Python
uv run pre-commit run --all-files                   # ruff + hygiène (installé via `pre-commit install`)
uv run djlint . --lint                              # rapport templates — voir avertissement ci-dessous
```

⚠️ **Ne jamais lancer `djlint --reformat`.** Une passe design a retravaillé les templates ; un
reformatage global entrerait en conflit avec d'éventuelles retouches restantes. djLint est
configuré en *rapport seul* (~95 erreurs connues, à traiter avec la passe design).

### i18n

Traductions dans `locale/{fr,en}/` (racine, seul `LOCALE_PATHS`) **et** dans `base/locale/`,
`avis/locale/`, `music/locale/` (récupérées automatiquement par app). `makemessages` lancé à la
racine n'écrit que dans `locale/` ; pour les catalogues d'app, lancer la commande **depuis le
dossier de l'app**.

```bash
uv run python manage.py makemessages -l fr --ignore .venv    # racine → locale/
uv run python manage.py compilemessages --ignore .venv       # .po → .mo (sans --ignore, recompile le venv)
```

Le serveur charge les `.mo` en mémoire au démarrage → **redémarrer après un `compilemessages`**
(d'autant plus si le serveur tourne en `--noreload`, cf. `.vscode/launch.json`).

### Médias

```bash
uv run python manage.py clean_orphan_media         # dry-run par défaut, --apply pour supprimer
```

À lancer **en settings prod** (en dev, `default_storage` est local alors que `MEDIA_URL` pointe sur
GCS : la commande listerait le disque local au lieu du bucket). Les commandes de migration
`normalize_photo_paths` et `optimize_existing_photos` ont été retirées une fois le lot existant
converti — l'optimisation à l'upload est assurée par `base/image_utils.py`.

## Architecture

### Settings et environnements

`config/settings/` éclaté en `base.py` / `dev.py` / `prod.py` (les deux derniers font `from .base
import *`). Différences structurantes :

- **prod** : `STORAGES` bascule sur `GoogleCloudStorage` (bucket Firebase = bucket GCS,
  `publicRead`), Anymail/Mailgun, durcissement sécurité.
- **dev** : `FileSystemStorage` local **mais** `MEDIA_URL` pointe vers le bucket GCS public → les
  images de la base de prod s'affichent sans credentials, en lecture seule ; un fichier uploadé en
  dev reste sur le disque local et **ne s'affichera pas**. C'est voulu.
- SQLite en dev **comme en prod**, mais `db.sqlite3` est **gitignoré** : la base locale et
  celle de prod sont deux fichiers indépendants. Une modification de données faite en local
  (ajout d'un projet, changement d'image…) ne part **pas** au déploiement — il faut la refaire
  côté prod, ou rapatrier le fichier de prod pour travailler sur les mêmes données.

### URLs et i18n

`config/urls.py` : quelques routes non localisées (API JWT, sitemap, robots, callback Spotify) puis
un bloc `i18n_patterns` où **les préfixes d'URL eux-mêmes sont traduits** (`path(_("review/"), …)`).
Conséquence : dans les tests et le code, reverser une URL nécessite la bonne locale active — voir le
helper `url()` de `smoke_tests.py` qui force `translation.override('fr')`.

### App `base` = socle partagé

- `PhotoAbstract` / `PhotoOptimizationMixin` (`base/models.py`) : classes de base des modèles
  porteurs d'image ; leur `save()` appelle `base/image_utils.py` qui **redimensionne à 1280 px et
  réencode en WebP** à l'upload. Tout nouveau modèle avec photo doit passer par là.
- `base/context_processors.py` : injecte `GOOGLE_ANALYTICS_KEY`, la clé Maps et les liens réseaux
  sociaux dans **tous** les templates.
- `base/ajax_middleware.py` : réinjecte `request.is_ajax()` (retiré de Django 4).
- `base/sitemap.py`, `base/templatetags/custom_tags.py`, `base/fields.py`, `base/widgets.py`.

### Les apps métier

`avis` (structures/produits/avis), `music` (playlists, artistes, morceaux ; intégrations Spotify /
SoundCloud / YouTube), `tracker` (compteurs + séries temporelles via pandas), `versus`
(joueurs/jeux/parties), `kendama` (tricks, combos, ladders), `my_spot` (spots géolocalisés,
abandonné), `super_moite_moite` (tâches colocation, front Vue.js embarqué).

### API

DRF + SimpleJWT, consommés par des clients **externes** : une app mobile et
`vue-trackers.onrender.com` (tracker), plus le Vue.js embarqué de `super_moite_moite`
(`tracker/serializers.py`, `super_moite_moite/api_views.py`/`serializers.py`). **Ne pas casser ces
contrats d'API** — les endpoints correspondants sont couverts par `smoke_tests.py`.

### Front-end : aucun build

Pas de `package.json`, pas de bundler, pas de framework CSS. Le JS est soit vanilla maison, soit
vendorisé dans `assets/js/` (Tom Select, Chart.js v4, minifiés). `assets/` est un `STATICFILES_DIRS`,
`collectstatic` écrit vers `static/`.

- **`assets/css/main.css`** (~1600 lignes) est le design system maison : tokens en custom
  properties, reset, composants. **En-tête du fichier = documentation à lire avant modification**
  (sommaire numéroté des sections, direction visuelle).
- **Namespace `.ds-*` obligatoire** pour tout composant (`.ds-btn`, `.ds-card`, `.ds-alert`,
  `.ds-nav`, `.ds-form`…). Convention héritée de la coexistence avec Bootstrap ; Bootstrap est
  parti mais la convention reste.
- **Direction visuelle** : jaune de marque `--ds-primary` **en accent uniquement** (fond + texte
  foncé `--ds-primary-ink` dessus) — jamais de texte ni de lien jaune (contraste). `--ds-warning`
  est volontairement ambre/orange pour ne pas se confondre avec le jaune de marque.
- **Dark mode** complet via `[data-theme]` + `@media (prefers-color-scheme)`. Toggle
  clair/sombre/auto dans la navbar (`assets/js/theme.js`, persistance localStorage) + script inline
  anti-FOUC dans `<head>` de `templates/base.html` (**doit rester inline et synchrone**).
- `assets/js/http.js` expose `window.http` (helper `fetch` + CSRF) et un shim `window.Cookies`.
- Chrome global : `templates/base.html`, `navbar.html`, `footer.html`, `components/`
  (`form.html`, `messages.html`, `pagination.html`).

### ⚠️ kendama est un cas à part

`kendama` n'utilise **pas** `templates/base.html` : elle a son propre layout
(`kendama/templates/kendama/base.html`) et son thème « paper » autonome
(`kendama/static/kendama/css/paper.css`, polices manuscrites, bordures ondulées, modales en
checkbox-hack CSS). **Elle doit rester visuellement identique** — pas de dark mode, pas de `.ds-*`,
pas de réécriture de son JS. Contrat détaillé dans `docs/kendama-a-preserver.md`.

## Dépendances

Source de vérité unique : **`pyproject.toml` + `uv.lock`** (plus de `requirements/*.txt`). Pour
ajouter/bumper : éditer `pyproject.toml`, lancer `uv lock`, committer le lock. Deux dépendances sont
des forks git (`[tool.uv.sources]`), et `redis` est conservé uniquement parce que `spotipy`
l'importe au chargement.

## Déploiement

Push sur `main` → `.github/workflows/deploy-to-pythonanywhere.yml` (SSH) → `git pull`,
`uv sync --frozen --no-dev` dans `~/.virtualenvs/benbb96`, `migrate`, `collectstatic`, `touch wsgi`.
Aucune étape de build front. Le venv Web tab de PythonAnywhere (`~/.virtualenvs/benbb96`) est ciblé
via `UV_PROJECT_ENVIRONMENT` ; `uv` doit être installé sur le serveur.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** : vue d'ensemble (stack, apps, design system, déploiement).
- **[docs/kendama-a-preserver.md](docs/kendama-a-preserver.md)** : contrat de préservation du thème
  « paper » de kendama.
- Les docs détaillées de pilotage de la **refonte 2026** (roadmap, décisions, checklists de mise en
  prod, backlog design) sont conservées **en local uniquement** sous `docs/refonte/` (gitignoré) —
  utiles au propriétaire et aux agents, hors dépôt public.

## Conventions de commit

Conventional commits **en français** : `feat(design): …`, `fix(avis): …`, `docs(refonte): …`.
Ne **pas** ajouter de trailer `Co-Authored-By`. Ne **pas** utiliser le skill `/commit` sur ce projet
(préférences du propriétaire).
