# 05 — Roadmap phasée

Ordre d'exécution conseillé, pensé pour livrer par incréments **déployables** et limiter les risques.
Chaque phase peut être confiée à un agent distinct avec le document de chantier correspondant.

## Phase 0 — Filet de sécurité (recommandé avant tout)

- Sauvegarder `db.sqlite3` et les images (export Firebase) avant toute migration.
- Ajouter quelques **tests de smoke** (status 200 des vues clés, non-régression des endpoints API
  tracker & smm). Sécurise toutes les phases suivantes.
- Vérifier l'environnement : `python manage.py check`, `makemigrations --check --dry-run`.

## Phase 1 — Nettoyage sec des dépendances (doc 4)

- Retirer `django-avatar`, `django-redis`. (`redis` finalement conservé : dépendance transitive
  obligatoire de `spotipy` — voir doc 4.)
- Mettre à jour `google-api-python-client` (1.12.11 → 2.x) et tester le fetch YouTube (music).
- **Faible risque, gain immédiat.** Déployable seul.

## Phase 2 — Modernisation du stockage d'images (doc 3)

> Indépendant du chantier front. Peut tourner en parallèle de la Phase 3.

**Décision actée** : on garde le bucket **Firebase = GCS** existant, mais via `django-storages`
(backend `GoogleCloudStorage`) + `ImageField` standard + optimisation **Pillow** (resize + WebP) à la
sauvegarde. Gratuit, images existantes en place, disque PythonAnywhere plus jamais sollicité.

1. Ajouter/config `django-storages[google]` + credentials compte de service GCS (dans `secrets.json`).
2. `PhotoAbstract` : `ImageField` sur storage GCS + `photo_url` rétrocompatible + optimisation Pillow.
3. Remplacer `FirebaseUploadWidget` par un upload serveur standard dans les 4 `forms.py`.
4. Adapter les templates d'affichage des photos (retrait du JS Firebase).
5. Management command de **normalisation** des chemins (les fichiers ne bougent pas du bucket), testée
   sur copie de prod.
6. Déployer code → normaliser en prod → vérifier → retirer Pyrebase4 + SDK Firebase JS + config exposée.

## Phase 3 — Front : design system + layout global (doc 2) — ✅ FAITE

1. ✅ Design system CSS maison (`assets/css/main.css` : tokens, reset, base, layout, composants `.ds-*`).
2. ✅ Chrome global réécrit : `base.html`, `navbar.html`, `footer.html` (menu mobile sans JS, footer
   social `.ds-social`).
3. ✅ Composants `components/form.html` (prêt, branché en Phase 4), messages Django en `.ds-alert`
   (`components/messages.html`), `components/pagination.html` restylé `.ds-pagination`.
4. ✅ Helper `fetch` + CSRF (`assets/js/http.js`, `window.http`). Le `$.ajaxSetup` jQuery est
   **conservé** pour music/tracker jusqu'à leur migration (Phase 4) ; retiré ensuite.

**Stratégie de coexistence retenue** (détail en doc 2) : namespace `ds-` pour tous les composants
maison (aucune classe Bootstrap redéfinie) ; `main.css` chargé en dernier (les sélecteurs d'éléments
modernisent le rendu « nu », les classes Bootstrap gardent la priorité sur les pages d'app) ; JS
ajouté sans rien retirer. Validé : `check` OK, `makemigrations --check` sans changement, 27 smoke
tests OK, pages home/profil/login/signup/listes d'app servies en 200 avec Bootstrap encore actif.

> ⚠️ **Bootstrap et jQuery restent chargés** pendant toute la transition (Phases 3 → 4). Les
> templates des apps utilisent encore les classes Bootstrap : les retirer maintenant casserait
> toutes les pages non migrées. Leur **retrait définitif se fait en Phase 5**, une fois la Phase 4
> terminée. Le design system de la Phase 3 doit donc **coexister** avec Bootstrap (éviter de
> redéfinir de façon destructive les classes Bootstrap encore utilisées : `.btn`, `.row`, `.col-*`,
> `.container`, `.panel`, `.alert`… — préférer des sélecteurs d'éléments + de nouvelles classes, ou
> un préfixe). Le site doit rester **fonctionnel et déployable** après la Phase 3.

## Phase 4 — Migration des templates app par app (doc 2) — ✅ FAITE

Tous les groupes sont migrés vers le design system `.ds-*` (1 commit par groupe). Plus aucune
classe Bootstrap ni `{% bootstrap_* %}` dans les templates des apps (vérifié par grep). Validé après
chaque groupe : `check` OK, `makemigrations --check` sans changement, 27 smoke tests OK.

1. ✅ `registration/` (login, signup) + `base` (home, profils, about, gallery, rallye, labyrinthe).
   Carousel galerie Bootstrap → `.ds-carousel` (CSS scroll-snap).
2. ✅ `avis`, `versus`. Carousel avis, tables, progress, breadcrumb, score → `.ds-*`.
3. ✅ `music` : tous templates + AJAX `.platformLink`/`.synchronize` `$.post` → **`window.http`**
   (fetch). Collapses Bootstrap → `<details>`. **select2 / DataTables conservés** (jQuery gardé
   jusqu'en Phase 5).
4. ✅ `tracker` : modale Bootstrap → `<dialog>` natif (`.ds-modal`), onglets `nav-tabs` → `.ds-tabs`
   + contrôleur vanilla dans `common.js`, `.hidden` → `.ds-hidden`, fréquence active `btn-primary`
   → `is-active`, glyphicons → FA6. **moment.js + bootstrap-daterangepicker + Chart.js v2
   CONSERVÉS** (remplacement par `Intl`/`Date`/Chart v4 reporté en Phase 5, écran fonctionnel) ;
   l'AJAX tracks/stats reste en `$.ajax` jQuery pour l'instant.
5. ✅ `super_moite_moite` : **enveloppe Django uniquement** (list, form, delete, boutons du jumbotron
   du detail) → `.ds-*`. ⚠️ **Composant Vue.js embarqué** (`<div id="app">` : `progress-bar`,
   `panel`, `modal`, `nav-pills`, `bootstrapClassColors`, etc.) **laissé tel quel** — il dépend
   encore de Bootstrap (CSS chargé globalement). À traiter séparément en Phase 5.
6. ✅ `my_spot` : migration cosmétique (carousels photos → `.ds-carousel`, grilles/tables/badges →
   `.ds-*`) + **`request.is_ajax()` corrigé** dans `views.py` →
   `request.headers.get('x-requested-with') == 'XMLHttpRequest'`. JS Google Maps / `$.get` conservé.
7. ✅ `kendama` : **uniquement** retrait de `{% bootstrap_form %}` / `{% load bootstrap3 %}` des 4
   formulaires (doc 6), via le nouveau partial `kendama/components/paper_form.html` (rendu
   `.form-group` paper, à l'identique visuellement). Thème paper, JS fetch, modales, formsets intacts.

**Reste à faire avant/pendant la Phase 5** (Bootstrap/jQuery encore chargés via `base.html`) :
- Composant Vue de `super_moite_moite` (dépend de Bootstrap CSS).
- `tracker` : remplacement moment.js + daterangepicker → `Intl`/`Date` + `<input date>`, Chart.js → v4,
  et conversion de l'AJAX jQuery restant en `window.http`.
- `music` : select2 (charge son propre jQuery) et DataTables (plugin jQuery) à arbitrer.

## Phase 5 — Suppression de Bootstrap & jQuery (doc 2)

- Une fois **tous** les `{% bootstrap_* %}` éliminés (apps + kendama) :
  retirer `django-bootstrap3` de `INSTALLED_APPS` + requirements, supprimer le CDN Bootstrap,
  `bootstrap-social.css`, et le jQuery global.
- **Supprimer `moment-with-locales.js` (541 Ko) + `bootstrap-daterangepicker`** : remplacés par
  `Intl.DateTimeFormat` / `Intl.RelativeTimeFormat` / `Date` natifs (fait en Phase 4 sur tracker &
  super_moite_moite). Monter **Chart.js → v4**. Pas de Temporal (non fiable en natif début 2026).

## Phase 6 — Finitions

- Évaluer `soundcloud` (fork git, API dépréciée) → garder ou retirer (doc 4).
- Mettre à jour `README.md` et régénérer/supprimer `techstack.md`/`techstack.yml` (obsolètes :
  mentionnent encore Bootstrap, Redis, etc.).
- Revue d'accessibilité / Lighthouse / poids des pages.
- Nettoyer le code mort éventuel des apps abandonnées.

## Phase 7 — Amélioration progressive avec htmx (étape finale)

> Étape **finale**, une fois le front modernisé (Bootstrap retiré, design system en place).
> On **refait le tour de l'appli** pour identifier les interactions qui gagneraient à se faire
> **sans rechargement de page**, et on les enrichit progressivement avec
> [htmx](https://htmx.org/) (petite lib, pas de build, philosophie « HTML over the wire »).

**Principe.** htmx complète le design system maison sans le remplacer : on garde des vues Django
qui renvoient des **fragments HTML** (includes existants), et les attributs `hx-*` les injectent
dans la page. Amélioration progressive : sans JS, les formulaires continuent de fonctionner en
POST classique (full reload) — htmx n'est qu'une surcouche.

**Cibles candidates (à confirmer pendant le tour de l'appli) :**
- **Tracker — liste** (`tracker_list.html`) :
  - Créer un **tracker** via le formulaire en bas sans recharger : `hx-post` → la vue renvoie la
    nouvelle carte, `hx-target` sur la grille (`hx-swap="beforeend"`), reset du formulaire.
  - **Ajout rapide d'un track** (bouton « + » des cartes) : `hx-post` vers `tracker_quick_add`,
    mise à jour en place du compteur + de la date du dernier track (renvoyer le fragment de carte).
- **super_moite_moite** : validation/ajout de tâches sans reload (en complément du composant Vue
  existant, ou en remplacement progressif si on veut retirer Vue à terme — à décider).
- **music / avis / versus** : ajout d'éléments en ligne (liens de plateforme, avis, parties)
  actuellement en `$.ajax` jQuery → bons candidats pour passer à htmx en supprimant le JS maison.
- **Filtres / pagination** des listes (`avis`, `music`) : navigation `hx-get` + `hx-push-url`
  pour filtrer/paginer sans reload complet.

**Méthode.**
1. Refaire le tour des pages app par app, lister les interactions « POST → reload complet » ou
   « `$.ajax` jQuery » et noter le gain UX de leur passage en htmx.
2. Ajouter htmx (CDN ou static local, ~14 Ko) dans `base.html`.
3. Adapter les vues concernées pour renvoyer un **fragment** quand la requête vient de htmx
   (`request.headers.get('HX-Request')`), sinon la page complète.
4. Réutiliser les includes existants comme fragments (ex. une carte tracker isolée dans son include).
5. Conserver le **fallback sans JS** (le `<form method="post">` doit rester fonctionnel).
6. Rejouer les smoke tests + vérifier les en-têtes CSRF (htmx envoie le token via le header géré
   par `window.http`/le middleware).

**Dépendances :** se fait **après** la Phase 5 (front nettoyé). Peut réutiliser le helper
`window.http` et le rendu de fragments. Indépendant des Phases 1/2.

## Phase 8 — Internationalisation : traduction complète EN (étape finale)

> Objectif : **site entièrement traduit en anglais**. Aujourd'hui le site est bilingue FR/EN mais
> la couverture est **partielle** et la pipeline `.po`/`.mo` mérite d'être consolidée.

**État des lieux i18n (au moment de la rédaction) :**
- `LANGUAGE_CODE = 'fr'`, `LANGUAGES = [fr, en]`, `LOCALE_PATHS = (BASE_DIR/locale,)`,
  `LocaleMiddleware` actif, URLs sous `i18n_patterns`, sélecteur de langue (`set_language`) dans la navbar.
- Catalogues `.po`/`.mo` présents pour : **projet (`locale/`), `base`, `music`, `avis`** (fr + en).
- **Apps sans dossier `locale/`** (leurs chaînes ne sont donc pas collectées proprement) :
  **`tracker`, `versus`, `super_moite_moite`, `my_spot`, `kendama`**.
- **Beaucoup de texte en dur en français** non enveloppé dans `{% trans %}`/`{% blocktrans %}` ni
  `gettext`, y compris dans les templates retravaillés en Phase 3+ (ex. `tracker_list.html` :
  « Mes trackers », « Comparer des trackers », « Créer un nouveau tracker », « track/tracks »,
  « aucun track », « Ajouter un track rapidement » ; `components/pagination.html` : « Objets … résultats »).

**Travail à faire :**
1. **Audit de couverture** : repérer toutes les chaînes visibles non internationalisées
   (templates + Python : messages `messages.add_message`, `verbose_name`, `help_text`, libellés de
   formulaires, exceptions affichées…). Les envelopper dans `{% trans %}`/`{% blocktrans %}` (templates)
   et `gettext`/`gettext_lazy` (Python). Penser au pluriel (`{% blocktrans count %}`, `ngettext`).
2. **Créer les dossiers `locale/`** manquants pour `tracker`, `versus`, `super_moite_moite`,
   `my_spot`, `kendama` (ou centraliser dans `locale/` projet — décider d'une stratégie unique :
   per-app vs projet). Privilégier **une seule** approche pour simplifier la pipeline.
3. **Pipeline `.po`/`.mo`** :
   - Documenter et fiabiliser `makemessages` (langues, `--ignore` des dossiers `node_modules`/`.venv`/
     `static` tiers, `--no-obsolete` pour purger les entrées mortes, `--add-location=file` pour des
     diffs `.po` plus propres).
   - `compilemessages` à l'étape de build/déploiement (vérifier que le déploiement PythonAnywhere
     le lance, sinon l'ajouter au workflow GitHub Actions / script de deploy).
   - Décider si les `.mo` sont versionnés ou (re)générés au déploiement.
4. **Traduire** l'intégralité des entrées `msgstr` anglaises manquantes (relecture EN).
5. **Vérifs** : parcourir le site en `?lang=en` / via le sélecteur, contrôler qu'il ne reste **aucun
   texte français** ; cas des dates/nombres (`Intl` côté JS, `humanize`/`l10n` côté serveur :
   `naturaltime` etc. sont déjà localisés par `django.contrib.humanize`).
6. **Tests** : étendre les smoke tests pour charger quelques vues clés en `lang='en'` (le helper
   `url(..., lang=...)` existe déjà dans `smoke_tests.py`) et vérifier l'absence de chaînes FR
   témoins.

**Dépendances :** transverse, mais le plus efficace **après la Phase 4** (templates stabilisés, on ne
réécrit plus les chaînes) et idéalement **après la Phase 7** si htmx ajoute de nouveaux fragments à
traduire. Peut se faire en dernier, app par app.

## Phase 9 — Modernisation de l'outillage Python (DX)

> Indépendante du front (comme les Phases 1/2) : peut se faire à tout moment, idéalement **tôt** pour
> profiter du linter/formatter sur tout le reste du chantier. Objectif : outils **plus rapides et plus
> modernes** (écosystème Astral) pour la qualité et le confort de dev.

**État des lieux outillage :**
- Gestion des deps : `requirements/{base,dev,prod}.txt` (pip), dont **2 dépendances git forkées**
  (`django-admin-sortable`, `soundcloud`) et plusieurs **pins Snyk** de deps transitives.
- **Aucun** `pyproject.toml`, **aucun** linter/formatter/pre-commit configuré. Python 3.14.
- Déploiement PythonAnywhere : `pip install -r requirements/prod.txt` dans un virtualenv manuel
  (`~/.virtualenvs/benbb96`), via `.github/workflows/deploy-to-pythonanywhere.yml`.

**1. `uv` (remplace pip / virtualenv / pip-tools).**
- Migrer `requirements/*.txt` → `pyproject.toml` : `[project].dependencies` (prod) + groupes de deps
  dev (PEP 735 `[dependency-groups]` ou `optional-dependencies`). Générer un **`uv.lock`** versionné.
- Exprimer les **deps git** en sources uv (`[tool.uv.sources]` → `{ git = "…", rev/branch }`).
- Reporter les **pins Snyk** en contraintes (`[tool.uv] constraint-dependencies` / overrides) avec un
  commentaire sur la raison (vulnérabilité), pour ne pas les perdre.
- Épingler la version Python (`.python-version` + `uv python pin`).
- ⚠️ **Déploiement** : ne pas casser PythonAnywhere. Deux options :
  (a) installer `uv` sur PythonAnywhere et faire `uv sync --frozen` (ou `uv pip sync`) ;
  (b) garder pip côté serveur et générer un `requirements.txt` via `uv export --no-dev` au build/CI
  (fallback robuste si installer uv sur PA est contraignant). Choisir et **documenter** dans la doc deploy.

**2. `ruff` (lint + format, remplace flake8 / isort / black / pyupgrade).**
- Config dans `pyproject.toml` (`[tool.ruff]`) : règles `E,F,I` (imports), `UP` (pyupgrade),
  `DJ` (django), `B` (bugbear), `S` (sécurité, façon bandit) ; `ruff format` comme formateur.
- Passe initiale sur le code existant (corrections auto `ruff check --fix`), puis intégration CI.

**3. `pre-commit`.**
- Hooks : `ruff` + `ruff-format`, plus hygiène (`end-of-file-fixer`, `trailing-whitespace`,
  `check-yaml`, `check-added-large-files`). Lancement local + en CI.

**4. Vérification de types (optionnel, progressif).**
- `mypy` + `django-stubs` (mature) **ou** `ty` (vérificateur de types Astral, encore en préversion
  début 2026 — à adopter quand stable). Démarrer en mode permissif, app par app.

**5. Templates Django.**
- `djLint` (ou `djhtml`) pour **linter/formatter les templates** — utile vu le volume de templates
  retravaillés en Phases 3/4. Intégrable à `pre-commit`.

**6. Tests & couverture (optionnel).**
- `pytest` + `pytest-django` (exécution et fixtures plus agréables que le runner Django) +
  `pytest-cov`/`coverage`. Migrer les smoke tests si on adopte pytest. CI : lancer les tests sur PR.

**7. Mises à jour de dépendances automatisées.**
- **Dependabot** ou **Renovate** (PR automatiques de bumps), en complément/remplacement des pins Snyk
  manuels. Cible : `pyproject.toml`/`uv.lock` + actions GitHub.

**Autres pistes DX éventuelles :** `django-upgrade` (modernisation de code Django ; recouvre en partie
les règles `UP`/`DJ` de ruff), `interrogate` (couverture de docstrings), un `justfile`/`Makefile` pour
les commandes courantes (`run`, `lint`, `test`, `messages`), et `uv run` pour exécuter manage.py sans
activer le venv.

**Dépendances :** indépendante du front. **Recommandé tôt** (uv + ruff + pre-commit d'abord) pour que
tout le reste du chantier bénéficie du lint/format ; les briques optionnelles (types, pytest, djLint,
bots de MAJ) peuvent suivre. Seul point dur : **adapter le déploiement** (point 1) sans le casser.

## Dépendances entre phases

```
Phase 0 (filet) ─┬─> Phase 1 (deps sèches)            [indépendant]
                 ├─> Phase 2 (images/Firebase)        [indépendant du front]
                 ├─> Phase 9 (outillage uv/ruff)      [indépendant — recommandé tôt]
                 └─> Phase 3 (design system) ─> Phase 4 (templates apps) ─> Phase 5 (suppr. Bootstrap)
                                                          │                           │
                              Phase 8 (i18n EN) <─────────┤  Phase 6 (finitions) <─┬──┘
                                                          └─ Phase 7 (htmx)     <──┘
```

Les phases 1, 2 et 9 peuvent avancer en parallèle du front (3→4→5). La Phase 5 ne peut se faire
qu'après la fin de la Phase 4 (kendama forms inclus). Les Phases 6 (finitions), 7 (htmx) et
8 (i18n EN) sont les dernières. La Phase 8 est plus efficace une fois les templates stabilisés
(après la Phase 4), idéalement après la Phase 7 pour traduire aussi les fragments htmx.
La Phase 9 (outillage) est indépendante et gagne à être faite **tôt**.

## Rappels opérationnels

- Déploiement : push sur `master` déclenche le déploiement PythonAnywhere. Travailler sur la
  branche `refonte`, fusionner par incréments testés.
- Pas de trailer `Co-Authored-By` dans les commits ; ne pas utiliser le skill `/commit`.
- Vérifier `makemigrations --check` et `python manage.py check` à chaque phase.
- **Rejouer la suite de tests de smoke (27 tests, livrés en Phase 0) après chaque phase**, en
  particulier les phases front 3→5 et la Phase 2 (non-régression des endpoints API tracker & smm).
- Filet de sécurité Phase 0 en place : backup DB OK + backup bucket dans
  `~/backups/bucket-refonte-2026-05-29/media/` (325 fichiers, ~827 Mo).
</content>
