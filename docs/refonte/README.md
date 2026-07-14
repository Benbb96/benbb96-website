# Refonte du site benbb96.com — Documentation de planification

> Ces documents sont le **point d'entrée pour tout agent** (ou développeur) qui travaille sur la
> refonte. Ils décrivent l'état des lieux, les décisions prises et le plan d'exécution découpé en
> chantiers indépendants. Lis ce README en premier, puis le document du chantier qui te concerne.

## Objectifs de la refonte (demandés par le propriétaire)

1. **Moderniser le site**, le rendre plus actuel visuellement et techniquement.
2. **Supprimer Bootstrap** (et jQuery) — le CSS moderne permet aujourd'hui de reproduire la
   plupart des composants sans framework ni JS.
3. **Alléger le bundle** : réduire le nombre de dépendances (Python + front), supprimer le code mort.
4. **Mettre à jour les paquets** vieillissants et **retirer ceux devenus inutiles**.
5. **Améliorer la gestion des images uploadées** — aujourd'hui via un script JS qui pousse sur
   Firebase Storage. Objectif : faire mieux, **sans solution payante** (pas de S3).
6. **Conserver à l'identique** la partie **Kendama** (thème CSS « paper » séparé).
7. Les projets **abandonnés** (ex. MySpot) ne nécessitent pas d'effort — voir cas par cas.

## Contraintes connues

- **Hébergement** : PythonAnywhere, déploiement par SSH sur push `master`
  (`.github/workflows/deploy-to-pythonanywhere.yml`). `git pull` → `pip install` →
  `migrate` → `collectstatic` → `touch wsgi`.
- **Base de données** : **SQLite** en prod (`db.sqlite3`) comme en dev.
- **Médias** : `MEDIA_ROOT = /home/benbb96/media` déjà configuré en prod → **le stockage de fichiers
  local est déjà opérationnel** (point clé pour la sortie de Firebase).
- **Static** : servis par PythonAnywhere (pas de WhiteNoise), `collectstatic` vers `static/`.
- **Pas de build front** : aucun `package.json`, webpack, npm. Tout le JS est soit en CDN, soit
  embarqué dans `assets/`/`<app>/static/`, soit inline dans les templates.
- **i18n** : site bilingue FR/EN (`gettext`, fichiers `.po`/`.mo`).
- **API** : DRF + JWT consommés par des frontends externes (app mobile + `vue-trackers.onrender.com`
  pour le tracker, Vue.js embarqué pour `super_moite_moite`). **Ne pas casser les contrats d'API.**

## Index des documents

| # | Document | Contenu |
|---|----------|---------|
| 1 | [01-etat-des-lieux.md](01-etat-des-lieux.md) | Cartographie complète : apps, modèles, dépendances, front actuel |
| 2 | [02-frontend-suppression-bootstrap.md](02-frontend-suppression-bootstrap.md) | Plan de suppression de Bootstrap/jQuery et modernisation CSS |
| 3 | [03-gestion-images.md](03-gestion-images.md) | Sortie de Firebase → stockage local Django + migration des images existantes |
| 4 | [04-nettoyage-dependances.md](04-nettoyage-dependances.md) | Audit dépendance par dépendance, ce qui part / reste / se met à jour |
| 5 | [05-roadmap.md](05-roadmap.md) | Roadmap phasée, ordre des chantiers, dépendances entre eux |
| 6 | [06-kendama-a-preserver.md](06-kendama-a-preserver.md) | Contrat de préservation du thème « paper » Kendama |
| 7 | [07-design-todo.md](07-design-todo.md) | Backlog de la passe design sur les templates |
| 8 | [08-deploiement-uv.md](08-deploiement-uv.md) | Déploiement PythonAnywhere sur uv + prérequis prod manuels (Phase 9) |

## Résumé exécutif des décisions

- **Front** : remplacer Bootstrap 3.3.7 (CDN) + jQuery par **une feuille CSS maison moderne**
  (custom properties, flexbox, grid, `:has()`, `<dialog>`), pas de framework. Supprimer
  `django-bootstrap3`, remplacer `{% bootstrap_form %}` par un rendu Django natif maison.
- **Images** : abandonner Pyrebase + le SDK Firebase JS + la config exposée. Repasser sur
  `ImageField` Django + `django-storages` (backend Google Cloud Storage) **sur le bucket Firebase
  existant** (un bucket Firebase = un bucket GCS) → gratuit, images existantes en place. Upload
  serveur + optimisation Pillow (resize + WebP). Migration = simple normalisation (les fichiers ne
  bougent pas). Le disque PythonAnywhere n'est plus sollicité (cause de la saturation passée).
- **Dépendances à retirer** : `django-bootstrap3`, `django-avatar`, `django-redis`, `redis`,
  `Pyrebase4`, et à terme `soundcloud` (fork git, API dépréciée). À **ajouter** :
  `django-storages[google]` (stockage images). À mettre à jour : `google-api-python-client`
  (1.12.11 → récent). Côté front : suppression de `moment.js` (541 Ko) + `bootstrap-daterangepicker`
  au profit des API natives `Intl`/`Date`, et montée de Chart.js en v4. Détails dans les docs 2 et 4.
- **Kendama** : intouchable visuellement. Seule exception : retirer la dépendance
  `{% bootstrap_form %}` de ses templates de formulaire (doc 6).

## Conventions pour les agents

- Le site est en **français** (UI et commentaires existants mélangent FR/EN — privilégier le FR).
- **Ne pas** ajouter le trailer `Co-Authored-By` dans les commits ; **ne pas** utiliser le skill
  `/commit` de ce projet (préférences enregistrées du propriétaire).
- Tester chaque chantier avec `python manage.py runserver` + `python manage.py check`.
- Vérifier les migrations : `python manage.py makemigrations --check --dry-run`.
</content>
</invoke>
