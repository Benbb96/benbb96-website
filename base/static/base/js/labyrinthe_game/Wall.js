// Classe pour construire les murs du labyrinthe

class Wall {

    constructor(ax, ay, bx, by) {
        this.a = createVector(ax, ay);  // Point A du mur (haut / gauche)
        this.b = createVector(bx, by);  // Point B du mur (bas / droite)
        this.alpha = 255;  // Transparence du mur
    }

    display() {
        // Calcul de la diminution de l'alpha (peut-être à adpater)
        if (disappear) this.alpha -= 1.2 / (nbCase / 2);
        if (this.alpha < niveau * -5) state = GAME_OVER;  // Si tous les murs ont disparu depuis un certain temps, le joueur a perdu
        push();
        stroke(color(4, this.alpha));
        strokeWeight((width + height) / (nbCase * 40));
        line(this.a.x * tailleX, this.a.y * tailleY, this.b.x * tailleX, this.b.y * tailleY);
        pop();
    }

}