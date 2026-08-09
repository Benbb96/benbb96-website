# 01 — État des lieux (cartographie de l'existant)

Référence factuelle de l'architecture actuelle, au démarrage de la refonte. Sert de base à tous les
autres documents.

## Stack technique

- **Backend** : Django 5.2.14, Python. Settings éclatés en `config/settings/{base,dev,prod}.py`.
- **Secrets** : `secrets.json` à la racine (hors VCS), lu par `get_secret_setting()`.
- **DB** : SQLite (dev **et** prod).
- **Front** : Bootstrap 3.3.7 (CDN) + jQuery (via `django-bootstrap3`), FontAwesome 6, CSS maison.
- **Pas de build front** (pas de npm/webpack). JS en CDN, en `static/`, ou inline.
- **API** : Django REST Framework + SimpleJWT (app mobile + frontends Vue externes).
- **Hébergement** : PythonAnywhere ; CI/CD GitHub Actions (deploy SSH sur push `main`) +
  CodeQL (`.github/workflows/codeql-analysis.yml`).

## Apps Django et leur état

| App | Rôle | État | Remarques refonte |
|-----|------|------|-------------------|
| `base` | Cœur : home, profils, about, gallery, rallye, jeu labyrinthe (p5.js), widget upload Firebase | Actif | Contient le widget Firebase à remplacer (doc 3) |
| `tracker` | Suivi de séries temporelles (événements/mesures), graphes Chart.js, **API DRF** consommée par Vue externe + montre connectée | **Actif (récent)** | Ne pas casser l'API. Frontend HTML à moderniser |
| `versus` | Suivi de parties/jeux entre joueurs, classements | Actif | HTML only, Select2 dans formsets |
| `avis` | Avis sur produits/structures, geoposition, photos | Actif | Utilise Firebase + geoposition + django-filter |
| `music` | Catalogue musical (artistes, titres, playlists), intégrations Spotify/SoundCloud/YouTube | Actif | Dépend de spotipy, soundcloud (fork), google-api |
| `super_moite_moite` | Suivi de tâches en colocation, **API DRF + Vue.js embarqué** | **Actif (récent)** | Vue.js dans `static/`, Firebase pour photos de tâches |
| `kendama` | Tricks/combos/ladders de kendama, suivi de fréquence, historique | Actif | **À PRÉSERVER** — thème « paper » autonome (doc 6) |
| `my_spot` | Carte de « spots » géolocalisés | **Abandonné** | `request.is_ajax()` déprécié (cassé Django ≥4.1). Effort minimal |

### Détails par app (modèles clés)

- **base** : `Profil` (OneToOne User, avatar, birthday), `Projet` (cartes de la home, contrôle
  d'accès actif/logged_only/staff_only), `LienReseauSocial` (footer), `PhotoAbstract` (abstrait,
  champ `photo` = TextField stockant un chemin Firebase ou une URL ; propriété `photo_url` qui
  résout via Pyrebase). Vues : `signup`, `UserDetailView`, `update_profil`, `change_password`,
  `ProjetListView` (home). Jeu labyrinthe = p5.js (`base/static/base/js/labyrinthe_game/`).
- **tracker** : `Tracker` (SortableMixin, type événement/mesure, IconField, ColorField),
  `Track` (datetime, valeur, commentaire). API DRF : `TrackerViewSet`, `TrackViewSet`,
  `TrackerSerializer` / `TrackerLightSerializer` (sans tracks, pour montre connectée). AJAX :
  `tracker_data` (datasets Chart.js, resampling **pandas**), `get_other_stats`, `tracker_history`.
  CORS autorise `https://vue-trackers.onrender.com`.
- **versus** : `Joueur`, `Jeu` (types Score / Score inverse / Classement), `Partie`,
  `PartieJoueur`. Logique de classement/winners. Formsets inline + Select2.
- **avis** : `CategorieProduit`, `TypeStructure`, `Structure` (GeopositionField),
  `Produit`, `Avis` (hérite PhotoAbstract, note 0-10). FilterViews (django-filter).
- **music** : `Artiste`, `Musique`, `Playlist`, `Style`, `Label`, `Plateforme`, `Lien`
  (+ HistoricalRecords sur Artiste/Musique). OAuth Spotify, sync playlists, fetch YouTube/SoundCloud.
- **super_moite_moite** : `Logement`, `Categorie`, `Tache` (hérite PhotoAbstract), `PointTache`,
  `TrackTache`. API DRF complète + composant Vue.js (`static/super_moite_moite/js/vue.js`).
- **kendama** : `KendamaTrick`, `Combo`, `Ladder` (+ tables d'ordre `ComboTrick`/`LadderCombo`),
  `TrickPlayer`/`ComboPlayer` (fréquence 1-6 + HistoricalRecords), `Kendama` (hérite PhotoAbstract).
- **my_spot** : `Spot` (GeopositionField), `SpotTag`, `SpotGroup`, `SpotPhoto` (PhotoAbstract),
  `SpotNote`. Vues FBV avec `request.is_ajax()` **déprécié**.

## Frontend actuel (détaillé)

### Templates globaux (`templates/`)
- `base.html` : layout maître. Charge Bootstrap 3.3.7 (CDN), `{% bootstrap_javascript jquery='full' %}`,
  `style.css`, `avis-style.css`, `bootstrap-social.css`, FontAwesome 6. Blocs : `title`,
  `stylesheet`, `navbar`, `jumbotron_title`, `jumbotron_description`, `content`, `javascript`.
  Contient un `$.ajaxSetup` jQuery (CSRF via `js-cookie`).
- `navbar.html` : navbar Bootstrap (`navbar-inverse`, toggle mobile, sélecteur de langue, glyphicons
  login/logout).
- `footer.html` : boucle de boutons sociaux (`btn-social-icon` + `bootstrap-social.css`).
- `favicon.html`, `404.html`, `500.html`, `components/pagination.html`,
  `registration/` (login, signup), overrides `admin/`, `colorfield/`.

### CSS
- `assets/css/style.css` (~122 lignes) : custom navbar/footer, `.content`, **classes flex maison
  déjà présentes** (`.flex-container`, `.flex-row`, `.flex-col` responsive) — base utile pour la
  modernisation.
- `assets/css/bootstrap-social.css` (~800 lignes) : boutons sociaux (à remplacer par ~20 lignes de CSS).
- `avis/static/avis/css/avis-style.css` : chargé globalement depuis `base.html`.

### JavaScript
- jQuery (via django-bootstrap3) : `$.ajaxSetup` global, AJAX dans `music`, `tracker`.
- `assets/js/moment-with-locales.js` (**541 KB**) : moment.js — usage à confirmer/supprimer.
- `base/static/base/js/firebase-upload.js` : upload Firebase (doc 3).
- `base/static/base/js/formset_handlers.js` : utilise `django.jQuery` (jQuery de l'admin — OK à garder).
- `base/static/base/js/p5*.js` + `labyrinthe_game/` : jeu labyrinthe (p5.js).
- **Chart.js** (CDN) : utilisé par `tracker` et `kendama` (composant fréquence).
- `kendama` : déjà en **`fetch()` natif**, pas de jQuery (voir doc 6).

### Context processors / template tags
- `base/context_processors.py` → `GOOGLE_ANALYTICS_KEY`, `GEOPOSITION_GOOGLE_MAPS_API_KEY`,
  `liens_reseaux_sociaux`.
- `base/templatetags/custom_tags.py` → `multiply_10`, `color`, `url_quote_plus`,
  `param_replace` (pagination), `contrast_color`.

## Mécanisme d'upload d'images actuel (Firebase)

Voir le détail complet dans [03-gestion-images.md](03-gestion-images.md). En résumé :
1. `FirebaseUploadWidget` (`base/widgets.py`) rend un `<input file>` + bouton + `<progress>` + preview.
2. `firebase-upload.js` initialise Firebase **avec une config en clair** (clé API exposée), uploade
   le fichier **directement du navigateur vers Firebase Storage** (bucket
   `eminent-airport-148108.appspot.com`), chemin `media/{folder}/{année}/{mois}/{jour}/{fichier}`.
3. Le **chemin** (pas l'URL) est stocké dans un champ texte du modèle (`PhotoAbstract.photo`).
4. À l'affichage, `PhotoAbstract.photo_url` résout le chemin en URL via **Pyrebase4** côté serveur.
5. Modèles concernés : `Avis`, `Tache` (smm), `Kendama`, `SpotPhoto` (my_spot), + `Profil.avatar`.

## Dépendances (voir doc 4 pour l'audit complet)

Fichiers : `requirements/base.txt`, `dev.txt`, `prod.txt`.
- **Inutilisées** : `django-avatar`, `django-redis`, `redis` (pas de `CACHES` configuré).
- **À remplacer** : `django-bootstrap3` (front), `Pyrebase4` (images).
- **Vieilles/risquées** : `google-api-python-client==1.12.11` (2020), `soundcloud` (fork git, API
  dépréciée), SDK Firebase JS v7.8.1 (CDN, 2020).
- **À conserver** : Django, DRF, simplejwt, django-filter, django-select2, simple-history,
  colorfield, fontawesome-6, geoposition, autoslug, admin-sortable, pandas/django-pandas (tracker),
  Pillow, spotipy, python-slugify, anymail (prod).
</content>
