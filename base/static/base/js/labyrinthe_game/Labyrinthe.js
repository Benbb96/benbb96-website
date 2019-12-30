// La classe du Labyrinthe

const zeros = (m, n) => [...Array(m)].map(e => Array(n).fill(0));

class Labyrinthe {

    constructor() {
        this.walls = [];  // Liste des murs du labyrinthe
        this.chemins = [];  // Liste des chemins

        this.disappear = false;  // Permet de choisir si les murs du labyrinthe disparaissent ou non


        // Réinitialise les tableaux à 2 dimensions
        matrice = zeros(nbCase*nbCase, nbCase*nbCase);
        grille = zeros(nbCase, nbCase);
        // Génère la matrice d'adjacence et construit les murs du labyrinthe
        this.creuse_passage(0, 0);
        grille = zeros(nbCase, nbCase);  // On remet à 0 la grille pour renseigner ensuite par où est passer le joueur

        // En mode facile, la case de départ est en haut à gauche et celle d'arrivée est en bas à droite
        if (mode === EASY) {
            this.startCase = createVector(0, 0);
            this.endCase = createVector(nbCase - 1, nbCase - 1);
        } else {  // Dans les autres modes, ce sera random
            this.startCase = createVector(int(random(nbCase)), int(random(nbCase)));
            this.endCase = createVector(int(random(nbCase)), int(random(nbCase)));
        }
        while (this.endCase.x === this.startCase.x && this.endCase.y === this.startCase.y) {
            this.endCase = createVector(int(random(nbCase)), int(random(nbCase)));
        }
        this.buildMaze();
    }

    // Affichage du labyrinthe en général
    display() {
        fill(color(0, 0, 255));
        noStroke();
        // Affichage des points/carrés de déplacements
        if (player.point) {
            for (let i = 0; i < nbCase; i++) {
                for (let j = 0; j < nbCase; j++) {
                    if (grille[j][i] !== 0) {
                        //ellipse(i * tailleX + tailleX/2, j * tailleY + tailleY/2, tailleX/10, tailleY/10);
                        rect(i * tailleX, j * tailleY, tailleX, tailleY);
                    }
                }
            }
        }

        // Cases Départ Vert et Arrivée Rouge
        fill(color(0, 255, 0));
        rect(tailleX * this.startCase.x + tailleX / 7, tailleY * this.startCase.y + tailleY / 7, tailleX * 5 / 7, tailleY * 5 / 7);
        fill(color(255, 0, 0));
        rect(tailleX * this.endCase.x + tailleX / 7, tailleY * this.endCase.y + tailleY / 7, tailleX * 5 / 7, tailleY * 5 / 7);

        // Affichage des chemins empruntés par le joueur
        if (player.chemin) {
            for (let i = 0; i < this.chemins.length; i++) {
                this.chemins[i].display();
            }
        }

        // Information sur la case départ du niveau du labyrinthe
        fill(wallColor);
        textSize(tailleY / 2);
        textAlign(LEFT_ARROW);
        text(niveau, tailleX / 3, tailleY - tailleY / 3);

        // Affichage des murs
        for (let i = 0; i < this.walls.length; i++) {
            this.walls[i].display();
        }

        // Contour du terrain de jeu
        strokeWeight((width + height) / (nbCase * 40));
        stroke(wallColor);
        line(0, 0, tailleX * nbCase, 0);
        line(0, 0, 0, tailleY * nbCase);
        line(tailleX * nbCase, 0, tailleX * nbCase, tailleY * nbCase - 1);
        line(0, tailleY * nbCase, tailleX * nbCase, tailleY * nbCase);
    }

    resetAlpha() {
        for (let i = 0; i < walls.length; i++) {
            walls[i].alpha = 255;
        }
    }

    // Fonction récursive qui permet de creuser le labyrinthe
    creuse_passage(cx, cy) {
        //println("Creuse Passage depuis " + cx + "," + cy);
        let directions = this.newDirectionList();
        let direction;
        // On va tester chaque direction une à une
        for (let i = 0; i < 4; i++) {
            direction = directions[i];
            // Quelle est la case qu'on souhaite atteindre
            let nx = cx + this.newX(direction);
            let ny = cy + this.newY(direction);

            // Est-elle sur la grille (entre 0 et le nombre de case)
            if ((ny >= 0 && ny < nbCase) && (nx >= 0 && nx < nbCase)) {
                // A-t-elle déjà été visité ?
                if (grille[nx][ny] === 0) {
                    // Elle est accessible donc on mets à jour nos différentes matrices
                    grille[cx][cy] = direction;  // Sur la cellule sur laquelle on se trouve, on met la direction où l'on va
                    grille[nx][ny] = this.opposite(direction);  // Sur la cellule sur laquelle on va arriver, on met la direction opposé vers où l'on va

                    // Et on ajoute des 1 dans la matrice d'adjacence pour que le joueur sache qu'il peut atteindre cette cellule à partir de celle-ci
                    matrice[this.two2one(cx, cy)][this.two2one(nx, ny)] = 1;
                    matrice[this.two2one(nx, ny)][this.two2one(cx, cy)] = 1;

                    // Enfin on appelle donc à nouveau cette même fonction qui va continuer de creuser à partir de cette nouvelle case atteinte
                    this.creuse_passage(nx, ny);
                }
            }
        } // Et cela donc pour chaque direction
    }

    // Crée une liste d'entier représentant les 4 directions et rangés dans le désordre
    newDirectionList() {
        let list = [];
        for (let i = LEFT_ARROW; i <= DOWN_ARROW; i++) list.push(i);
        list.sort(() => Math.random() - 0.5);  // Mélange les nombres/directions
        return list;
    }

    // Fonction qui calcul quelle sera le nouveau x en fonction de la direction
    newX(direction) {
        let n = 0;
        if (direction === LEFT_ARROW) n = -1;
        else if (direction === RIGHT_ARROW) n = 1;
        return n;
    }

    // Fonction qui calcul quelle sera le nouveau y en fonction de la direction
    newY(direction) {
        let n = 0;
        if (direction === UP_ARROW) n = -1;
        else if (direction === DOWN_ARROW) n = 1;
        return n;
    }

    // Fonctions de correspondances entre le tableau 2 dimension et une dimension
    two2one(x, y) {
        return x * nbCase + y;
    }

    one2two(n) {
        let coordonnee = createVector();
        coordonnee.x = n / nbCase;
        coordonnee.y = n % nbCase;
        return coordonnee;
    }

    // Retourne la direction opposé
    opposite(direction) {
        switch (direction) {
            case UP_ARROW :
                return DOWN_ARROW;
            case DOWN_ARROW :
                return UP_ARROW;
            case LEFT_ARROW :
                return RIGHT_ARROW;
            case RIGHT_ARROW :
                return LEFT_ARROW;
            default:
                return 0;
        }
    }

    // Fonction qui construit le labyrinthe en créant des murs en bas et à droite de chaque case s'il y en besoin
    buildMaze() {
        let ax, ay, bx, by;  // Case A et B adjacente
        // Parcours de toutes les cases du labyrinthe
        for (let i = 0; i < nbCase; i++) {
            for (let j = 0; j < nbCase; j++) {
                // Ya-t-il un passage à droite de cette case ?
                if (j + 1 < nbCase && matrice[this.two2one(i, j)][this.two2one(i, j + 1)] === 0) {
                    ax = i;
                    ay = j + 1;
                    bx = i + 1;
                    by = j + 1;
                    this.walls.push(new Wall(bx, by, ax, ay));
                }
                // Ya-t-il un passage en bas de cette case ?
                if (i + 1 < nbCase && matrice[this.two2one(i, j)][this.two2one(i + 1, j)] === 0) {
                    ax = i + 1;
                    ay = j;
                    bx = i + 1;
                    by = j + 1;
                    this.walls.push(new Wall(bx, by, ax, ay));
                }
            }
        }
    }

    // Vérifie si le joueur a atteint le point d'arrivée
    checkFinish() {
        if (player.posOnGrid.x === this.endCase.x && player.posOnGrid.y === this.endCase.y) {
            player.isMoving = false;  // On stoppe le joueur pour ne plus qu'il puisse bouger à l'aide de la souris
            timer.end();
            if (mode === BLIND) {  // Dans ce mode on stoppe la disparition des murs
                this.disappear = false;
            }
            state = LEVEL_UP;
        }
    }

}