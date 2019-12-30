// La classe du Joueur

class Player {

    constructor() {
        this.location;  // La position réel sur l'écran (en pixel)

        this.sizeX;  // La taille de la largeur du joueur
        this.sizeY;  // La taille de la hauteur du joueur

        this.overPlayer = false;  // Pour savoir si la souris est au-dessus du joueur
        this.isMoving = false;  // Lorsque le joueur est est en déplacement
        this.point = false;  // Affichage des points de marquage du chemin du joueur
        this.chemin = true;  // Affichage des chemins empruntés par le joueur

        this.couleur = color(255, 255, 0);  // La couleur du joueur, par défaut jaune

        // Le joueur commence sur la première case en général en haut à gauche (0,0)
        this.posOnGrid = createVector(labyrinthe.startCase.x, labyrinthe.startCase.y);
        this.updateLocation();
    }

    // Remet à jour la position réelle du joueur en pixel à partir de sa position dans la grille de jeu
    updateLocation() {
        if (this.isMoving) {
            this.tryMoving();
        }
        this.location = createVector(this.posOnGrid.x * tailleX + this.sizeX, this.posOnGrid.y * tailleY + this.sizeY);
    }

    // Fonction d'actualisation du joueur, sa taille, sa position et s'il a atteint son but
    update() {
        // Remise à jour de la taille du joueur
        this.sizeX = tailleX / 2;
        this.sizeY = tailleY / 2;

        // Test si le curseur de la souris est au-dessus du joueur
        if (mouseX > this.location.x - this.sizeX / 2 && mouseX < this.location.x + this.sizeX / 2 &&
            mouseY > this.location.y - this.sizeY / 2 && mouseY < this.location.y + this.sizeY / 2) {
            if (!this.isMoving) cursor(HAND);
            this.overPlayer = true;
        } else {
            cursor(ARROW);
            this.overPlayer = false;
        }

        // Mise à jour de sa position à partir de la position sur la grille de jeu et affichage
        this.updateLocation();
        this.display();
        // Vérification si le joueur est sur la dernière case
        labyrinthe.checkFinish();
    }

    // Affiche le joueur
    display() {
        push();
        if (this.isMoving) fill(230, 150, 70);
        else fill(this.couleur);
        if (this.overPlayer && !this.isMoving) strokeWeight((width + height) / (nbCase * 40));
        else strokeWeight((width + height) / (nbCase * 60));
        stroke(0);
        ellipse(this.location.x, this.location.y, this.sizeX, this.sizeY);
        pop();
    }

    // Fonction de déplacement qui vérifie si le déplacement peut se faire (limites du terrain et les murs)
    move(direction) {
        let canGoThere = true;
        let oldPosOnGrid = createVector(this.posOnGrid.x, this.posOnGrid.y);
        switch (direction) {
            case UP_ARROW :
                if (this.posOnGrid.y > 0 && matrice[this.posOnMatrice()][int(this.posOnGrid.x) * nbCase + int(this.posOnGrid.y) - 1] === 1) this.posOnGrid.y--;
                else canGoThere = false;
                break;
            case DOWN_ARROW :
                if (this.posOnGrid.y < nbCase - 1 && matrice[this.posOnMatrice()][int(this.posOnGrid.x) * nbCase + int(this.posOnGrid.y) + 1] === 1) this.posOnGrid.y++;
                else canGoThere = false;
                break;
            case LEFT_ARROW :
                if (this.posOnGrid.x > 0 && matrice[this.posOnMatrice()][(int(this.posOnGrid.x) - 1) * nbCase + int(this.posOnGrid.y)] === 1) this.posOnGrid.x--;
                else canGoThere = false;
                break;
            case RIGHT_ARROW :
                if (this.posOnGrid.x < nbCase - 1 && matrice[this.posOnMatrice()][(int(this.posOnGrid.x) + 1) * nbCase + int(this.posOnGrid.y)] === 1) this.posOnGrid.x++;
                else canGoThere = false;
                break;
        }

        if (canGoThere) {
            if (grille[int(this.posOnGrid.y)][int(this.posOnGrid.x)] === 0) {
                grille[int(this.posOnGrid.y)][int(this.posOnGrid.x)] = 1;  // Indique que le joueur est passé par cette case
                labyrinthe.chemins.push(new Chemin(oldPosOnGrid, createVector(this.posOnGrid.x, this.posOnGrid.y)));  // Ajoute le nouveau segment de chemin parcouru par le joueur
            }
        }

    }

    // Repositionne le joueur à l'endroit souhaité
    repositionne(x, y) {
        this.posOnGrid.x = x;
        this.posOnGrid.y = y;
    }

    // Retourne le numéro de la case sur laquelle se positionne le joueur
    // Exemple : il y a 3 cases de largeur, le joueur est sur la 2ème case de la 3ème ligne (1,2), il est donc sur la 7ème case de la grille (2*3 + 1 = 7)
    posOnMatrice() {
        return int(this.posOnGrid.x) * nbCase + int(this.posOnGrid.y);
    }

    // Essaye de faire bouger le joueur à l'aide de la souris
    tryMoving() {
        // Récupère les coordonnées de la position de la souris
        let x = floor(mouseX / tailleX);
        let y = floor(mouseY / tailleY);

        // Appelle la fonction de déplacement dans la direction où se trouve la souris par rapport au joueur
        this.move(this.getDirection(x, y));
    }

    // Retourne la direction à une case d'écart par rapport à la position donné en paramètre et la position du joueur
    getDirection(x, y) {
        // Calcul d'où souhaite-t-on se rendre
        let targetX = int(x - this.posOnGrid.x);
        let targetY = int(y - this.posOnGrid.y);

        // Retourne la direction en fonction
        if (targetX === 1) return RIGHT_ARROW;
        else if (targetX === -1) return LEFT_ARROW;
        else if (targetY === 1) return DOWN_ARROW;
        else if (targetY === -1) return UP_ARROW;
        return 0;  // Le joueur ne bougera pas
    }

}