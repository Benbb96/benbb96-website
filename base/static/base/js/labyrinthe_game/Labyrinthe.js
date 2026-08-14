// La classe du Labyrinthe

const zeros = (m, n) => [...Array(m)].map(e => Array(n).fill(0))

// Masque de bits par direction (les constantes p5 valent 37..40).
// Sert à stocker les passages ouverts d'une case dans un seul octet.
const DIR_BIT = { 37: 1, 38: 2, 39: 4, 40: 8 } // LEFT, UP, RIGHT, DOWN

class Labyrinthe {
    constructor() {
        this.walls = [] // Liste des murs du labyrinthe
        this.chemins = [] // Liste des chemins

        this.disappear = mode === BLIND // Permet de choisir si les murs du labyrinthe disparaissent ou non

        // Passages ouverts entre cases : un octet par case, un bit par direction.
        // C'était auparavant une matrice d'adjacence de nbCase² × nbCase², soit
        // O(n⁴) — au niveau 20 en mode Hard (nbCase = 61) elle réservait ~14
        // millions de cellules (plus de 100 Mo) à chaque régénération, alors que
        // le jeu est conçu pour monter en niveaux indéfiniment. Seules les 4
        // cases voisines peuvent être reliées : un masque de bits suffit.
        passages = new Uint8Array(nbCase * nbCase)
        grille = zeros(nbCase, nbCase)
        // Génère les passages et construit les murs du labyrinthe
        this.creuse_passage(0, 0)
        grille = zeros(nbCase, nbCase) // On remet à 0 la grille pour renseigner ensuite par où est passé le joueur

        // En mode facile, la case de départ est en haut à gauche et celle d'arrivée est en bas à droite
        if (mode === EASY) {
            this.startCase = createVector(0, 0)
            this.endCase = createVector(nbCase - 1, nbCase - 1)
        } else {
            // Dans les autres modes, ce sera random
            this.startCase = createVector(int(random(nbCase)), int(random(nbCase)))
            this.endCase = createVector(int(random(nbCase)), int(random(nbCase)))
        }
        while (this.endCase.x === this.startCase.x && this.endCase.y === this.startCase.y) {
            this.endCase = createVector(int(random(nbCase)), int(random(nbCase)))
        }
        this.buildMaze()
    }

    // Affichage du labyrinthe en général
    display() {
        push()

        // Affichage des cases par lesquelles le joueur est passé (touche P).
        // En aplat semi-transparent : opaque, il masquait murs et tracé.
        if (player.point) {
            noStroke()
            fill(PALETTE.visited)
            for (let i = 0; i < nbCase; i++) {
                for (let j = 0; j < nbCase; j++) {
                    if (grille[j][i] !== 0) {
                        rect(i * tailleX, j * tailleY, tailleX, tailleY)
                    }
                }
            }
        }

        this.displayStartCase()
        this.displayEndCase()

        // Affichage des chemins empruntés par le joueur
        if (player.chemin) {
            for (let i = 0; i < this.chemins.length; i++) {
                this.chemins[i].display()
            }
        }

        // Le numéro de niveau était dessiné ici, dans la case (0, 0) — c'est-à-dire
        // pile sur le marqueur de départ en mode Easy, où celui-ci est toujours en
        // haut à gauche. Il est désormais affiché dans le HUD HTML (data-laby-level),
        // en permanence et sans rien recouvrir.

        // Affichage des murs
        for (let i = 0; i < this.walls.length; i++) {
            this.walls[i].display()
        }

        // Contour du terrain de jeu
        strokeWeight((width + height) / (nbCase * 40))
        stroke(PALETTE.wall)
        noFill()
        line(0, 0, tailleX * nbCase, 0)
        line(0, 0, 0, tailleY * nbCase)
        line(tailleX * nbCase, 0, tailleX * nbCase, tailleY * nbCase - 1)
        line(0, tailleY * nbCase, tailleX * nbCase, tailleY * nbCase)
        pop()
    }

    // Case de départ : un carré évidé — repère discret, puisqu'on l'a quittée.
    // La FORME distingue départ et arrivée, pas seulement la teinte : vert et
    // rouge sont indistinguables en daltonisme rouge-vert (~8 % des hommes), et
    // ces deux repères sont l'information la plus utile du terrain.
    displayStartCase() {
        push()
        noFill()
        stroke(PALETTE.start)
        strokeWeight(max(1, tailleX / 10))
        rect(
            tailleX * this.startCase.x + tailleX / 4,
            tailleY * this.startCase.y + tailleY / 4,
            tailleX / 2,
            tailleY / 2
        )
        pop()
    }

    // Case d'arrivée : une cible (anneau + disque plein au centre).
    displayEndCase() {
        const cx = tailleX * this.endCase.x + tailleX / 2
        const cy = tailleY * this.endCase.y + tailleY / 2
        push()
        noFill()
        stroke(PALETTE.end)
        strokeWeight(max(1, tailleX / 10))
        ellipse(cx, cy, tailleX * 0.62, tailleY * 0.62)
        noStroke()
        fill(PALETTE.end)
        ellipse(cx, cy, tailleX * 0.26, tailleY * 0.26)
        pop()
    }

    // Remet les murs pleinement opaques (touche A, mode Blind).
    // Corrige un ReferenceError : la boucle itérait sur `walls`, qui n'existe pas
    // — il n'y a pas de globale de ce nom, seulement this.walls. La touche
    // documentée dans le template ne fonctionnait donc pas du tout.
    resetAlpha() {
        for (let i = 0; i < this.walls.length; i++) {
            this.walls[i].alpha = 255
        }
    }

    // ── Passages entre cases ────────────────────────────────────────────────

    // Ouvre le passage entre la case (cx, cy) et sa voisine dans `direction`
    openPassage(cx, cy, nx, ny, direction) {
        passages[this.two2one(cx, cy)] |= DIR_BIT[direction]
        passages[this.two2one(nx, ny)] |= DIR_BIT[this.opposite(direction)]
    }

    // Peut-on aller de la case (x, y) vers sa voisine dans `direction` ?
    hasPassage(x, y, direction) {
        const bit = DIR_BIT[direction]
        if (!bit) return false
        return (passages[this.two2one(int(x), int(y))] & bit) !== 0
    }

    // Fonction récursive qui permet de creuser le labyrinthe
    creuse_passage(cx, cy) {
        let directions = this.newDirectionList()
        let direction
        // On va tester chaque direction une à une
        for (let i = 0; i < 4; i++) {
            direction = directions[i]
            // Quelle est la case qu'on souhaite atteindre
            let nx = cx + this.newX(direction)
            let ny = cy + this.newY(direction)

            // Est-elle sur la grille (entre 0 et le nombre de case)
            if (ny >= 0 && ny < nbCase && nx >= 0 && nx < nbCase) {
                // A-t-elle déjà été visitée ?
                if (grille[nx][ny] === 0) {
                    // Elle est accessible donc on met à jour la grille…
                    grille[cx][cy] = direction // Sur la cellule sur laquelle on se trouve, on met la direction où l'on va
                    grille[nx][ny] = this.opposite(direction) // Sur la cellule où l'on va arriver, la direction opposée

                    // …et on ouvre le passage dans les deux sens pour que le
                    // joueur sache qu'il peut atteindre cette cellule
                    this.openPassage(cx, cy, nx, ny, direction)

                    // Enfin on rappelle cette même fonction qui va continuer de creuser à partir de cette nouvelle case
                    this.creuse_passage(nx, ny)
                }
            }
        } // Et cela donc pour chaque direction
    }

    // Crée une liste d'entier représentant les 4 directions et rangés dans le désordre
    newDirectionList() {
        let list = []
        for (let i = LEFT_ARROW; i <= DOWN_ARROW; i++) list.push(i)
        list.sort(() => Math.random() - 0.5) // Mélange les nombres/directions
        return list
    }

    // Fonction qui calcul quelle sera le nouveau x en fonction de la direction
    newX(direction) {
        let n = 0
        if (direction === LEFT_ARROW) n = -1
        else if (direction === RIGHT_ARROW) n = 1
        return n
    }

    // Fonction qui calcul quelle sera le nouveau y en fonction de la direction
    newY(direction) {
        let n = 0
        if (direction === UP_ARROW) n = -1
        else if (direction === DOWN_ARROW) n = 1
        return n
    }

    // Correspondance entre les coordonnées 2D et l'index à une dimension
    two2one(x, y) {
        return x * nbCase + y
    }

    // Retourne la direction opposé
    opposite(direction) {
        switch (direction) {
            case UP_ARROW:
                return DOWN_ARROW
            case DOWN_ARROW:
                return UP_ARROW
            case LEFT_ARROW:
                return RIGHT_ARROW
            case RIGHT_ARROW:
                return LEFT_ARROW
            default:
                return 0
        }
    }

    // Fonction qui construit le labyrinthe en créant des murs en bas et à droite de chaque case s'il y en besoin
    buildMaze() {
        let ax, ay, bx, by // Case A et B adjacente
        // Parcours de toutes les cases du labyrinthe
        for (let i = 0; i < nbCase; i++) {
            for (let j = 0; j < nbCase; j++) {
                // Ya-t-il un passage en bas de cette case ?
                if (j + 1 < nbCase && !this.hasPassage(i, j, DOWN_ARROW)) {
                    ax = i
                    ay = j + 1
                    bx = i + 1
                    by = j + 1
                    this.walls.push(new Wall(bx, by, ax, ay))
                }
                // Ya-t-il un passage à droite de cette case ?
                if (i + 1 < nbCase && !this.hasPassage(i, j, RIGHT_ARROW)) {
                    ax = i + 1
                    ay = j
                    bx = i + 1
                    by = j + 1
                    this.walls.push(new Wall(bx, by, ax, ay))
                }
            }
        }
    }

    // Vérifie si le joueur a atteint le point d'arrivée
    checkFinish() {
        if (player.posOnGrid.x === this.endCase.x && player.posOnGrid.y === this.endCase.y) {
            player.isMoving = false // On stoppe le joueur pour ne plus qu'il puisse bouger à l'aide de la souris
            timer.end()
            recordMazeTime(timer.elapsed()) // Meilleur temps sur un labyrinthe
            state = LEVEL_UP
            playSound(successSound)
        }
    }
}
