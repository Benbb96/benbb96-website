// Classe pour construire les boutons du menu de démarrage

class Button {

    constructor(id, text, x, y, mode, overColor) {
        this.id = id;  // Numéro du bouton servant de passer d'un bouton à l'autre avec le clavier
        this.text = text;  // Le texte du bouton
        this.x = x;
        this.y = y;
        this.buttonMode = mode;  // Le mode auquel donne accès le bouton
        this.overColor = overColor;  // Les couleurs du bouton
        this.selected = false;  // Indique si le bouton est actuellement sélectionné
    }

    // Fonction permettant l'affichage du bouton
    display() {
        // Si la souris est au-dessus du bouton, il est sélectionné
        if (this.mouseOver() && !this.selected) {
            this.resetSelectedButtons();
            this.selected = true;
            selectedButton = this.id;
        }

        if (this.selected) {  // Si le bouton est sélectionné, on utilise sa couleur de survol et on grossit un peu la taille du texte
            fill(this.overColor);
            stroke(this.overColor);
            strokeWeight(2);
            textSize(width / 19);
            line(this.x - textWidth(this.text) / 2 - 27, this.y + 3, this.x - textWidth(this.text) / 2 - 8, this.y + 3);
            line(this.x + textWidth(this.text) / 2 + 27, this.y + 3, this.x + textWidth(this.text) / 2 + 8, this.y + 3);
        } else {
            fill(wallColor);
            textSize(width / 21);
        }
        textAlign(CENTER, CENTER);
        text(this.text, this.x, this.y);
    }

    // Fonction qui initialise tous les paramètres propres à un mode de jeu
    chargeMode() {
        switch (this.buttonMode) {
            case EASY :
                nbCaseDefaut = 2;
                incrementationDefaut = 1;
                disappear = false;
                mode = EASY;
                break;
            case MEDIUM :
                nbCaseDefaut = 3;
                incrementationDefaut = 2;
                disappear = false;
                mode = MEDIUM;
                break;
            case HARD :
                nbCaseDefaut = 4;
                incrementationDefaut = 3;
                disappear = false;
                mode = HARD;
                break;
            case BLIND :
                nbCaseDefaut = 3;
                incrementationDefaut = 3;
                disappear = true;  // On active le booléen de disparition
                mode = BLIND;
                break;
        }
        nbCase = nbCaseDefaut;
    }

    // Permet de déterminer si la souris estau-dessus du bouton ou non
    mouseOver() {
        return mouseY > this.y - 25 && mouseY < this.y + 10 && mouseX < width / 2;
    }

    // Fonction pour désélectionner tous les boutons
    resetSelectedButtons() {
        for (let i = 0; i < 4; i++) {
            buttons[i].selected = false;
        }
    }

}