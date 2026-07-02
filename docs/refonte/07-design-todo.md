# 07 — Design TODO (passe design dédiée, après la 5b)

> Liste **des retouches purement visuelles / d'ergonomie** repérées pendant la QA de la refonte,
> à traiter dans une **passe design dédiée** (plutôt Phase 6 « finitions »), une fois le front
> nettoyé (Bootstrap/jQuery retirés en 5b). Ce fichier ne concerne **pas** les bugs ni les
> régressions (ceux-là sont corrigés au fil de l'eau) : uniquement le « ça marche mais ça
> mériterait mieux ».
>
> Convention : une entrée = **page/zone concernée** + **ce qui cloche** + (éventuellement) piste.
> Cocher quand fait.

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

- [ ] **Page d'accueil (`home.html`)** : retravailler le design (priorité haute).
- [ ] **« À propos » (`about.html`)** : retravailler le design.

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
