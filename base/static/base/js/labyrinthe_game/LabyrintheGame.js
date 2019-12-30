// Générateur de Labyrinthe
// Jeu crée et développé par Benjamin Bernard-Bouissières

// Le but du jeu est évidemment de traverser des labyrinthes qui sont génénés aléatoirement grâce
// à un algorithme appelé le Recursive Backtracker (voir sur http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)

// Instanciation des variables globales
let player;
let niveau = 1;
let delai = 0;

// Valeurs de défaut du jeu pouvant être altérés par les différents modes
let nbCaseDefaut;
let incrementationDefaut;

let nbCase;  // Nombre de case actuel
let tailleX;  // Taille largeur en pixel d'une case
let tailleY;  // Taille hauteur en pixel d'une case

let labyrinthe;  // Le labyrinthe du jeu
let matrice;  // Matrice d'adjacence du jeu pour savoir si on a le droit de se déplacer d'une case à l'autre ou non
let grille;  // Grille qui va nous servir pour la construction du labyrinthe

let backgroundColor;  // Couleur du fond de jeu
let wallColor;  // Couleur des murs du labyrinthe
let disappear = false;  // Permet de choisir si les murs du labyrinthe disparaissent ou non

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
let mode;  // La variable du mode de jeu pour définir les paramètres de jeu

// Les boutons du menus
let buttons = [];
let selectedButton;

// Les sélecteurs de couleurs
// let backgroundColorPicker = undefined;
// let wallColorPicker = undefined;

// Les lignes d'animations pour l'écran d'accueil
let lines = [];

// Le timer qui sera utilisé pour chronométrer le temps passé dans un labyrinthe
let timer;

// ============================================================================================================================================

function resetMovingLines() {
    // Construction des Moving Lines avec leurs animations prédéfinis
    lines[0] = new MovingLine(createVector(0, 1), createVector(1, 0), [4, 0, 4, 6, 4, 4, 3, 4, 2, 2, 6, 5, 1, 2, 2, 0, 2, 5, 2, 2, 1, 2, 4, 4, 5, 6, 3, 4]);
    lines[1] = new MovingLine(createVector(2, 0), createVector(0, 1), [4, 2, 2, 6, 5, 1, 2, 2, 0, 2, 5, 2, 2, 1, 2, 4, 4, 5, 6, 3, 4, 4, 0, 4, 6, 4, 4, 3]);
    lines[2] = new MovingLine(createVector(1, 1), createVector(0, 1), [3, 0, 4, 4, 5, 2, 0, 1, 0, 2, 2, 6, 4, 0]);
    lines[3] = new MovingLine(createVector(1, 2), createVector(1, 0), [4, 5, 1, 6, 3, 5, 1, 2, 6, 3, 5, 1, 6, 3]);
}

function setup() {
    let canvas = createCanvas(444, 444);
    canvas.parent('sketch-holder');

    backgroundColor = color(255);
    wallColor = color(4);
    background(backgroundColor);

    //Construction des boutons du menu
    buttons = [];  // Tableau des boutons
    buttons[0] = new Button(0, "Easy", width / 4, (height * 5 / 9), EASY, color(0, 255, 0));
    buttons[1] = new Button(1, "Medium", width / 4, (height * 6 / 9), MEDIUM, color(255, 165, 0));
    buttons[2] = new Button(2, "Hard", width / 4, (height * 7 / 9), HARD, color(255, 0, 0));
    buttons[3] = new Button(3, "Blind", width / 4, (height * 8 / 9), BLIND, color(60, 60, 255));
    buttons[1].selected = true;  // Le mode medium est sélectionné par défaut
    selectedButton = 1;

    // Construction des ColorPickers
    // backgroundColorPicker = new ColorPicker(20, 20, wallColor);
    // wallColorPicker = new ColorPicker(20, 60, backgroundColor);

    resetMovingLines();
}

function draw() {
    //A quelle état sommes-nous ?
    switch (state) {

        case MENU :
            // Affichage du menu
            background(backgroundColor);
            push();
            fill(wallColor);
            textAlign(RIGHT);
            textSize(width / 13);
            strokeWeight(3);
            text("Le Labyrinthe Infini", width - 50, height / 4);
            pop();

            drawAnimatedMaze();

            // Affichage des boutons
            for (let i = 0; i < 4; i++) {
                buttons[i].display();
            }

            // Color Picker
            // fill(wallColor);
            // textAlign(LEFT);
            // textSize(12);
            // text("Couleur de fond", 50, 35);
            // text("Couleur des murs", 50, 75);
            // backgroundColorPicker.display();
            // wallColorPicker.display();

            if (mouseIsPressed) {
                for (let i = 0; i < 4; i++) {
                    if (buttons[i].mouseOver()) {
                        buttons[i].chargeMode();
                        runGame();
                    }
                }
            }
            break;

        case GAME :
            // Raffraichissement de la couleur de fond
            background(backgroundColor);

            // Déplacement du joueur via les touches du clavier
            if (keyPressed) {
                player.move(keyCode);
                //delay(delai);
            }

            displayGame(false);  // On affiche le jeu et on n'empêche pas le joueur de bouger
            if (mouseIsPressed) {
                // Si le joueur essaye de déplacer son personnage en cliquant sur celui-ci
                player.isMoving = !player.isMoving && player.overPlayer;
            }
            break;

        case LEVEL_UP :
            background(backgroundColor);
            displayGame(true);
            popUp("Bravo !\nNiveau " + niveau + "\nTemps : " + timer.getDisplay() + "\nAppuiez sur Entrée\n Ou cliquez pour continuer");
            if (mouseIsPressed) {
                levelUp();
            }
            break;

        case GAME_OVER :
            background(backgroundColor);
            displayGame(true);
            popUp("Game Over !\nNiveau " + niveau + "\nAppuiez sur Entrée\n Ou cliquez pour revenir au menu");
            if (mouseIsPressed) {
                gameOver();
            }
            break;

        case PAUSE :
            background(backgroundColor);
            displayGame(true);
            popUp("Pause\nNiveau " + niveau + "\nTemps : " + timer.getDisplay() + "\nAppuiez sur Entrée\npour revenir au menu");
            if (mouseIsPressed) {
                if (mode === BLIND) {
                    disappear = true;  // On remet la disparition des murs
                }
                timer.restart();  // On relance le timer
                state = GAME;
            }
            break;

        default :
            background(255, 0, 0);
    }
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
    player.update();  //Met à jour la position du joueur
    if (stopPlayer) {
        player.isMoving = false;  // On empêche le joueur de bouger pendant les différents menus
    }
}

// Fonction à l'appui d'une touche
function keyPressed() {
    switch (state) {
        case MENU :
            // A l'appui de la touche Entrée, on charge le mode sélectionné
            if (keyCode === ENTER) {
                for (let i = 0; i < 4; i++) {
                    if (buttons[i].selected) {
                        buttons[i].chargeMode();
                        runGame();
                    }
                }
            }
            // Sélection des boutons du menu avec les touches du clavier
            else if (keyCode === UP_ARROW && selectedButton > 0) {
                buttons[selectedButton].selected = false;
                selectedButton--;
                buttons[selectedButton].selected = true;
            } else if (keyCode === DOWN_ARROW && selectedButton < 3) {
                buttons[selectedButton].selected = false;
                selectedButton++;
                buttons[selectedButton].selected = true;
            }
            break;
        case GAME :
            switch (key) {
                // Déplacement du joueur avec ZQSD
                case 'z' :
                    player.move(UP_ARROW);
                    break;
                case 's' :
                    player.move(DOWN_ARROW);
                    break;
                case 'q' :
                    player.move(LEFT_ARROW);
                    break;
                case 'd' :
                    player.move(RIGHT_ARROW);
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
                    disappear = !disappear;
                    break; //Active le BLIND mode
                case 'w' :
                    condole.log(player.posOnMatrice());
                    break;
                case 'x' :
                    // La touche X permet de mettre le jeu en pause
                    key = 0;  // Empêche le jeu de se fermer
                    timer.pause();  // On met le timer en pause
                    if (mode === BLIND) {  // Dans ce mode on stoppe la disparition des murs
                        disappear = false;
                    }
                    state = PAUSE;
                    break;
            }
            break;
        case LEVEL_UP :
            if (keyCode === ENTER) {
                levelUp();
            }
            break;
        case GAME_OVER :
            if (keyCode === ENTER) {
                gameOver();
            }
            break;
        case PAUSE :
            if (keyCode === ENTER) {
                gameOver();  // Le jeu est terminé, on appelle donc Game Over
            } else if (key === 'x') {
                key = 0;
                if (mode === BLIND) {
                    disappear = true;  // On remet la disparition des murs
                }
                timer.restart();  // On relance le timer
                state = GAME;
            }
            break;
    }
}

// Fonction lors du relachement du clic de la souris
/*function mouseReleased() {
    backgroundColorPicker.isDraggingCross = false;
    backgroundColorPicker.isDraggingLine = false;
    wallColorPicker.isDraggingCross = false;
    wallColorPicker.isDraggingLine = false;

    if (backgroundColorPicker.closeColorPicker()) {
        backgroundColorPicker.ShowColorPicker = false;
        backgroundColor = backgroundColorPicker.activeColor;
    } else if (wallColorPicker.closeColorPicker()) {
        wallColorPicker.ShowColorPicker = false;
        wallColor = wallColorPicker.activeColor;
    }
}*/

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
    // Création d'un nouveau Labyrtinthe
    labyrinthe = new Labyrinthe();
    player.repositionne(labyrinthe.startCase.x, labyrinthe.startCase.y);
    player.isMoving = false;

    if (mode === BLIND) {  // On remet la disparition des murs
        disappear = true;
    }
    timer = new Timer();  // On crée un nouveau timer pour ce nouveau niveau
    state = GAME;
}

// Fonction de transition pour revenir au menu correctement
function gameOver() {
    niveau = 1;  // Reset le niveau

    // Remise à 0 des Moving Lines
    resetMovingLines();

    state = MENU; // On retourne au Menu si Game Over
}

// Fonction permettant l'affichage d'une pop-up un peu transparente avec un message
function popUp(message) {
    push();
    fill(255, 255, 255, 200);
    stroke(0);
    strokeWeight(1);
    rect(width / 5, (height * 2 / 6), (width * 3) / 5, (height * 2) / 6);
    fill(0);
    textSize(width / 30);
    textAlign(CENTER, CENTER);
    text(message, width / 2, height / 2);
    pop();
}

// Fonction pour afficher le labyrinthe animé de l'écran de démarrage
function drawAnimatedMaze() {
    push();
    noFill();
    stroke(wallColor);
    strokeWeight(4);
    translate(220, 220);
    rect(0, 0, 180, 180);
    for (let i = 0; i < 4; i++) {
        lines[i].show();
    }
    pop();
}

// Empêche de scroller la page
window.addEventListener("keydown", function(e) {
    // space and arrow keys
    if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }
}, false);
