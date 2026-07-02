# 07 — Design TODO (passe design dédiée, après la 5b)

> Liste **des retouches purement visuelles / d'ergonomie** repérées pendant la QA de la refonte,
> à traiter dans une **passe design dédiée** (plutôt Phase 6 « finitions »), une fois le front
> nettoyé (Bootstrap/jQuery retirés en 5b). Ce fichier ne concerne **pas** les bugs ni les
> régressions (ceux-là sont corrigés au fil de l'eau) : uniquement le « ça marche mais ça
> mériterait mieux ».
>
> Convention : une entrée = **page/zone concernée** + **ce qui cloche** + (éventuellement) piste.
> Cocher quand fait.

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
