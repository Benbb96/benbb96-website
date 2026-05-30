# 02 — Front-end : suppression de Bootstrap & jQuery, modernisation CSS

## Objectif

Retirer Bootstrap 3.3.7, jQuery et `django-bootstrap3`. Les remplacer par une **feuille CSS maison
moderne**, sans framework et sans étape de build. Réduire drastiquement le poids front.

## Décision d'architecture

**Pas de framework, pas de build.** On écrit un petit design system maison en CSS natif moderne :

- **Custom properties** (`:root { --color-primary: ... }`) pour thème/couleurs/espacements.
- **Flexbox + CSS Grid** pour la mise en page (les classes `.flex-*` de `style.css` sont un point
  de départ).
- **`<dialog>`** natif pour les modales (remplace les modales Bootstrap/jQuery).
- **`:has()`, `:is()`, container queries** pour des composants sans JS.
- **`<details>/<summary>`** pour les accordéons/menus repliables.
- **Form rendering Django natif** (voir plus bas) pour remplacer `{% bootstrap_form %}`.

> Alternative écartée : un framework classless (Pico.css, etc.). Plus rapide à poser mais ajoute une
> dépendance CDN et un style générique. Le propriétaire veut du sur-mesure léger → CSS maison.

## Inventaire de ce qui dépend de Bootstrap/jQuery

D'après l'exploration (~500 occurrences de classes Bootstrap sur ~110 templates) :

| Élément Bootstrap | Occurrences (ordre de grandeur) | Remplacement moderne |
|-------------------|-------------------------------|----------------------|
| Grille `.row` / `.col-*` | ~212 | CSS Grid / flex maison (`.grid`, `.cols-*`) |
| Boutons `.btn .btn-*` | ~109 | `.btn` maison + variantes via custom properties |
| Formulaires `.form-control/.form-group` | ~60 | rendu form natif + CSS sur `input, select, textarea` |
| Panels `.panel*` | ~25 | `.card` maison |
| Alerts `.alert*` | ~15 | `.alert` maison (+ messages Django) |
| Glyphicons | ~15 | FontAwesome 6 (déjà présent) ou SVG inline |
| `.jumbotron`, `.container`, utilitaires | divers | `.hero`, `.container` maison, utilitaires ciblés |
| Pagination | qq | `components/pagination.html` restylé |
| `bootstrap-social.css` (boutons réseaux) | footer | ~20 lignes de CSS + FontAwesome brand icons |

Tags `{% bootstrap_* %}` à éliminer : `bootstrap_form`, `bootstrap_button`, `bootstrap_alert`,
`bootstrap_messages`, `bootstrap_javascript`. Présents notamment dans `templates/registration/`,
et dans les templates de formulaire de **plusieurs apps** (dont kendama — voir doc 6).

Usages jQuery à convertir en `fetch`/vanilla :
- `templates/base.html` : `$.ajaxSetup` CSRF → helper `fetch` avec header `X-CSRFToken`.
- `music` (templates) : `$.post().done().fail()` sur `.platformLink` → `fetch`.
- `tracker/static/tracker/js/common.js` : AJAX Chart.js → `fetch`.
- `base/static/base/js/formset_handlers.js` : utilise `django.jQuery` (jQuery **de l'admin**) →
  peut rester tel quel si seulement utilisé en admin ; sinon réécrire en vanilla.
- **kendama est déjà en `fetch` natif** → ne pas toucher au JS kendama.

## Remplacement du rendu de formulaire (`{% bootstrap_form %}`)

Django 5 sait rendre les formulaires nativement. Stratégie recommandée :

1. Définir un template de rendu de champ maison (form renderer) ou utiliser `{{ form.as_div }}`
   (Django ≥ 4.1) + CSS sur la structure générée.
2. Pour un contrôle fin, créer un include `templates/components/form.html` qui itère
   `{% for field in form %}` et rend label / widget / aide / erreurs avec les classes maison.
3. Remplacer chaque `{% bootstrap_form form %}` par `{% include 'components/form.html' %}` (ou
   `{{ form.as_div }}`).
4. Styler `input, select, textarea, .errorlist, .helptext` dans le CSS global.

Cela permet de **désinstaller `django-bootstrap3`** une fois tous les usages convertis.

## Plan de découpe (sous-chantiers)

1. **Design system CSS** — créer `assets/css/main.css` (ou plusieurs fichiers) :
   custom properties (couleurs, typo, espacements, radius), reset léger, base typographique,
   layout (`.container`, `.grid`, `.flex-*`), composants (`.btn`, `.card`, `.alert`, `.badge`,
   nav, footer, table, pagination, form). Documenter les classes dans un commentaire en tête.
2. **Layout global** — réécrire `base.html`, `navbar.html`, `footer.html`, `favicon` :
   retirer le CDN Bootstrap et `{% bootstrap_javascript %}`, charger `main.css`, navbar moderne
   (menu `<details>` ou checkbox-hack pour le mobile, sans JS), footer social en FontAwesome.
   Conserver le bloc Google Analytics et le sélecteur de langue.
3. **Composant form + messages** — `components/form.html`, rendu des `messages` Django en `.alert`
   maison (remplace `{% bootstrap_messages %}`), `components/pagination.html`.
4. **Migration app par app** des templates : `registration/`, `base`, `avis`, `music`, `tracker`,
   `versus`, `super_moite_moite`, `my_spot` (effort minimal), `kendama` (forms only, doc 6).
   Convertir grille, boutons, panels, alerts, glyphicons.
5. **JS** : helper `fetch` + CSRF, conversion des usages jQuery, suppression du `$.ajaxSetup`.
   **Supprimer `moment-with-locales.js` (541 Ko)** — décision actée. Usages réels et remplacements
   **natifs** (pas de Temporal : pas encore fiable en natif sur tous les navigateurs début 2026) :
   - `tracker/static/tracker/js/common.js`, `tracker_detail.html`, `compare_trackers.html` :
     formatage + presets de plage de dates, couplés à **`bootstrap-daterangepicker`** (CDN, dépend de
     jQuery **et** moment). → Remplacer daterangepicker par **deux `<input type="date">` natifs**
     (ou un petit composant moderne), l'arithmétique des presets (« 7 derniers jours »…) par `Date`
     natif, et le formatage par **`Intl.DateTimeFormat`**.
   - `super_moite_moite/static/super_moite_moite/js/vue.js` + `logement_detail.html` : `format('LLL')`
     → `Intl.DateTimeFormat` ; `fromNow()` → **`Intl.RelativeTimeFormat`**.
   - Au passage, **monter Chart.js de v2.7.3/2.9.3 → v4** (tracker ; vérifier aussi le composant
     fréquence kendama qui utilise Chart.js 2.9.3 — cf. doc 6, à upgrader prudemment ou laisser).
   Gain : -541 Ko (moment) + suppression de daterangepicker, le tout sans nouvelle dépendance.
6. **Nettoyage** : supprimer `bootstrap-social.css`, retirer `django-bootstrap3` des requirements
   et de `INSTALLED_APPS`, retirer le CDN Bootstrap. `collectstatic` + tests visuels.

## Points d'attention

- **Kendama** : son `base.html` et `paper.css` sont autonomes (aucune dépendance Bootstrap pour le
  style) **mais** ses templates de **formulaire** utilisent `{% bootstrap_form %}`. Il faut donc les
  convertir avant de désinstaller `django-bootstrap3` (doc 6). Ne pas toucher au reste de kendama.
- **FontAwesome 6** : conservé (`django-fontawesome-6`). Sert aussi aux `IconField`
  (tracker, my_spot, réseaux sociaux) → **ne pas retirer**.
- **Select2** (`django-select2`) : composant JS qui embarque sa propre dépendance. Conservé
  fonctionnellement (versus, music, tracker, smm). Vérifier qu'il fonctionne sans le jQuery global
  (django-select2 charge son propre jQuery côté admin/forms).
- **Admin Django** : utilise son propre jQuery (`django.jQuery`) — indépendant du front public.
- **Responsive** : `style.css` a déjà des breakpoints (768/576px) à harmoniser dans le design system.
- **i18n** : préserver les `{% trans %}`/`{% blocktrans %}` lors des réécritures de templates.

## Critères de validation

- [ ] Plus aucune référence à `bootstrap`, `glyphicon`, `panel`, `jumbotron`, `bootstrap3` dans les
      templates (hors kendama `paper.css` qui a ses propres classes).
- [ ] `django-bootstrap3` retiré de `INSTALLED_APPS` et des requirements.
- [ ] jQuery non chargé sur les pages publiques (vérifier l'onglet réseau).
- [ ] Aucune régression visuelle majeure sur home, profils, listes/détails de chaque app.
- [ ] Kendama strictement identique (doc 6).
- [ ] `python manage.py check` OK, pages servies sans erreur JS console.
</content>
