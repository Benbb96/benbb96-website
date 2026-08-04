// Classe pour construire les boutons du menu de démarrage

// Paramètres de chaque mode, y compris sa clé de couleur dans PALETTE. La
// couleur est stockée par CLÉ et non par valeur : elle est résolue à
// l'affichage, donc elle suit les bascules clair/sombre en cours de partie.
const MODE_SETTINGS = {
    1: { nbCase: 2, incrementation: 1, paletteKey: 'easy' }, // EASY
    2: { nbCase: 3, incrementation: 2, paletteKey: 'medium' }, // MEDIUM
    3: { nbCase: 4, incrementation: 3, paletteKey: 'hard' }, // HARD
    4: { nbCase: 3, incrementation: 3, paletteKey: 'blind' }, // BLIND
}

class Button {
    constructor(id, text, x, y, mode) {
        this.id = id // Numéro du bouton servant de passer d'un bouton à l'autre avec le clavier
        this.text = text // Le texte du bouton
        this.x = x
        this.y = y
        this.buttonMode = mode // Le mode auquel donne accès le bouton
        this.selected = false // Indique si le bouton est actuellement sélectionné
    }

    // Taille de texte de référence, celle du bouton NON sélectionné
    baseTextSize() {
        return width / 21
    }

    // Fonction permettant l'affichage du bouton
    display() {
        // Si la souris est au-dessus du bouton, il est sélectionné
        if (this.mouseOver() && !this.selected) {
            this.resetSelectedButtons()
            this.selected = true
            selectedButton = this.id
        }
        push()
        if (this.selected) {
            // Si le bouton est sélectionné, on utilise sa couleur de survol et on grossit un peu la taille du texte
            const overColor = PALETTE[MODE_SETTINGS[this.buttonMode].paletteKey]
            fill(overColor)
            stroke(overColor)
            strokeWeight(2)
            textSize(width / 19)
            const half = textWidth(this.text) / 2
            line(this.x - half - 27, this.y + 3, this.x - half - 8, this.y + 3)
            line(this.x + half + 27, this.y + 3, this.x + half + 8, this.y + 3)
        } else {
            fill(PALETTE.wall)
            noStroke()
            textSize(this.baseTextSize())
        }
        textAlign(CENTER, CENTER)
        text(this.text, this.x, this.y)
        pop()
    }

    // Fonction qui initialise tous les paramètres propres à un mode de jeu
    chargeMode() {
        const settings = MODE_SETTINGS[this.buttonMode]
        nbCaseDefaut = settings.nbCase
        incrementationDefaut = settings.incrementation
        mode = this.buttonMode
        nbCase = nbCaseDefaut
    }

    // Zone de clic réelle du bouton.
    // Elle est calculée à la taille de texte de RÉFÉRENCE (bouton non
    // sélectionné) et non à la taille courante : sinon la zone grandirait au
    // survol, c'est-à-dire pendant qu'on la teste. L'ancienne version ne testait
    // qu'une bande horizontale et `mouseX < width / 2` : on lançait une partie en
    // cliquant à côté du texte, n'importe où dans la moitié gauche du canvas.
    hitBox() {
        push()
        textSize(this.baseTextSize())
        const w = textWidth(this.text) + 54 // + la place des deux traits latéraux
        pop()
        const h = this.baseTextSize() * 1.7
        return { x: this.x - w / 2, y: this.y - h / 2, w: w, h: h }
    }

    // Permet de déterminer si la souris est au-dessus du bouton ou non
    mouseOver() {
        const box = this.hitBox()
        return (
            mouseX > box.x && mouseX < box.x + box.w && mouseY > box.y && mouseY < box.y + box.h
        )
    }

    // Fonction pour désélectionner tous les boutons
    resetSelectedButtons() {
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].selected = false
        }
    }
}
