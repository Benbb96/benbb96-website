# 09 — Images des projets (home) : génération par IA

> État des lieux détaillé d'un chantier en cours (passe design, après la validation de la
> direction jaune + dark mode). Objectif : remplacer les photos/captures actuelles de
> `Projet.image` — souvent des stock-arts ou logos qui juraient avec la nouvelle direction —
> par des illustrations générées par IA, cohérentes avec la charte (jaune signature + fond
> encre + dark mode). Ce document consigne tout ce qu'il faut pour reprendre ce travail dans
> une session fraîche sans avoir à refaire l'exploration.

## Ce qui a été tenté et écarté

- **Icônes SVG codées à la main** (trait fin, `.ds-card__media--tile`) : trouvées « trop
  simples » par le propriétaire. Une 2e tentative avec un style « rempli + contour épais »
  (sticker) était un peu mieux mais restait nettement moins abouti que les illustrations IA.
  **Commit revert** (`git revert` du commit `feat(home): teste des vignettes SVG générées à
  la place des photos`) — ne pas relancer cette piste telle quelle sans nouvelle idée.
- **Décision actée** : on reste sur de vraies images en base (`Projet.image`), générées par IA
  puis uploadées manuellement par le propriétaire via l'admin Django (je n'ai pas d'accès
  fichier aux images générées dans le chat — seulement une vision de l'image partagée).

## Méthode de génération (validée)

### Prompt de style (constant, à réutiliser tel quel)

```
Minimalist flat vector illustration. Dark charcoal-brown background (#1C1912). Single
mustard-yellow accent color (#F2C200) for the main subject. Thin off-white line details
(#F7F5EF). No gradients, no photorealism, no text or letters anywhere in the image. Simple
geometric shapes, generous negative space, subject centered, 16:10 composition. Clean modern
icon-poster style, like a minimalist editorial illustration — not cartoonish, not cluttered.
```

### Règles qui ont fait la différence (leçons apprises)

1. **Décrire ce que le projet FAIT réellement, pas sa catégorie générique.** « Versus » n'est
   pas juste « un jeu » : c'est un tracker de sessions de jeux de société/vidéo avec
   classements dans la durée (cf. `versus/models.py` : `Joueur`/`Jeu`/`Partie`). Le premier
   essai générique (deux éclairs qui s'entrechoquent) ratait complètement cette nuance.
2. **Un seul objet unifié, jamais un collage.** Les tout premiers essais (Gemini, sujet
   « musique » générique) avaient trop d'éléments disjoints (casque + 3 vinyles + 3 cassettes +
   téléphone) avec des lignes de connexion qui ne menaient nulle part. Toujours explicitement
   demander *"one unified object/composition, no collage of separate objects, no dangling
   lines"*.
3. **Penser à la taille réelle d'affichage.** La carte fait ~380×240px sur la home
   (`.ds-card__media`, ratio 16/10) — une composition trop détaillée devient du bruit visuel à
   cette taille. Toujours le préciser dans le prompt.
4. **Garder la cohérence en réutilisant le même fil de conversation**, ou en attachant
   plusieurs images déjà validées comme référence avant de demander un nouveau sujet (« same
   style as the previous image(s) »). Un seul modèle de référence risque d'être copié
   littéralement ; 2-3 images de référence aident l'IA à isoler ce qui est constant (palette,
   fond, épaisseur de trait) de ce qui est spécifique au sujet.
5. **Itérer par édition ciblée plutôt que tout regénérer**, une fois qu'une composition est
   globalement bonne (ex. « generate this in the exact same style as the previous image, with
   one change: … »).

### Outils testés

- **Gemini** (app Gemini, gratuit) : génération conversationnelle itérative, permet de
  référencer l'image précédente pour affiner. A nécessité pas mal d'allers-retours sur des
  sujets à la composition compliquée (5 itérations pour Versus).
- **ChatGPT / GPT (images)** (chatgpt.com, gratuit) : a globalement atteint un résultat
  exploitable plus vite que Gemini sur les sujets suivants (souvent 1er-2e essai). ⚠️ **Palier
  de génération gratuit atteint en cours de session** — prévoir d'attendre le renouvellement du
  quota ou de repasser sur Gemini en attendant.

## État par projet (au moment de la rédaction)

| Projet | Fonction réelle (vérifiée dans le code) | Concept retenu | Statut |
|---|---|---|---|
| **Musique** | Rassemble ses morceaux favoris dans des playlists, alimentées depuis plusieurs plateformes de streaming. | Liste de lecture empilée (3 barres) + badge étoile (favoris) + lignes convergentes venant de la gauche (plusieurs plateformes) + note de musique au point de convergence. | ✅ Prête (meilleure version = régénération GPT, lignes lissées) — à télécharger et uploader. |
| **Mes avis** | Journal personnel et subjectif : le propriétaire teste des lieux (restos/cafés) et des produits, leur donne une note sur 10 selon son propre ressenti — pas un agrégateur public d'avis. | Une loupe qui examine une étoile. | ✅ Prête (Gemini, « Not bad »). |
| **Versus** | **Pas du sport** : logue des sessions de jeux (société ET vidéo — `versus/models.py` : `Joueur`, `Jeu`, `Partie`, `PartieJoueur`), calcule classements et ratios de victoire par joueur dans la durée. | Après plusieurs refus (podium+trophée = trop sportif ; dé+couronne = pas assez « versus » ; deux pions jumeaux = pas assez compétitif) : une tour d'échecs (jeu de société) et une manette (jeu vidéo), penchées l'une vers l'autre, lignes d'impact façon BD au point de contact. | ✅ Prête (Gemini, « ok »). Une régénération GPT avec le même concept a été demandée mais interrompue par le palier de génération — à retenter si voulu, sinon garder la version Gemini. |
| **Tracker** | Log un indicateur personnel récurrent dans le temps — soit un événement (occurrence), soit une mesure (`tracker/models.py` : `Tracker.type` = `evenement`/`mesure`) — pour en garder un historique consultable (fréquence, graphes). | Courbe ascendante avec quelques points, le dernier point plus gros/mis en avant (dernière entrée). | ✅ Prête (GPT, « Pas trop mal pour un 1er essai »). |
| **MySpot** | Carte personnelle : marque des lieux réels découverts, y attache photos et notes, partage possible en privé à des groupes précis plutôt qu'en public (`my_spot/models.py` : `Spot`, `SpotPhoto`, notes, `groupes` M2M vers `SpotGroup`, visibilité public/partagé/caché). | Épingle de carte avec une petite icône photo (montagne + soleil) à la place du point habituel. | ✅ Utilisable mais mitigé (GPT, « pourrait être mieux mais ça ira ») — à retenter si le propriétaire veut mieux. |
| **Super Moite Moite** | Tracker de tâches amélioré pour un couple/coloc : répartir équitablement les tâches ménagères récurrentes entre habitants d'un logement (`super_moite_moite/models.py` : `Logement.habitants` M2M vers `Profil`). | Une planchette/checklist coupée exactement en deux (moitié pleine jaune, moitié contour seul), une coche de chaque côté. | ⚠️ Prompt préparé, **résultat non confirmé/partagé dans cette session** — à générer/reconfirmer. |
| **Kendama Tricks** | Suit la pratique de tricks/combos/ladders de kendama, logue les tentatives, permet de revoir l'historique de fréquence de pratique (cf. [[06-kendama-a-preserver]] : `django-simple-history` sur `TrickPlayer`/`ComboPlayer` = cœur de l'UX). Cette vignette vit sur la home avec le thème principal du site — le thème « paper » autonome de kendama, lui, reste intouché. | Un kendama (pique + coupelle + balle sur fil) saisi en plein trick, balle en l'air, trait de trajectoire courbe. | ⚠️ Prompt préparé ; le propriétaire a dit « il s'en sort plutôt pas mal » (laisse penser qu'un bon résultat a été généré) mais **l'image n'a pas été partagée dans le chat pour confirmation**. |
| **Clips visuellement captivants** | Projet **externe** (`Projet.external=True`) — redirige vers un site tiers. | — | ✅ **Garder l'image actuelle** : c'est déjà une capture d'écran du site de destination, cohérent avec ce que l'utilisateur va voir en cliquant. Pas besoin d'y toucher. |
| **Liste des Fresques** | Projet **externe** (`Projet.external=True`). | — | ✅ **Garder l'image actuelle** (même raison que ci-dessus). |
| **Labyrinthe Game** | Projet **interne** (`Projet.external=False` — le jeu est servi par ce site, `base/templates/base/labyrinthe_game.html`). | — | ❓ **Pas encore traité.** Contrairement aux deux ci-dessus, ce n'est PAS un projet externe — la raison de « garder l'image actuelle » ne s'applique donc pas ici. Décision à prendre : générer une illustration IA (cohérent avec les autres projets internes) ou laisser tel quel. |

## Prompts détaillés déjà utilisés (pour reproduire ou reprendre l'itération)

Les prompts « Subject » complets validés pour Musique / Mes avis / Versus / Tracker / MySpot /
Super Moite Moite / Kendama Tricks sont conservés dans l'historique de la conversation Claude
Code où ce travail a été fait (session du 2026-07-19). Reformulation courte de chacun ci-dessus
dans le tableau ; si le fil de conversation n'est plus accessible, repartir de la fonction
réelle listée dans le tableau + la méthode « décrire ce que ça fait, un seul objet, pas de
collage » suffit à reconstruire un bon prompt.

## À faire (backlog, séparé de la génération d'images)

- [ ] Terminer la génération pour **Super Moite Moite**, **Kendama Tricks**, et statuer sur
  **Labyrinthe Game**.
- [ ] Uploader les images validées (Musique, Mes avis, Versus, Tracker, MySpot) dans
  `Projet.image` via l'admin.
- [ ] **Champ description par projet** (discuté mais différé) : ajouter `Projet.description_fr`
  / `Projet.description_en` (deux champs texte simples, PAS `django-modeltranslation` — le
  projet évite les dépendances neuves pour un besoin d'une dizaine de lignes) + une méthode de
  fallback qui choisit selon la langue active (repli sur le français si l'anglais est vide,
  cohérent avec la Phase 8/i18n EN qui reste différée). Pourquoi un champ dédié et pas
  `{% trans %}` : le mécanisme gettext ne traduit que les chaînes statiques trouvées par
  `makemessages` dans les templates/le code Python, pas le contenu de la base de données.
  Deux usages prévus : (1) description affichée dans le hero de chaque module (remplace les
  descriptions actuellement codées en dur, éparpillées par template) ; (2) un texte **toujours
  visible** (pas au survol — casse l'accessibilité mobile/clavier) sous le titre de la carte
  sur la home.
