// Générateur de Labyrinthe
// Jeu crée et développé par Benjamin Bernard-Bouissières

// Le but du jeu est évidemment de traverser des labyrinthes qui sont génénés aléatoirement grâce
// à un algorithme appelé le Recursive Backtracker (voir sur http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)

// Les couleurs ne sont plus codées en dur : elles viennent des tokens --ds-* du
// design system et suivent le thème clair/sombre du site (voir Palette.js).
// Niveau, chrono, record, pavé directionnel et bouton muet vivent hors du canvas,
// en HTML (voir Hud.js).

// Instanciation des variables globales
let player;
let niveau = 1;

// Valeurs de défaut du jeu pouvant être altérés par les différents modes
let nbCaseDefaut;
let incrementationDefaut;

let nbCase;  // Nombre de case actuel
let tailleX;  // Taille largeur en pixel d'une case
let tailleY;  // Taille hauteur en pixel d'une case

let labyrinthe;  // Le labyrinthe du jeu
let passages;  // Passages ouverts entre cases (un octet par case, cf. Labyrinthe.js)
let grille;  // Grille qui va nous servir pour la construction du labyrinthe

// Les différents états du jeu
let MENU = 1;
let GAME = 4;
let LEVEL_UP = 44;
let GAME_OVER = 13;
let PAUSE = 10;
let state = MENU;  // La variable de l'état de jeu servant à déterminer quel écran afficher

// Les différents modes de jeu
let EASY = 1;
let MEDIUM = 2;
let HARD = 3;
let BLIND = 4;
let mode = MEDIUM;  // La variable du mode de jeu pour définir les paramètres de jeu

// Les boutons du menus
let buttons = [];
let selectedButton;

// Les lignes d'animations pour l'écran d'accueil
let lines = [];

// Le timer qui sera utilisé pour chronométrer le temps passé dans un labyrinthe
let timer;

// Correspondance entre les commandes du pavé tactile (data-laby-dir) et les
// constantes de touches de p5, pour que clavier et tactile empruntent le même
// chemin (voir inputDirection).
let DIRECTION_KEYS;

// Le suivi à la souris n'a de sens qu'avec un pointeur fin : sur un écran
// tactile, mouseX/mouseY restent figés sur le dernier appui après le relâchement,
// et le joueur se mettrait à « suivre » un doigt qui n'est plus là.
const hasFinePointer = window.matchMedia('(pointer: fine)').matches;

// ============================================================================================================================================

function resetMovingLines() {
    // Construction des Moving Lines avec leurs animations prédéfinis
    lines[0] = new MovingLine(createVector(0, 1), createVector(1, 0), [4, 0, 3, 5, 6, 3, 4, 4, 0, 3, 5, 6, 3, 4, 3, 4, 4, 6, 4, 4, 3, 4, 2, 2, 6, 4, 4, 3]);
    lines[1] = new MovingLine(createVector(2, 0), createVector(0, 1), [4, 2, 1, 5, 2, 2, 1, 2, 4, 3, 6, 4, 4, 3, 3, 0, 2, 6, 5, 1, 2, 2, 0, 2, 5, 6, 3, 4]);
    lines[2] = new MovingLine(createVector(1, 1), createVector(0, 1), [3, 0, 4, 4, 5, 2, 0, 1, 0, 2, 2, 6, 4, 0]);
    lines[3] = new MovingLine(createVector(1, 2), createVector(1, 0), [4, 5, 1, 6, 3, 5, 1, 2, 6, 3, 5, 1, 6, 3]);
}

let wallSounds;
let successSound;

function preload() {
    wallSounds = ['aie', 'ouille', 'ah', 'oh'].map((sound) => loadSound(`/static/base/js/labyrinthe_game/sounds/${sound}.mp3`));
    successSound = loadSound(`/static/base/js/labyrinthe_game/sounds/ouais.mp3`);
}

// Taille du terrain, carré, calée sur la largeur réellement disponible.
// Le canvas était figé à 444×444 px : sur un mobile en 360 px de large il
// débordait, et il n'y avait de toute façon aucune commande tactile.
function canvasSize() {
    const holder = document.getElementById('sketch-holder');
    const available = holder && holder.clientWidth ? holder.clientWidth : 444;
    // On plafonne aussi sur la hauteur du viewport : sur un mobile en paysage,
    // suivre la seule largeur donnerait un terrain plus haut que l'écran.
    return constrain(floor(min(available, windowHeight * 0.75)), 240, 600);
}

function setup() {
    const size = canvasSize();
    let canvas = createCanvas(size, size);
    canvas.parent('sketch-holder');

    // Les constantes de touches de p5 n'existent qu'à partir d'ici
    DIRECTION_KEYS = { up: UP_ARROW, down: DOWN_ARROW, left: LEFT_ARROW, right: RIGHT_ARROW };

    refreshPalette();  // Lecture des tokens --ds-* du thème courant
    loadBests();       // Records enregistrés en localStorage
    background(PALETTE.bg);

    buildButtons();
    resetMovingLines();
}

function windowResized() {
    const size = canvasSize();
    resizeCanvas(size, size);
    buildButtons();  // Les positions des boutons dépendent de width/height
}

// Construction (ou repositionnement) des boutons du menu
function buildButtons() {
    const previouslySelected = selectedButton === undefined ? 1 : selectedButton;
    buttons = [
        new Button(0, "Easy", width / 4, (height * 5 / 9), EASY),
        new Button(1, "Medium", width / 4, (height * 6 / 9), MEDIUM),
        new Button(2, "Hard", width / 4, (height * 7 / 9), HARD),
        new Button(3, "Blind", width / 4, (height * 8 / 9), BLIND),
    ];
    selectedButton = previouslySelected;  // Le mode medium est sélectionné par défaut
    buttons[selectedButton].selected = true;
}

function draw() {
    //A quelle état sommes-nous ?
    switch (state) {

        case MENU :
            // Affichage du menu
            background(PALETTE.bg);
            push();
            fill(PALETTE.wall);
            noStroke();
            textAlign(RIGHT, BASELINE);
            textSize(width / 13);
            text("Le Labyrinthe Infini", width * 0.89, height / 4);
            pop();

            drawAnimatedMaze();

            // Affichage des boutons
            for (let i = 0; i < buttons.length; i++) {
                buttons[i].display();
            }
            break;

        case GAME :
            // Raffraichissement de la couleur de fond
            background(PALETTE.bg);

            // Déplacement du joueur via les touches du clavier
            if (keyIsPressed) {
                player.move(keyCode);
            }

            displayGame(false);  // On affiche le jeu et on n'empêche pas le joueur de bouger
            break;

        case LEVEL_UP :
            background(PALETTE.bg);
            displayGame(true);
            popUp("Bravo !\nNiveau " + niveau + "\nTemps : " + timer.getDisplay() + "\nAppuyez sur Entrée\nou cliquez pour continuer");
            break;

        case GAME_OVER :
            background(PALETTE.bg);
            displayGame(true);
            popUp("Game Over !\nNiveau " + niveau + "\nAppuyez sur Entrée\nou cliquez pour revenir au menu");
            break;

        case PAUSE :
            background(PALETTE.bg);
            displayGame(true);
            popUp("Pause\nNiveau " + niveau + "\nTemps : " + timer.getDisplay() + "\nEntrée pour revenir au menu\nX ou clic pour reprendre");
            break;

        default :
            background(PALETTE.end);
    }

    updateHud();
}

// Fonction de recalcul de la taille du case en fonction de la taille de la fenêtre
function updateCaseSize() {
    tailleX = width / nbCase;
    tailleY = height / nbCase;
}

// Fonction affichant correctement le terrain de jeu et défini si le joueur peut bouger ou non
function displayGame(stopPlayer) {
    updateCaseSize();  // Recalcul de la taille d'une case
    labyrinthe.display();  // Affichage du labyrinthe
    if (stopPlayer) {
        player.isMoving = false;  // On empêche le joueur de bouger pendant les différents menus
    }
    player.update();  // Met à jour la position du joueur
}

// ── Entrées ─────────────────────────────────────────────────────────────────
// Clavier, souris et pavé tactile passent tous par inputDirection / inputConfirm
// / inputPause, pour que la logique de jeu ne soit pas écrite trois fois.

function inputDirection(direction) {
    switch (state) {
        case MENU :
            // Sélection des boutons du menu
            if (direction === UP_ARROW && selectedButton > 0) {
                buttons[selectedButton].selected = false;
                selectedButton--;
                buttons[selectedButton].selected = true;
            } else if (direction === DOWN_ARROW && selectedButton < buttons.length - 1) {
                buttons[selectedButton].selected = false;
                selectedButton++;
                buttons[selectedButton].selected = true;
            }
            break;
        case GAME :
            player.move(direction);
            break;
    }
}

// Équivalent de la touche Entrée / du clic : valide l'écran courant
function inputConfirm() {
    switch (state) {
        case MENU :
            buttons[selectedButton].chargeMode();
            runGame();
            break;
        case LEVEL_UP :
            levelUp();
            break;
        case GAME_OVER :
            gameOver();
            break;
        case PAUSE :
            gameOver();  // Le jeu est terminé, on appelle donc Game Over
            break;
    }
}

// Bascule pause / reprise (touche X, Échap, bouton du HUD)
function inputPause() {
    if (state === GAME) {
        timer.pause();
        state = PAUSE;
    } else if (state === PAUSE) {
        timer.restart();
        state = GAME;
    }
}

// Les transitions d'écran se font à l'appui plutôt que dans draw() : la version
// précédente testait mouseIsPressed à chaque frame, donc un bouton maintenu
// enchaînait plusieurs écrans d'affilée.
function mousePressed() {
    switch (state) {
        case MENU :
            for (let i = 0; i < buttons.length; i++) {
                if (buttons[i].mouseOver()) {
                    buttons[i].chargeMode();
                    runGame();
                    return;
                }
            }
            break;
        case LEVEL_UP :
            levelUp();
            break;
        case GAME_OVER :
            gameOver();
            break;
        case PAUSE :
            timer.restart();
            state = GAME;
            break;
        case GAME :
            if (player.overPlayer) {
                // Clic sur le joueur : (dés)active le suivi de souris
                if (hasFinePointer) player.isMoving = !player.isMoving;
            } else if (!player.isMoving) {
                // Appui sur une case voisine : on s'y déplace d'un pas. C'est la
                // commande naturelle au doigt, et elle ne piège pas le
                // défilement de la page comme le ferait un balayage.
                // Adjacence STRICTE ici, contrairement au suivi de souris qui
                // tolère l'écart sur l'autre axe : un appui doit désigner sans
                // ambiguïté une seule case.
                const dx = floor(mouseX / tailleX) - int(player.posOnGrid.x);
                const dy = floor(mouseY / tailleY) - int(player.posOnGrid.y);
                if (abs(dx) + abs(dy) === 1) {
                    if (dx === 1) inputDirection(RIGHT_ARROW);
                    else if (dx === -1) inputDirection(LEFT_ARROW);
                    else if (dy === 1) inputDirection(DOWN_ARROW);
                    else inputDirection(UP_ARROW);
                }
            }
            break;
    }
}

// Fonction à l'appui d'une touche
function keyPressed() {
    switch (state) {
        case MENU :
            if (keyCode === ENTER) inputConfirm();
            else inputDirection(keyCode);
            break;
        case GAME :
            if (keyCode === ESCAPE) {
                inputPause();
                break;
            }
            // Les flèches sont traitées dans draw() tant qu'elles sont maintenues
            // (déplacement rapide) — rien à faire à l'appui.
            if (keyCode >= LEFT_ARROW && keyCode <= DOWN_ARROW) break;
            switch (key) {
                // Déplacement du joueur avec ZQSD
                case 'z' :
                    inputDirection(UP_ARROW);
                    break;
                case 's' :
                    inputDirection(DOWN_ARROW);
                    break;
                case 'q' :
                    inputDirection(LEFT_ARROW);
                    break;
                case 'd' :
                    inputDirection(RIGHT_ARROW);
                    break;
                case 'r' :
                    state = GAME_OVER;
                    break;  // RESET
                case 'l' :
                    levelUp();
                    break;
                case 'p' :
                    player.point = !player.point;
                    break;
                case 'c' :
                    player.chemin = !player.chemin;
                    break;
                case 'a' :
                    labyrinthe.resetAlpha();
                    break;
                case 'b' :
                    labyrinthe.disappear = !labyrinthe.disappear; // Toggle le BLIND mode
                    break;
                case 'w' :
                    console.log('case', player.posOnGrid.x + ',' + player.posOnGrid.y, '— index', player.cellIndex());
                    break;
                case 'x' :
                    inputPause();
                    break;
            }
            break;
        case LEVEL_UP :
        case GAME_OVER :
            if (keyCode === ENTER) inputConfirm();
            break;
        case PAUSE :
            if (keyCode === ENTER) inputConfirm();
            else if (key === 'x' || keyCode === ESCAPE) inputPause();
            break;
    }
}

// Fonction qui permet de lancer le jeu
function runGame() {
    // Calcul de la taille d'une case
    updateCaseSize();

    // Création du Labyrtinthe
    labyrinthe = new Labyrinthe();

    // Création du joueur
    player = new Player();

    state = GAME;  // On passe à l'état de Jeu

    timer = new Timer(); // Enfin, on instancie et démarre le timer
}

// Fonction qui fait passer le jeu au niveau supérieur
function levelUp() {
    niveau++;  // La fonction ne s'appelle pas level Up pour rien !
    nbCase += incrementationDefaut;
    recordLevel(niveau);  // Record du plus haut niveau atteint dans ce mode
    // Création d'un nouveau Labyrtinthe
    labyrinthe = new Labyrinthe();
    player.repositionne(labyrinthe.startCase.x, labyrinthe.startCase.y);
    player.isMoving = false;

    timer = new Timer();  // On crée un nouveau timer pour ce nouveau niveau
    state = GAME;
}

// Fonction de transition pour revenir au menu correctement
function gameOver() {
    recordLevel(niveau);
    niveau = 1;  // Reset le niveau

    // Remise à 0 des Moving Lines
    resetMovingLines();

    state = MENU; // On retourne au Menu si Game Over
}

// Fonction permettant l'affichage d'une pop-up un peu transparente avec un message
function popUp(message) {
    push();
    fill(PALETTE.panelFill);
    stroke(PALETTE.panelBorder);
    strokeWeight(1);
    rect(width / 6, (height * 2 / 6), (width * 4) / 6, (height * 2) / 6, 8);
    noStroke();
    fill(PALETTE.text);
    textSize(width / 30);
    textAlign(CENTER, CENTER);
    text(message, width / 2, height / 2);
    pop();
}

// Fonction pour afficher le labyrinthe animé de l'écran de démarrage
function drawAnimatedMaze() {
    push();
    noFill();
    stroke(PALETTE.wall);
    strokeWeight(4);
    // Proportions du canvas d'origine (220/444 et 180/444), désormais relatives
    translate(width * 0.495, height * 0.495);
    rect(0, 0, width * 0.405, height * 0.405);
    for (let i = 0; i < lines.length; i++) {
        lines[i].show();
    }
    pop();
}

// Empêche de scroller la page
window.addEventListener("keydown", function(e) {
    // space and arrow keys
    if(['Space', 'ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown'].indexOf(e.code) > -1) {
        e.preventDefault();
    }
});
