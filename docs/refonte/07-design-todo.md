# 07 — Design TODO (passe design dédiée, après la 5b)

> Liste **des retouches purement visuelles / d'ergonomie** repérées pendant la QA de la refonte,
> à traiter dans une **passe design dédiée** (plutôt Phase 6 « finitions »), une fois le front
> nettoyé (Bootstrap/jQuery retirés en 5b). Ce fichier ne concerne **pas** les bugs ni les
> régressions (ceux-là sont corrigés au fil de l'eau) : uniquement le « ça marche mais ça
> mériterait mieux ».
>
> Convention : une entrée = **page/zone concernée** + **ce qui cloche** + (éventuellement) piste.
> Cocher quand fait.

## 🎯 Passe UI/design dédiée à prévoir (souhait propriétaire)

Le propriétaire estime que **l'interface peut être nettement améliorée** (« il y a mieux comme
interface »). Une **passe design/UI dédiée** est prévue plus tard, potentiellement pilotée par un
**skill front-end / UI / design** spécialisé. Les corrections faites au fil de l'eau (ci-dessous et
dans les commits) sont des ajustements ponctuels, **pas** cette refonte visuelle d'ensemble.

## Direction visuelle (décidée avec le propriétaire)

- **Couleur signature : le JAUNE.** Le propriétaire aime beaucoup le jaune → couleur de marque /
  accent principal. ⚠️ À manier avec méthode : le jaune pur a un **contraste insuffisant** sur blanc
  → l'utiliser comme **accent** (fonds/boutons/highlights avec **texte foncé** dessus), **pas** pour du
  texte ou des liens fins. Construire une **rampe** complète (tints/shades du jaune) + des **neutres**
  (gris légèrement chauds pour s'harmoniser) + des couleurs **sémantiques** ; attention à **différencier
  le jaune de marque du « warning »** (souvent jaune/ambre aussi → décaler le warning vers l'orange/ambre).
  Valider les **contrastes WCAG** dans les deux thèmes (utiliser la méthodo couleur du skill design/dataviz).
- **Dark mode requis.** Prévoir un **thème sombre** complet, via les custom properties existantes
  (deux jeux de tokens : clair par défaut + sombre). **Toggle utilisateur** dans la navbar
  (clair / sombre / auto), **persisté** (localStorage), **défaut = préférence système**
  (`prefers-color-scheme`), en **vanilla JS** (pas de framework) avec un **petit script inline en
  `<head>`** pour éviter le flash de mauvais thème (FOUC). En sombre, **adoucir le jaune** (un peu
  désaturé) pour éviter l'éblouissement. **kendama exclu** (thème paper autonome — ne pas lui imposer
  le dark mode ; le toggle ne doit rien casser sur ses pages). Les maquettes Artifact doivent montrer
  **les deux thèmes**.

## Décisions/ajustements faits pendant la QA post-5b (contexte pour la passe design)

- **Conteneur large** : token `--ds-container-wide` (1280px) + modificateur `.content--wide`
  (activable par page via `{% block content_class %}content--wide{% endblock %}`). Appliqué à la
  **navbar** (plus large que les 1140px du contenu) et aux pages **tracker** (liste, détail,
  comparaison) pour que grilles/tableaux/graphes respirent.
- **Navbar** : compactée pour tenir à l'échelle 16px (liens `--ds-fs-sm`, padding réduit,
  `white-space:nowrap`) ; bascule menu burger relevée 860→1140px.
- **Contrôles tracker (détail & comparaison)** : formulaire d'ajout + filtre de dates regroupés dans
  une **colonne centrée `.tracker-controls` (720px, sans encadré)** au-dessus des données pleine
  largeur. (Un encadré avait été essayé puis retiré : il jurait avec le bandeau titre plus large et
  bridait les noms de trackers longs.) → à ré-évaluer lors de la passe design.

## ⚠️ Échelle globale : root 16px depuis la 5b (à re-QA sur TOUT le site)

Découvert pendant la QA 5b : Bootstrap 3 imposait `html { font-size: 10px }`. Comme `main.css` est
entièrement en `rem`, **tout le site était rendu à ~62,5 % de la taille nominale** pendant les phases
3→5a (body « 1.0625rem » = 10,6px, etc.). Le retrait de Bootstrap (5b) rétablit le root navigateur
(**16px**) : le site retrouve sa taille prévue (body 17px…), plus lisible — c'est le comportement
**voulu** (décision actée avec le propriétaire : « adopter le 16px nominal »). La navbar a été
corrigée dans la foulée (commit dédié).

**Conséquence** : toutes les pages sont désormais ~1,6× plus grandes que ce qui avait été validé
visuellement en 3→5a. Il faut **refaire une passe de QA visuelle sur l'ensemble des apps** à cette
échelle : espaces/marges, tailles de titres, éléments à largeur fixe, tableaux, cartes, graphes…
Les entrées ci-dessous restent valables mais sont à ré-évaluer à la nouvelle échelle.

## base (chrome & pages vitrines)

- [x] **Page d'accueil (`home.html`)** : direction jaune + dark mode appliquée, home
  passée en pitch perso (photo, tagline, CTA) + grille de projets. Design system
  (tokens, hero, navbar, boutons…) mis à jour en même temps (sitewide).
- [x] **« À propos » (`about.html`)** : parcours condensé (frise), compétences
  (pills), centres d'intérêt (chips), lien CV (PDF déposé dans `assets/files/`, fonctionnel).
- [ ] **Images des projets (home)** : remplacer les photos/stock-arts qui juraient avec la
  direction jaune + dark mode par des illustrations générées par IA. 7/10 générées et uploadées
  en local (Musique, Mes avis, Versus, Tracker, MySpot, Super Moite Moite, Kendama Tricks) ;
  Clips visuellement captivants/Liste des Fresques gardent leur image actuelle (captures de
  sites externes). Reste : régénérer Mes avis/Versus (filigrane Gemini), statuer sur Labyrinthe
  Game, synchroniser en prod, puis ajouter `Projet.description_fr`/`description_en` (différé).
  Détail complet dans [09-images-projets-ia.md](09-images-projets-ia.md).
- [x] **Tunnel « mot de passe oublié »** : les 4 étapes (`password_reset_form/done/confirm/complete`)
  n'étaient pas surchargées → Django servait celles de `contrib.admin`, donc thème admin bleu, hors
  design system et hors dark mode. Templates créés dans `templates/registration/` sur le pattern
  `login.html`/`signup.html`. Au passage, `password_reset_complete` pointait sur
  `PasswordResetConfirmView` (500 en fin de parcours) → corrigé en `PasswordResetCompleteView`.
- [x] **`.ds-alert` en thème sombre (sitewide)** : les fonds des variantes étaient des hex clairs en
  dur (`#f0fdf4`, `#f0f9ff`…) et la bordure mixée avec `white` → pastel clair sur fond sombre sur
  *toutes* les alertes du site. Fond et bordure désormais dérivés de `--_c` + `--ds-surface` via
  `color-mix()`, dosés par `--ds-alert-tint` / `--ds-alert-border-tint` (7 %/35 % en clair,
  18 %/45 % en sombre). Une variante ne pose plus que `--_c` — ne jamais y remettre de hex en dur.
- [x] **Déconnexion (405)** : `LogoutView` n'accepte plus le GET depuis Django 5.1, les deux liens
  du menu (navbar `.ds-*` et kendama) renvoyaient 405. Passés en `<form method="post">` ; le bouton
  est restylé pour rester indiscernable d'une entrée de menu, côté kendama dans sa feuille propre
  `style.css` (le `paper.css` vendorisé n'est pas touché, rendu vérifié identique au lien).
- [x] **Survol des `.ds-btn` sémantiques** : `--_bg-hover` était un hex figé de l'ancienne palette
  (`#b91c1c`, `#15803d`…), donc le survol s'assombrissait alors que le fond, tokenisé, s'éclaircit
  en sombre — sens du contraste inversé. Dérivé du fond via `color-mix(--_bg 88%, --ds-text)` :
  s'assombrit en clair, s'éclaircit en sombre. Les variantes ne posent plus que `--_bg` ; le bouton
  jaune garde `--ds-primary-dark` (déjà défini par thème).
- [x] **Badges sémantiques retirés** : `.ds-badge--success/--warning/--danger/--info` avaient des
  couleurs en dur hors thème **et** zéro usage (seul `--primary`, tokenisé, sert — 6× dans avis).
  Supprimées plutôt que retokenisées ; `--info` traînait en plus isolé loin de sa section.

## avis

- [x] **Liste des structures (`structure_filter.html`)** : titre centré, filter-bar en encart,
  produits d'une structure en badges cliquables.
- [x] **Détail d'une structure (`structure_detail.html`)** : hiérarchie typographique nettoyée,
  bloc infos en `.ds-card`, grille infos/carte à une colonne si pas d'adresse.
- [x] **Liste des produits (`produit_filter.html` / `produit_table.html`)** : titre centré,
  filter-bar en encart ; filtre catégories en Tom Select multiple, prix en min/max avec
  placeholders (`avis/filters.py`).
- [x] **Détail d'un produit (`produit_detail.html`)** : bloc infos produit en `.ds-card`, section
  avis avec compteur, harmonisé avec structure_detail.
- [x] Cohérence visuelle des pages avis (liste avis, détail avis, catégorie) : titres/notes/badges
  harmonisés, note (`.ds-score`) remontée à côté du titre sur avis_detail.

## music

- [x] **Module musique** (listes musiques/artistes/styles/labels/playlists + détails) : passe de
  design d'ensemble faite — en-tête des 4 pages détail (artiste/label/style/playlist) uniformisé
  sur le pattern h1 centré, titres-labels de métadonnées démotés en `<small>`, listes polish
  (`.ds-cluster--split`, i18n, alignement tableau artistes).

## super_moite_moite

- [x] **`logement_detail.html` (onglet Statistiques)** : hauteur des donuts ApexCharts fixée
  (280px, au lieu du défaut ~400px sans rapport avec la largeur réelle) ; thème clair/sombre
  synchronisé (`theme.mode` + tooltip) via `data.theme` (`vue.js`).

## tracker

- [x] **Filtre de plage de dates** : les deux `<input type="date">` regroupés visuellement
  (`.ds-input-group` + séparateur), bornés à la plage réelle de données, fin/début non inversables.
- [x] **Graphes Statistiques (Chart.js)** : couleurs de grille/axes/légende thémées clair/sombre
  (`applyChartTheme()`), palette catégorielle validée pour le donut « par jour de la semaine »,
  couleur du tracker reprise pour le bar chart « par heure ».

<!--
Gabarit d'entrée à copier :
- [ ] **<page / template>** : <ce qui cloche>. <piste éventuelle>
-->
