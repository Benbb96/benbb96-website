// La classe du Joueur

// Les touches maintenues appellent move() à CHAQUE frame (voir draw()) : sans
// garde-fou, rester collé contre un mur déclenchait un « aïe » par frame, soit
// une soixantaine de sons par seconde.
const WALL_SOUND_COOLDOWN = 350 // ms

class Player {
    constructor() {
        this.location // La position réel sur l'écran (en pixel)

        this.sizeX // La taille de la largeur du joueur
        this.sizeY // La taille de la hauteur du joueur

        this.overPlayer = false // Pour savoir si la souris est au-dessus du joueur
        this.isMoving = false // Lorsque le joueur est en déplacement
        this.point = false // Affichage des points de marquage du chemin du joueur
        this.chemin = true // Affichage des chemins empruntés par le joueur

        this.lastWallSound = 0 // Dernier « aïe » joué (cf. WALL_SOUND_COOLDOWN)

        // Le joueur commence sur la première case en général en haut à gauche (0,0)
        this.posOnGrid = createVector(labyrinthe.startCase.x, labyrinthe.startCase.y)
        this.sizeX = tailleX / 2
        this.sizeY = tailleY / 2
        this.updateLocation()
    }

    // Remet à jour la position réelle du joueur en pixel à partir de sa position dans la grille de jeu
    updateLocation() {
        if (this.isMoving) {
            this.tryMoving()
        }
        this.location = createVector(
            this.posOnGrid.x * tailleX + this.sizeX,
            this.posOnGrid.y * tailleY + this.sizeY
        )
    }

    // Fonction d'actualisation du joueur, sa taille, sa position et s'il a atteint son but
    update() {
        // Remise à jour de la taille du joueur
        this.sizeX = tailleX / 2
        this.sizeY = tailleY / 2

        // Test si le curseur de la souris est au-dessus du joueur
        if (
            mouseX > this.location.x - this.sizeX / 2 &&
            mouseX < this.location.x + this.sizeX / 2 &&
            mouseY > this.location.y - this.sizeY / 2 &&
            mouseY < this.location.y + this.sizeY / 2
        ) {
            if (!this.isMoving) cursor(HAND)
            this.overPlayer = true
        } else {
            cursor(ARROW)
            this.overPlayer = false
        }

        // Mise à jour de sa position à partir de la position sur la grille de jeu et affichage
        this.updateLocation()
        this.display()
        if (state === GAME) {
            // Vérification si le joueur est sur la dernière case
            labyrinthe.checkFinish()
        }
    }

    // Affiche le joueur
    display() {
        push()
        // Le joueur porte le jaune de marque (--ds-primary) en aplat, avec un
        // contour foncé (--ds-primary-ink) : c'est le seul usage du jaune autorisé
        // par la charte, et il tombe juste ici — le joueur est l'élément le plus
        // important du terrain. En déplacement souris, il passe à --ds-warning
        // (l'ambre de la charte, volontairement distinct du jaune de marque).
        fill(this.isMoving ? PALETTE.playerMoving : PALETTE.player)
        stroke(PALETTE.playerInk)
        if (this.overPlayer && !this.isMoving) strokeWeight((width + height) / (nbCase * 40))
        else strokeWeight((width + height) / (nbCase * 60))
        ellipse(this.location.x, this.location.y, this.sizeX, this.sizeY)
        pop()
    }

    // Fonction de déplacement qui vérifie si le déplacement peut se faire (limites du terrain et les murs)
    move(direction) {
        const oldPosOnGrid = createVector(this.posOnGrid.x, this.posOnGrid.y)

        if (this.canMove(direction)) {
            this.posOnGrid.x += labyrinthe.newX(direction)
            this.posOnGrid.y += labyrinthe.newY(direction)
            if (grille[int(this.posOnGrid.y)][int(this.posOnGrid.x)] === 0) {
                grille[int(this.posOnGrid.y)][int(this.posOnGrid.x)] = 1 // Indique que le joueur est passé par cette case
                // Ajoute le nouveau segment de chemin parcouru par le joueur
                labyrinthe.chemins.push(
                    new Chemin(oldPosOnGrid, createVector(this.posOnGrid.x, this.posOnGrid.y))
                )
            }
        } else if (DIR_BIT[direction] && millis() - this.lastWallSound > WALL_SOUND_COOLDOWN) {
            // On ne « râle » que sur une vraie tentative bloquée : getDirection()
            // renvoie 0 quand la souris ne désigne pas une case adjacente.
            this.lastWallSound = millis()
            playSound(wallSounds[int(random(0, wallSounds.length))])
        }
    }

    // Le joueur peut-il se déplacer dans cette direction ? (limites du terrain
    // puis murs). Remplace les quatre branches quasi identiques d'origine, qui
    // recalculaient chacune à la main un index dans la matrice d'adjacence.
    canMove(direction) {
        if (!DIR_BIT[direction]) return false // direction inconnue : on ne bouge pas
        const nx = int(this.posOnGrid.x) + labyrinthe.newX(direction)
        const ny = int(this.posOnGrid.y) + labyrinthe.newY(direction)
        if (nx < 0 || nx >= nbCase || ny < 0 || ny >= nbCase) return false
        return labyrinthe.hasPassage(this.posOnGrid.x, this.posOnGrid.y, direction)
    }

    // Repositionne le joueur à l'endroit souhaité
    repositionne(x, y) {
        this.posOnGrid.x = x
        this.posOnGrid.y = y
    }

    // Index de la case sur laquelle se trouve le joueur (touche W, débogage).
    // Exemple : il y a 3 cases de largeur, le joueur est sur la 2ème case de la
    // 3ème ligne (1,2), il est donc sur la 7ème case de la grille (2*3 + 1 = 7)
    cellIndex() {
        return int(this.posOnGrid.x) * nbCase + int(this.posOnGrid.y)
    }

    // Essaye de faire bouger le joueur à l'aide de la souris
    tryMoving() {
        // Récupère les coordonnées de la position de la souris
        let x = floor(mouseX / tailleX)
        let y = floor(mouseY / tailleY)

        // Appelle la fonction de déplacement dans la direction où se trouve la souris par rapport au joueur
        this.move(this.getDirection(x, y))
    }

    // Retourne la direction à une case d'écart par rapport à la position donné en paramètre et la position du joueur
    getDirection(x, y) {
        // Calcul d'où souhaite-t-on se rendre
        let targetX = int(x - this.posOnGrid.x)
        let targetY = int(y - this.posOnGrid.y)

        // Retourne la direction en fonction. La tolérance sur l'autre axe est
        // volontaire : c'est elle qui rend le suivi de souris jouable, sinon il
        // faudrait garder le curseur pile sur la case voisine.
        if (targetX === 1) return RIGHT_ARROW
        else if (targetX === -1) return LEFT_ARROW
        else if (targetY === 1) return DOWN_ARROW
        else if (targetY === -1) return UP_ARROW
        return 0 // Le joueur ne bougera pas
    }
}
