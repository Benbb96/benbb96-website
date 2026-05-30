# 02 — Front-end : suppression de Bootstrap & jQuery, modernisation CSS

## État d'avancement

- **Phase 3 — FAITE** (design system + chrome global). Voir la section « Stratégie de
  coexistence retenue » ci-dessous. Livré :
  - `assets/css/main.css` : design system maison (tokens, reset léger, typo/éléments de base,
    layout, composants `.ds-*`). Chargé **en dernier** dans `base.html`.
  - `assets/js/http.js` : helper `fetch` + CSRF vanilla (`window.http`).
  - Chrome réécrit : `templates/base.html` (hero, conteneur, scripts), `templates/navbar.html`
    (nav maison, menu mobile sans JS via checkbox-hack + `:has()`, sélecteur de langue, icônes
    FontAwesome), `templates/footer.html` (boutons réseaux `.ds-social`).
  - `templates/components/messages.html` (+ `_message.html`) : messages Django en `.ds-alert`
    (remplace `{% bootstrap_messages %}`), fermeture sans JS.
  - `templates/components/pagination.html` restylé en `.ds-pagination`.
  - `templates/components/form.html` : rendu de formulaire maison (remplace `{% bootstrap_form %}`),
    **prêt pour la Phase 4** (pas encore branché sur les templates des apps).
- **Phases 4 et 5 — à venir** (migration des templates des apps, puis retrait de Bootstrap/jQuery).

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

## Stratégie de coexistence retenue (Phase 3 → 5)

Bootstrap 3 (CDN) + jQuery **restent chargés** tant que les apps ne sont pas migrées. Pour que le
design system maison cohabite **sans casser** les pages encore en Bootstrap, 3 règles sont appliquées
(documentées aussi en tête de `assets/css/main.css`) :

1. **Namespace `ds-` pour tous les composants maison** (`.ds-btn`, `.ds-card`, `.ds-alert`,
   `.ds-badge`, `.ds-nav`, `.ds-footer`, `.ds-hero`, `.ds-pagination`, `.ds-form`, `.ds-social`…).
   Aucune classe Bootstrap encore utilisée n'est redéfinie (`.btn`, `.row`, `.col-*`, `.container`,
   `.panel`, `.jumbotron`, `.form-control`, `.alert`, `.pagination`, `.label`…).
2. **`main.css` chargé en dernier** (après le CDN Bootstrap et `style.css`). Les **sélecteurs
   d'éléments** (`body`, titres, `a`, `table`, `input/select/textarea` nus) ont une spécificité
   d'élément (0,0,1) : ils gagnent le tie-break par l'ordre et modernisent le rendu « nu » partout.
   Mais les composants Bootstrap passent par des **classes** (spécificité supérieure) → ils gardent
   la priorité sur les pages d'app. Les styles de champs sont en plus restreints aux `input` nus
   (exclusion des types bouton/case/fichier) pour ne pas heurter `.form-control`. Aucun `!important`.
3. **JS — on ajoute sans retirer.** Le helper `fetch`+CSRF (`window.http`) est ajouté, mais le
   `$.ajaxSetup` jQuery de `base.html` est **conservé** (gardé derrière `if (window.jQuery)`) car
   `music` et `tracker` font encore du `$.ajax`. Il sera retiré quand ces usages passeront en `fetch`
   (Phase 4), en même temps que jQuery (Phase 5).

Includes globaux restylés dès la Phase 3 (assumé) : `components/pagination.html` et le rendu des
messages changent d'apparence sur **toutes** les pages, car ils font partie du chrome global.
`bootstrap-social.css` n'est plus utilisé (footer migré) mais reste **lié** dans `base.html` ;
son retrait est planifié en Phase 5.

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

1. **Design system CSS** — ✅ **FAIT** : `assets/css/main.css` (custom properties, reset léger, base
   typographique, layout `.ds-container`/`.ds-grid`, composants `.ds-btn`/`.ds-card`/`.ds-alert`/
   `.ds-badge`/`.ds-nav`/`.ds-footer`/`.ds-hero`/`.ds-pagination`/`.ds-form`/`.ds-social`). Classes
   namespacées `ds-` (pas de collision Bootstrap) et documentées en tête de fichier.
2. **Layout global** — ✅ **FAIT** : `base.html`, `navbar.html`, `footer.html` réécrits avec le CSS
   maison. ⚠️ Le CDN Bootstrap et `{% bootstrap_javascript %}` sont **conservés** (transition,
   Phase 5). Navbar moderne (menu mobile sans JS via checkbox-hack + `:has()`), footer social en
   FontAwesome (`.ds-social`). Bloc Google Analytics, sélecteur de langue et favicon conservés.
3. **Composant form + messages** — ✅ **FAIT** : `components/form.html` (rendu maison, branché en
   Phase 4), messages Django en `.ds-alert` (`components/messages.html`), `components/pagination.html`
   restylé `.ds-pagination`.
4. **Migration app par app** des templates : `registration/`, `base`, `avis`, `music`, `tracker`,
   `versus`, `super_moite_moite`, `my_spot` (effort minimal), `kendama` (forms only, doc 6).
   Convertir grille, boutons, panels, alerts, glyphicons.
5. **JS** : helper `fetch` + CSRF — ✅ **FAIT** (`assets/js/http.js`, `window.http`). Reste à faire en
   Phase 4 : conversion des usages jQuery, puis suppression du `$.ajaxSetup` (conservé pour l'instant).
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
