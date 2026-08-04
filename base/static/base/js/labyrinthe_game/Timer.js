// Classe pour gérer le chronomètre du jeu

// Formate une durée en millisecondes.
// Attention : l'implémentation précédente utilisait round() sur chaque unité
// (round(ms / 60000) pour les minutes, etc.), ce qui affichait un temps FAUX dès
// qu'on dépassait la moitié de l'unité — 1 min 50 s devenait « 2m 50s », et
// 1,6 s « 2s 600ms ». Il faut une troncature (floor) et non un arrondi.
function formatDuration(ms) {
    const total = max(0, floor(ms))
    const parts = {
        j: floor(total / 86400000),
        h: floor(total / 3600000) % 24,
        m: floor(total / 60000) % 60,
        s: floor(total / 1000) % 60,
    }
    let text = ''
    // Une unité n'est affichée que si elle est non nulle, ou qu'une unité plus
    // grande l'a déjà été (sinon « 1h 0m 4s » s'afficherait « 1h 4s »).
    for (const unit in parts) {
        if (parts[unit] > 0 || text !== '') text += parts[unit] + unit + ' '
    }
    return text + (total % 1000) + 'ms'
}

class Timer {
    constructor() {
        this.time = 0 // On réinitialise le temps enregistré à 0
        this.restart() // On démarre le timer
    }

    // Fonction pour démarrer ou redémarrer le chrono
    restart() {
        // On enregistre le temps depuis que le jeu a été lancé, pour ensuite le
        // comparer à un autre temps et ainsi avoir la différence
        this.start = millis()
        this.isRunning = true // Permet de s'assurer que le timer est en route ou non
    }

    // Mettre en pause le timer
    pause() {
        this.time += millis() - this.start // Calcul de la durée, ajoutée au temps déjà enregistré
        this.isRunning = false
    }

    // Quand c'est la fin du labyrinthe
    end() {
        if (this.isRunning) this.pause()
    }

    // Temps écoulé, fraction en cours incluse quand le chrono tourne : sans ça
    // le HUD resterait figé jusqu'à la première pause (this.time n'est mis à
    // jour que par pause()).
    elapsed() {
        return this.isRunning ? this.time + (millis() - this.start) : this.time
    }

    getDisplay() {
        return formatDuration(this.elapsed())
    }
}
