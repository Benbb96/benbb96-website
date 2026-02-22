// Classe pour construire les chemins empruntés par le joueur

class Chemin {

    constructor(a, b) {
        this.a = a;
        this.b = b;
        this.alpha = 255.0;
    }

    display() {
        push();
        stroke(color(0, 255, 255), this.alpha);
        strokeWeight((width + height) / (nbCase * 50));
        line(this.a.x * tailleX + tailleX / 2, this.a.y * tailleY + tailleY / 2, this.b.x * tailleX + tailleX / 2, this.b.y * tailleY + tailleY / 2);
        pop();
    }
}