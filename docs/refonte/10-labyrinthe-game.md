# Jeu Labyrinthe — palette, dark mode, mobile et corrections

> Chantier réalisé le **2026-08-03**, à la demande du propriétaire (« mettre à jour mon jeu de
> labyrinthe », palette de la refonte + dark mode). Il était listé en backlog basse priorité dans
> [09-images-projets-ia.md](09-images-projets-ia.md) ; il est fait, et il est allé plus loin que la
> seule palette (bugs et jouabilité mobile).

## Périmètre

Le jeu vit dans `base/static/base/js/labyrinthe_game/` (p5.js, mode global, une classe par fichier)
et `base/templates/base/labyrinthe_game.html`. Il n'utilise **pas** de build : les fichiers sont
chargés en `<script>` classiques, qui partagent un seul scope global.

## 1. Palette et thème clair/sombre

Le problème n'était pas cosmétique : les couleurs étaient des primaires pures RVB (`#00ff00`,
`#ff0000`, `#00ffff`, `#0000ff`, `#ffff00`) codées en dur et **éparpillées sur 5 fichiers**, avec un
fond `color(255)` — donc un jeu blanc éclatant même en thème sombre.

**Solution** : un nouveau `Palette.js` lit les tokens `--ds-*` de `assets/css/main.css` via
`getComputedStyle`, à l'init puis à chaque bascule de thème. Il se branche sur l'événement
`benbb96:themechange` émis par `assets/js/theme.js` — **le même patron que
`tracker/static/tracker/js/common.js` pour Chart.js**, qui existait déjà.

| Élément | Avant | Token |
|---|---|---|
| Fond du terrain | `color(255)` | `--ds-surface` |
| Murs + contour | `color(4)` | `--ds-text` (s'inverse donc en sombre) |
| Joueur | `#ffff00` + contour noir | `--ds-primary` + contour `--ds-primary-ink` |
| Joueur en déplacement souris | `#e69646` | `--ds-warning` |
| Départ | `#00ff00` | `--ds-success` |
| Arrivée | `#ff0000` | `--ds-danger` |
| Tracé du parcours | `#00ffff` | `--ds-info` |
| Cases visitées (touche P) | `#0000ff` **opaque** | `--ds-info` à alpha 38 |
| Pop-ups | blanc alpha 200 + texte noir | `--ds-surface` alpha 249, bord `--ds-border-strong`, texte `--ds-text` |
| Boutons du menu | vert/orange/rouge/bleu purs | success / warning / danger / info |

Le joueur porte le **jaune de marque en aplat avec contour foncé** : c'est le seul usage du jaune
autorisé par la charte, et il tombe juste — c'est l'élément le plus important du terrain.

### Deux pièges à connaître si on y retouche

1. **`color(unePaletteColor)` retourne le MÊME objet en p5 1.x** (compatibilité ascendante) et
   `setAlpha()` le mute sur place. Toute variante transparente doit repartir des composantes, sinon
   on altère la couleur partagée de la palette pour tout le reste du jeu → d'où le helper
   `withAlpha()` de `Palette.js`.
2. **Le mode Blind fait varier l'alpha des murs.** `Wall.js` faisait `color(4, this.alpha)`, un
   niveau de gris + alpha. Avec un token hexadécimal il faut passer par `withAlpha()`, sinon les
   murs ne s'effacent plus et le mode Blind est cassé. `this.alpha` devient volontairement négatif
   (compte à rebours du game over), `withAlpha()` le borne à 0.
3. `refreshPalette()` ne doit être appelé qu'**après** l'init de p5 (`color()` n'existe pas avant
   `setup()`) — d'où la garde `typeof color !== 'function'`, utile car `theme.js` peut émettre son
   événement avant que p5 ne soit prêt.

### Accessibilité : départ et arrivée ne se distinguent plus que par la teinte

Vert et rouge sont confondus en daltonisme rouge-vert (deutan/protan, ~8 % des hommes) — et ce sont
les deux repères les plus utiles du terrain. Ils ont donc désormais des **formes différentes** :

- **départ** = carré évidé (repère discret, on l'a quitté) ;
- **arrivée** = cible (anneau + disque plein au centre).

## 2. Bugs corrigés

| Bug | Détail |
|---|---|
| **Touche A plantait** | `Labyrinthe.resetAlpha()` bouclait sur `walls`, qui n'existe pas (aucune globale de ce nom) → `ReferenceError`. La touche documentée dans le template ne faisait **rien**. Corrigé en `this.walls`. |
| **Spam sonore** | `draw()` appelle `player.move()` à chaque frame tant qu'une flèche est tenue ; collé à un mur, ça jouait ~60 « aïe » par seconde. Cooldown `WALL_SOUND_COOLDOWN` (350 ms) dans `Player.js`. Vérifié : 300 tentatives bloquées d'affilée → 1 son. |
| **Chrono faux** | `Timer` utilisait `round()` sur chaque unité : 1 min 50 s s'affichait « 2m 50s », 1,6 s « 2s 600ms ». Remplacé par un `formatDuration()` en `floor()`, testé sur 6 cas. |
| **Matrice O(n⁴)** | `Labyrinthe` allouait une matrice d'adjacence `nbCase² × nbCase²`. Au niveau 20 en Hard (`nbCase = 61`) : **105,8 Mo mesurés** par régénération, alors que le jeu est conçu pour monter indéfiniment. Remplacée par un masque de bits d'un octet par case (`passages`, `Uint8Array`) : **3,6 Ko**, soit ~30 000× moins. |
| **Zone de clic du menu** | `Button.mouseOver()` ne testait qu'une bande horizontale et `mouseX < width / 2` : on lançait une partie en cliquant loin du texte. Vraie boîte englobante, calculée à la taille de texte de référence (et non courante, sinon elle grandirait au survol pendant qu'on la teste). |
| **Transitions d'écran répétées** | `draw()` testait `mouseIsPressed` à chaque frame : un bouton maintenu enchaînait plusieurs écrans. Déplacé dans `mousePressed()`. |
| **Numéro de niveau sur le marqueur de départ** | Il était dessiné dans la case (0, 0) — pile là où le départ se trouve toujours en mode Easy. Retiré du canvas : le HUD l'affiche en permanence. |
| **Aucun son ne sortait** (pré-existant, signalé par le propriétaire) | Les navigateurs créent l'`AudioContext` en état **`suspended`** et **p5.sound ne le réveille pas tout seul** : il expose `userStartAudio()` mais ne l'appelle jamais et n'installe aucun écouteur de geste (vérifié dans `p5.sound.min.js`). Résultat : `loadSound()` réussit, `isLoaded()` renvoie `true`, `play()` est bien appelé… et rien ne sort. Symptôme console : « An AudioContext was prevented from starting automatically ». Corrigé dans `Hud.js` par `unlockAudio()`, appelé depuis des écouteurs `pointerdown`/`keydown` en capture sur `document` — un point d'entrée unique qui couvre le canvas, le pavé, les boutons du HUD et le clavier. **Ce n'était pas une régression de ce chantier** : l'ancien code appelait `.play()` directement, sans resume non plus. |

## 3. Jouabilité mobile

Le canvas était figé à **444×444 px** (débordement sur un mobile de 360 px) et il n'existait
**aucune commande tactile** : le jeu était simplement injouable au doigt.

- `canvasSize()` suit la largeur disponible, plafonnée par `windowHeight * 0.75` (sinon un mobile en
  paysage donnerait un terrain plus haut que l'écran), bornée à 240–600 px. `windowResized()`
  recale le canvas **et** les positions des boutons du menu. Vérifié : la partie survit au
  redimensionnement (niveau et position conservés, taille des cases recalculée).
- **Pavé directionnel HTML** (`.ds-laby__pad`, 3×3, cibles de 3,25 rem ≥ 44 px) sous le terrain,
  utilisable aussi à la souris.
- **Appui sur une case voisine** pour s'y déplacer d'un pas — adjacence **stricte** ici, alors que
  le suivi de souris tolère l'écart sur l'autre axe (c'est cette tolérance qui le rend jouable).
- Volontairement **pas de balayage** : `touch-action: none` ou un `preventDefault` sur le canvas
  piégerait le défilement de la page pour qui veut juste faire défiler au-delà du jeu.
- Le suivi de souris est réservé aux pointeurs fins (`matchMedia('(pointer: fine)')`) : au tactile,
  `mouseX/mouseY` restent figés sur le dernier appui et le joueur « suivrait » un doigt absent.
- `MovingLine` : la taille de ligne valait 60 px en dur, calibrés pour le canvas de 444 px. Elle est
  désormais relative (`lineSize()`), comme les proportions de l'écran d'accueil.

## 4. Confort de jeu

- **HUD en HTML** (`.ds-laby__hud`) : mode, niveau, chrono, record. En HTML plutôt que dessiné dans
  le canvas → thémé par le CSS, sélectionnable, atteignable en navigation clavier. `draw()` tourne à
  60 fps donc `updateHud()` n'écrit dans le DOM que quand une valeur change. Dans le menu, le HUD
  affiche le mode **surligné** et son record (sinon on lisait « mode — » à côté d'un record dont on
  ignorait le mode).
- **Bouton muet** — les sons se déclenchaient sans aucun moyen de les couper.
- **Records en `localStorage`** (`benbb96-labyrinthe-best`) : plus haut niveau atteint et meilleur
  temps sur un labyrinthe, **par mode**. Le jeu n'avait aucune mémoire alors que sa boucle est faite
  pour battre son record. Échec de `localStorage` (navigation privée) toléré silencieusement.
- **Entrées unifiées** : clavier, souris et pavé passent tous par `inputDirection()` /
  `inputConfirm()` / `inputPause()`, au lieu de trois copies de la même logique.
- **i18n** : le tableau des touches spéciales était en français en dur, sans `{% trans %}` — trou
  dans le bilingue. Catalogues `base/locale/{fr,en}` régénérés (les `msgstr` EN restent vides, comme
  tout le reste de l'app : la traduction EN est différée, cf. Phase 8).
- **`base/static/base/js/p5.js` supprimé** : 4,3 Mo non minifiés, committés mais jamais chargés (le
  template ne référence que `p5.min.js`).

## 5. CSS

Nouvelle **section 21** de `assets/css/main.css` (`.ds-laby*`) : cadre du terrain, HUD, pavé.
Deux points non évidents y sont commentés :

- `.ds-laby` est plafonné à **600 px**, valeur qui doit rester **alignée sur le plafond de
  `canvasSize()`** : c'est la largeur de ce conteneur que le JS mesure.
- `.ds-laby__stage` n'a **pas de padding** : `canvasSize()` lit `clientWidth`, qui l'inclurait, et
  le terrain déborderait de son cadre.

## 6. Vérifications passées

- `manage.py check`, `djlint --lint` sur le template (0 erreur), les **27 tests de `smoke_tests`**.
- Harnais Node avec stub p5 : sur 9 combinaisons mode × taille (jusqu'à 31×31), **tous les
  labyrinthes générés sont connexes** (n² cases atteignables via `Player.canMove`), l'arrivée est
  toujours accessible, et le nombre de murs correspond à l'invariant de l'arbre couvrant
  (`2n(n−1) − (n²−1)`). C'est ce qui valide le remplacement de la matrice d'adjacence.
- Pilotage de Chromium headless en CDP, thèmes clair **et** sombre : palette correctement lue depuis
  le CSS, murs inversés (`#1c1912` → `#f3efe3`), bascule de thème **en cours de partie** sans
  interrompre la partie, pause/reprise, anti-spam sonore, bouton muet, pavé directionnel,
  redimensionnement, **zéro erreur console**.
- Audio : contexte `suspended` au chargement → **`running` après un geste de confiance** (émis via
  `Input.dispatchMouseEvent`), et `play()` déclenché avec un contexte actif.

> ⚠️ **Piège de test à ne pas refaire.** La première passe lançait Chromium avec
> `--autoplay-policy=no-user-gesture-required`, ce qui **masquait complètement** le blocage de
> l'`AudioContext` : tous les tests audio passaient alors qu'aucun son ne sortait dans un vrai
> navigateur. Ne jamais neutraliser une politique du navigateur dans un test censé valider le
> comportement réel — et pour l'audio, vérifier l'**état du contexte**, pas seulement que `play()`
> a été appelé.

## 7. Reste à faire

- [ ] **Synchroniser `media/projet/Labyrinthe_Game.png` côté prod (GCS).** Le screenshot a été
  regénéré en local (800×500, cadrage 16/10 comme les vignettes générées) mais `media/` est
  gitignoré et, en dev, `MEDIA_URL` pointe sur le bucket GCS : l'image locale ne s'affiche pas.
  À faire avec les autres uploads différés listés dans [09-images-projets-ia.md](09-images-projets-ia.md).
- [ ] Optionnel : **charger `p5.sound.min.js` paresseusement** (au premier geste) plutôt qu'au
  chargement de la page. Double bénéfice : ça retire l'avertissement console
  « An AudioContext was prevented from starting automatically » (émis à la **création** du contexte,
  donc au chargement du script — `unlockAudio()` le répare mais ne peut pas l'empêcher), et ça
  économise **200 Ko** au premier rendu pour 5 sons courts. Demande de sortir les `loadSound()` de
  `preload()`.
- [ ] Optionnel : l'easter egg des lignes animées de l'écran d'accueil (`MovingLine`) a des bugs
  d'animation connus et assumés depuis l'origine (cf. commit `7a31d86`, « didn't manage to fix
  bugs ^^' »). Non touché ici.
