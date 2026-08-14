// Classe pour construire les murs du labyrinthe

class Wall {
    constructor(ax, ay, bx, by) {
        this.a = createVector(ax, ay) // Point A du mur (haut / gauche)
        this.b = createVector(bx, by) // Point B du mur (bas / droite)
        this.alpha = 255 // Transparence du mur
    }

    display() {
        if (state === GAME) {
            // Calcul de la diminution de l'alpha (peut-être à adpater)
            if (labyrinthe.disappear) this.alpha -= 1.2 / (nbCase / 2)
            // Si tous les murs ont disparu depuis un certain temps, le joueur a perdu
            if (this.alpha < niveau * -5) state = GAME_OVER
        }
        push()
        // La couleur vient du thème (PALETTE.wall = --ds-text) : les murs
        // s'inversent donc avec le mode sombre. On repart des composantes plutôt
        // que d'un color(gris, alpha) : le mode Blind a besoin de faire varier
        // l'alpha d'une couleur qui n'est plus un simple niveau de gris.
        // this.alpha devient négatif (compte à rebours du game over) → withAlpha
        // le borne à 0.
        stroke(withAlpha(PALETTE.wall, this.alpha))
        strokeWeight((width + height) / (nbCase * 40))
        line(this.a.x * tailleX, this.a.y * tailleY, this.b.x * tailleX, this.b.y * tailleY)
        pop()
    }
}
