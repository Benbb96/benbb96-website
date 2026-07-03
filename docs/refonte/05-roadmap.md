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

### Phase 5a — Levée des usages jQuery / Bootstrap-JS / moment / select2 — ✅ FAITE

Objectif : **zéro usage public** de jQuery, des plugins Bootstrap-JS, de select2, DataTables,
moment et daterangepicker, **sans encore retirer** Bootstrap CSS / jQuery / `django-bootstrap3` /
le CDN (= Phase 5b). Site fonctionnel et déployable à chaque étape (1 commit par app/dépendance).
Validé après chaque app : `check` OK, `makemigrations --check` sans changement, 27 smoke tests OK.

- **Fondation Tom Select (vanilla, sans jQuery)** remplace `django-select2` :
  `assets/js/tom-select.complete.min.js` + `css/tom-select.css` (vendorisés v2.4.3),
  `assets/js/tomselect-init.js` (init des `<select.js-tomselect>` : options rendues + filtrage
  client, ou chargement distant via `data-ts-url` + `window.http`), `base/widgets.py`
  (`TomSelect{,Multiple,Remote,RemoteMultiple}Widget`, assets via `Media`), thème `.ts-*` dans
  `main.css`. Petits jeux (≤ ~110 : styles, playlists, joueurs, habitants, trackers, tags…) rendus
  côté serveur ; gros jeu **artistes** (~1600) en chargement distant via l'endpoint JSON
  `music:artiste-search`.
- **versus** : `ModelSelect2Widget` (joueurs) → `TomSelectWidget` ; formset dynamique réinitialisé
  via `window.tomSelectInit` (plus de `$('.django-select2')`).
- **music** : forms/filters select2 → Tom Select (artistes distants) ; `create_musique_from_url.html`
  `$.post`/`$()`/`.trigger('change')` → `window.http` + API Tom Select ; `auto_select_plateforme`
  jQuery → vanilla ; **DataTables** (`playlist_filter.html`) → table `.ds-sortable` triable +
  recherche client en vanilla.
- **my_spot** : tags/groupes select2 → Tom Select ; `map.html` / `spot_group_detail.html`
  `$.get` Google Maps → `window.http` + DOM natif (valeurs des selects via l'API Tom Select).
- **super_moite_moite** : habitants select2 → Tom Select ; `vue.js` débarrassé de jQuery et des
  plugins Bootstrap-JS (`$('#x').text()` → `textContent` ; `.modal()` → `<dialog>` ; onglets
  pilotés par l'état Vue `mainTab`/`modalTab` au lieu de `data-toggle` pill/tab ; tooltips supprimés,
  `title` natif conservé) ; **moment → Intl** (`DateTimeFormat`/`RelativeTimeFormat`) ;
  `logement_detail.html` migré en `.ds-*` (modale `<dialog class="ds-modal ds-modal--lg">`,
  `.ds-progress` multi-segments, `.ds-card`, `.ds-input-group`…).
- **tracker** : `Select2MultipleWidget` → `TomSelectMultipleWidget` ; **bootstrap-daterangepicker**
  → deux `<input type="date">` + presets en `Date` (`include/date_range.html`, logique dans
  `common.js`) ; **moment → Intl** ; `$.post`/`$.ajax` → `window.http` (FormData `id[]`, PUT
  urlencodé, DELETE) ; **Chart.js 2.7.3 → v4** vendorisé (`assets/js/chart.umd.min.js`, API
  `plugins.legend`/`scales.y`/`plugins.tooltip`).
- **kendama** : **non touché** (déjà fetch natif + paper.css, embarque son propre Chart.js 2.9.3 ;
  vérifié sans dépendance au jQuery global).
- **base.html** : le `$.ajaxSetup` jQuery (CSRF des `$.ajax` des apps) devenu mort a été retiré.
  Bootstrap CSS + jQuery + `django-bootstrap3` + `bootstrap-social.css` + le CDN restent **chargés
  mais inutilisés**.

> Le fichier `assets/js/moment-with-locales.js` n'était plus chargé par aucun template à l'issue de
> la 5a ; il a été **supprimé** en Phase 5b (voir ci-dessous).

### Phase 5b — Retrait sec — ✅ FAITE

Tous les chargements devenus inertes après la Phase 5a ont été supprimés (1 commit cohérent) :
- `base.html` : retrait du `{% load bootstrap3 %}`, du CDN Bootstrap CSS, de
  `{% bootstrap_javascript jquery='full' %}` (jQuery global) et du `<link>` `bootstrap-social.css`.
- `INSTALLED_APPS` : retrait de `'bootstrap3'` et `'django_select2'`.
- `config/urls.py` : retrait de `path('select2/', include('django_select2.urls'))`.
- `requirements/base.txt` : retrait de `django-bootstrap3` et `django-select2`.
- Fichiers morts supprimés (`git rm`) : `assets/css/bootstrap-social.css`,
  `assets/js/moment-with-locales.js` (541 Ko).

Validé : `check` OK, `makemigrations --check --dry-run` sans changement, 27 smoke tests OK,
`collectstatic` OK (aucun asset supprimé référencé), QA HTTP des pages publiques (200 + plus aucune
référence jQuery/Bootstrap/moment/select2/daterangepicker dans le HTML servi ; `main.css` + `http.js`
bien chargés). **kendama et l'admin Django (django.jQuery privé) strictement inchangés.**

> Note : pas de Temporal (non fiable en natif début 2026) — le formatage de dates reste en `Intl`.
> Reste pour la Phase 6 : mettre à jour `README.md` / `techstack.*` (mentionnent encore Bootstrap).

## Phase 6 — Finitions — ✅ FAITE (avec reste listé)

- ✅ **README.md** : section « Tech Stack » actualisée (retrait Bootstrap/Redis ; ajout du design
  system CSS maison, Tom Select, Chart.js, django-storages + GCS, DRF + JWT, Pillow, pandas ; DB
  SQLite). Lien « Full tech stack » vers `techstack.md` conservé. Instructions d'install vérifiées.
- ✅ **Code mort front retiré** (grep à l'appui, 1 commit) :
  - `assets/css/style.css` : suppression de `.navbar`, du bloc `footer` (bg/padding + `footer p a`),
    de `.content` et `.errorlist` (désormais gérés par `main.css`) et des `.flex-row`/`.flex-col`
    (aucune occurrence). Conservés : `.text-italic`, `.flex-container`, `.spot-tag`, `.platformLink`,
    `#map` + rallye (`.hotes`/`.hote`/`.number`).
  - `avis/static/avis/css/avis-style.css` : suppression de `ul.breadcrumb` (migré `.ds-breadcrumb`)
    et `.carousel-caption` (plus utilisé).
  - `templates/colorfield/color.html` : retrait de la classe Bootstrap `form-control`.
  - **`form-control` dans les widgets Python** (`tracker/forms.py`, `music/forms.py`,
    `versus/views.py`, `super_moite_moite/forms.py`) : retiré partout (type de widget préservé).
    → **plus aucune occurrence de `form-control`** dans le projet (templates + Python).
  - **Consolidation CSS** : `assets/css/style.css` et `avis/static/avis/css/avis-style.css`
    (tous deux chargés globalement à côté de `main.css`) **fusionnés dans `main.css`** (section
    « styles hérités »), fichiers supprimés, 2 `<link>` retirés de `base.html` → 2 requêtes en moins.
  - Vérifié : context processors (3) et template tags (`multiply_10`, `url_quote_plus`, `param_replace`,
    `contrast_color`, `color`) **tous utilisés** → rien à retirer.
- ✅ **Accessibilité — quick wins** (1 commit) : lien d'évitement clavier « Skip to content »
  (`.ds-skip-link` + `id=main-content`), bloc `@media (prefers-reduced-motion: reduce)` global,
  `<label>` associé (`ds-sr-only`) sur le champ de recherche des playlists. Bases déjà saines :
  `:focus-visible` présent, pagination/messages avec `aria-*`/`role`, un seul `<img>` sans `alt`
  (kendama, hors périmètre).
- ✅ **Accessibilité — 2e passe** (1 commit par sujet) :
  - **Icônes décoratives** : `aria-hidden="true"` sur les `<i>` FontAwesome accompagnés d'un texte
    visible ou d'un lien parent titré (boutons Filtrer/Effacer/Ajouter/Éditer, liens de recherche
    par plateforme…).
  - **Menu mobile** : burger `role=button` focusable + `aria-controls`/`aria-expanded` ;
    `assets/js/nav.js` (amélioration progressive) synchronise `aria-expanded` et ouvre le menu au
    clavier (Entrée/Espace), la case du checkbox-hack étant `hidden`. Fallback souris sans JS conservé.
  - **Onglets `.ds-tabs[data-tabs]`** (tracker) : `initTabs` (`common.js`) pose `role=tablist/tab/
    tabpanel`, `aria-selected`, `aria-controls`, `aria-labelledby`, roving tabindex + navigation
    clavier (flèches, Home/End). Les `.ds-tabs` de **navigation** (profil) restent de simples liens.
- ✅ **Poids des pages + Lighthouse** : mesuré (voir « Bilan Phase 6 » ci-dessous). Rapport
  Lighthouse (home, mobile) exécuté par le propriétaire → scores reportés ci-dessous.
- ✅ **Hiérarchie des titres (home)** : le titre des cartes projet passe `<h3>` → `<h2>`
  (le hero est `<h1>`) — corrige l'audit Lighthouse « heading elements not in sequentially-descending
  order ». `.ds-card__title` se dimensionne selon la balise (usages mixtes h2/h3 ailleurs, non touchés).

**Hors périmètre (décisions propriétaire) :**
- `soundcloud` : **non évalué/retiré** — la remise en marche de la récupération d'infos via URL
  SoundCloud est une **tâche future dédiée**. Laissé tel quel.
- `techstack.md` / `techstack.yml` : **non touchés** — générés par l'app Stack File de GitHub
  (régénérés côté GitHub par le propriétaire).

**Reste à faire (a11y — demande plus de travail, à planifier) :**
- **Noms accessibles des contrôles icône-seule** : de nombreux boutons/liens ne contiennent qu'une
  icône FontAwesome sans texte (edit/trash/plus/check nus dans `tracker`, `versus`, `music`,
  `super_moite_moite`…). Leur donner un nom accessible (`aria-label` sur le contrôle, `aria-hidden`
  sur l'icône), en réutilisant les `title` FR existants quand ils existent. ⚠️ Beaucoup vivent dans
  le composant Vue de `super_moite_moite` (à traiter avec soin).
- **Liens distinguables autrement que par la couleur** (audit `link-in-text-block`, vu sur avis /
  music) : les liens dans le corps de texte n'ont pas de soulignement (`a { text-decoration: none }`
  dans `main.css`). WCAG 1.4.1 demande un indice non-coloré. Piste : souligner les liens **au sein
  du contenu** (ex. `.content p a`, prose) sans toucher aux liens boutons/cartes/nav. **Décision de
  design** (le propriétaire prévoit une passe UI dédiée).
- **Cibles tactiles** : l'audit Lighthouse `target-size` ne remonte **que les cases de la
  debug-toolbar** (dev) → **rien à corriger sur le site**. À revérifier sur un build sans toolbar.
- **Contrastes** : audit à faire avec un outil dédié sur les tokens de `main.css`
  (texte muté sur fond clair, `.ds-social`, hero) — non mesuré automatiquement ici. Peut impliquer
  d'ajuster des couleurs (impact visuel = décision de design du propriétaire).

**Reste à faire (performance) :**
- **LCP élevé sur la home** (~10 s en test mobile Lighthouse, cf. ci-dessous) : le point de contenu
  le plus grand est vraisemblablement une **image de carte projet non optimisée** (`projet.image`
  servie en pleine résolution, `max-height` en CSS seulement). Pistes : `loading="lazy"` +
  `width`/`height` explicites, servir des images optimisées (l'optimisation Pillow existe pour les
  `PhotoAbstract` mais `Projet.image` n'en bénéficie pas forcément). À mesurer hors debug-toolbar.

### Bilan Phase 6 — payoff de la refonte (poids des assets)

Comparaison des assets **chargés globalement** (via `base.html`), hors FontAwesome (constant) et
hors debug-toolbar (dev only) :

| | Avant (Bootstrap/jQuery) | Après (design system) |
|---|---|---|
| CSS framework | Bootstrap 3.3.7 (CDN) ~121 Ko + `bootstrap-social.css` 31 Ko | `main.css` ~44 Ko (design system + styles hérités fusionnés, 1 seul fichier) |
| JS framework | jQuery « full » (~280 Ko non-min) + Bootstrap JS ~37 Ko | `http.js` 4 Ko (vanilla) |
| **Total global** | **≈ 470–490 Ko** | **≈ 47 Ko** |

- **`moment-with-locales.js` (528 Ko)** : entièrement supprimé (git rm) — était chargé côté tracker.
- Plugins jQuery lourds (**select2 / DataTables / bootstrap-daterangepicker**) remplacés par
  **Tom Select** (~49 Ko CSS+JS) chargé **uniquement** sur les pages qui en ont besoin.
- **Chart.js** monté en v4 (`chart.umd.min.js` ~201 Ko) chargé **uniquement** sur le tracker.

→ Gain net : **~450 Ko de framework CSS/JS retirés de chaque page**, plus jQuery éliminé du front
public (conservé uniquement le `django.jQuery` privé de l'admin), plus **528 Ko de moment.js**
supprimés. Le front public ne dépend plus d'aucun framework CSS/JS tiers.

### Bilan Phase 6 — Lighthouse (mobile) + itération multi-pages

Lighthouse 13.4.0 (form factor **mobile**, en dev avec debug-toolbar). ⚠️ **La debug-toolbar
fausse deux audits** : `target-size` (ses ~12 cases à cocher sont les seules « cibles trop
petites » — **0 sur le site réel**) et la perf. Les scores a11y « après » ci-dessous seraient
donc **100 en prod** (sans toolbar).

| Page | A11y avant → après | BP | SEO avant → après | Agentic avant → après |
|---|---|---|---|---|
| home | 94 → **96** (100 prod) | 100 | 92 → **100** | 50 → **100** |
| avis (liste) | 90 → **~93** (100 prod) | 100 | 100 | 100 |
| avis (détail) | 94 → **96** (100 prod) | 100 | 100 | 100 |
| music (playlists) | 92 → **97** (100 prod) | 100 | 100 | 50 → **100** |
| versus (jeux) | 96 (100 prod) | 100 | 100 | 100 |

**Corrigé pendant l'itération** (1 commit par sujet) :
- **SEO 92→100** : `<meta name="description">` ajoutée (`base.html`).
- **Agentic 50→100** : arbre d'accessibilité bien formé — (a) burger sans `role=button` sur
  `<label>` (voir menu mobile), (b) `aria-label` sur le `<select>` de filtre Styles (Tom Select
  masque l'élément → un `<label for>` ne suffit pas).
- **heading-order** : titres de cartes/listes/détails remis en séquence (home, avis liste + détail).
- **select-name** : filtre Styles nommé (label + aria-label).

Métriques perf home : FCP 2,8 s · **LCP ~10 s** (à optimiser, cf. reste à faire perf) · TBT 0 ms ·
CLS 0,013. Best Practices 100 / TBT 0 / CLS ~0 confirment le bénéfice de la refonte (plus de
framework JS bloquant, layout stable).

> **Reproduire** : serveur lancé, puis `CHROME_PATH=/usr/bin/chromium lighthouse
> http://127.0.0.1:8000/fr/<page> --form-factor=mobile --screenEmulation.mobile --view`.
> Idéalement en **settings sans debug-toolbar** pour des scores perf/target-size représentatifs.

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
