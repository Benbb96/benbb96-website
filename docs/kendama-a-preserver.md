# 06 — Kendama : contrat de préservation

> ⚠️ **L'app `kendama` doit rester visuellement IDENTIQUE.** Le propriétaire y tient. Elle utilise un
> thème CSS dédié (« paper ») totalement autonome. Ce document liste ce qui est **intouchable** et la
> **seule** modification autorisée.

## Pourquoi kendama est un cas à part

`kendama` n'utilise **pas** le `base.html` global du site. Elle a :
- son propre layout `kendama/templates/kendama/base.html` ;
- son propre thème `kendama/static/kendama/css/paper.css` (+ `paper.min.css` + `style.css`) ;
- du **JavaScript vanilla `fetch()`** (pas de jQuery) ;
- des composants sans JS lourd (modales via checkbox-hack CSS, nav repliable via checkbox).

→ La suppression de Bootstrap/jQuery sur le reste du site **n'affecte pas** le style de kendama.

## Le thème « paper » (NE PAS MODIFIER)

- **Fichiers** : `kendama/static/kendama/css/paper.css`, `paper.min.css`, `style.css`.
- **Police** : Google Fonts `Neucha` (texte) + `Patrick Hand SC` (titres) — aspect manuscrit.
- **Palette** : `#41403e` (texte), `#c1c0bd`, `#0071de` (secondaire), `#deefff`, `#86a361` (succès),
  `#ddcd45` (warning), `#a7342d` (danger), `#868e96` (muted).
- **Signatures visuelles** : conteneur `.paper` (bordure + ombre + padding), **bordures
  ondulées/organiques** sur les images (`border-radius` asymétriques type `255px 15px`), séparateurs
  `~~~`, grille maison (`col-1..12`, préfixes xs/sm/md/lg), modales et nav **sans JS** (checkbox-hack).
- paper.css est **autonome** : ne dépend ni de Bootstrap ni de Tailwind. Le garder chargé suffit.

## JavaScript kendama (NE PAS MODIFIER)

- `fetch()` natif + CSRF via `js-cookie`. Endpoints : `update-frequency` (POST JSON),
  `frequency-history` (GET → HTML de modale), `create-trick-from-modal` (POST FormData).
- **Chart.js** (CDN, v2.9.3) dans `components/table_frequency.html` (histogramme de fréquence).
- Aucune dépendance jQuery. **Ne pas réécrire ce JS** dans le cadre du chantier front.

## ⚠️ La SEULE modification nécessaire

Les **templates de formulaire** kendama dépendent de `django-bootstrap3` :

- `kendama/templates/kendama/kendamatrick_form.html`
- `kendama/templates/kendama/combo_form.html`
- `kendama/templates/kendama/ladder_form.html`
- `kendama/templates/kendama/kendama_form.html`

Ils contiennent `{% load bootstrap3 %}` et `{% bootstrap_form form %}`. Comme on désinstalle
`django-bootstrap3` (doc 2/4), il faut **remplacer ce rendu** par un rendu compatible avec le thème
paper :

- Rendre les champs manuellement avec les **classes paper** existantes (ex. `.input-block`,
  inputs/textarea/select stylés par paper.css), ou via un petit include maison.
- Conserver **strictement** la structure et l'apparence (les formsets `ComboTrickFormSet` /
  `LadderComboFormSet`, le bouton « + », la modale de création de trick, les widgets `trickSelect`,
  la largeur des champs `order`, etc.).
- **Tester visuellement** : les formulaires de création/édition de trick, combo, ladder, kendama
  doivent rester identiques.

> C'est la seule entorse au « ne rien toucher ». Elle est imposée par la suppression de
> `django-bootstrap3`. Tout le reste de kendama (listes, détails, profil, modales, charts) reste tel quel.

## Dépendances kendama à conserver

- `django-filter` (FilterViews), `django-autoslug` (slugs), `django-simple-history`
  (`HistoricalRecords` sur `TrickPlayer`/`ComboPlayer` — **cœur de l'UX** de suivi de fréquence).
- `PhotoAbstract` de l'app `base` : le modèle `Kendama` en hérite. Lors du chantier images (doc 3),
  `Kendama.photo` suit la même migration Firebase → local que les autres ; **le rendu visuel des
  photos de kendama doit rester identique** (bordures ondulées paper).

## Checklist de préservation

- [ ] `paper.css` / `paper.min.css` / `style.css` kendama **inchangés**.
- [ ] `kendama/templates/kendama/base.html` **inchangé** (hors éventuel ajustement si un asset global
      retiré y était référencé — à vérifier).
- [ ] JS kendama (`fetch`, modales, charts) **inchangé**.
- [ ] Seuls les 4 templates de formulaire modifiés, à l'identique visuellement, sans `bootstrap3`.
- [ ] Photos kendama migrées (doc 3) mais rendu visuel (bordures paper) préservé.
- [ ] Comparaison avant/après des pages kendama : aucune différence visible.
</content>
