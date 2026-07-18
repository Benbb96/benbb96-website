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
  direction jaune + dark mode par des illustrations générées par IA. Détail complet (méthode,
  prompts, état par projet) dans [09-images-projets-ia.md](09-images-projets-ia.md) — reste à
  terminer Super Moite Moite/Kendama/Labyrinthe Game, uploader les images validées, puis ajouter
  `Projet.description_fr`/`description_en` (différé, cf. même doc).

## avis

- [ ] **Liste des structures (`structure_filter.html`)** : retravailler le design.
- [ ] **Détail d'une structure (`structure_detail.html`)** : retravailler le design.
- [ ] **Liste des produits (`produit_filter.html` / `produit_table.html`)** : retravailler le design.
- [ ] **Détail d'un produit (`produit_detail.html`)** : réorganiser la page / mieux harmoniser les
  espaces (hiérarchie entre le bloc d'infos produit à gauche et « Les avis » à droite, marges,
  alignements).
- [ ] Revoir globalement la cohérence visuelle des pages avis (liste avis, détails…).

## music

- [ ] **Module musique** (listes musiques/artistes/styles/labels/playlists + détails) : passe de
  design d'ensemble à prévoir.

## super_moite_moite

- [ ] **`logement_detail.html` (onglet Statistiques)** : les cartes des donuts ApexCharts sont très
  hautes (beaucoup de vide vertical) — revoir la hauteur / le dimensionnement des graphes.

## tracker (optionnel, basse priorité)

- [ ] **Filtre de plage de dates** : le natif (deux `<input type="date">` + presets) fonctionne bien
  et sans dépendance. Un vrai « date-range picker » serait un confort marginal — à ne faire qu'en
  vanilla, si vraiment souhaité (ne pas ajouter de lib juste pour ça).

<!--
Gabarit d'entrée à copier :
- [ ] **<page / template>** : <ce qui cloche>. <piste éventuelle>
-->
