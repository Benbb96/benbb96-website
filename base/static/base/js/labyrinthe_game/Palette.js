// Palette du jeu — passerelle entre le design system CSS et p5.js
//
// p5 dessine dans un <canvas> : ses couleurs ne suivent pas le CSS. On lit donc
// les tokens --ds-* de assets/css/main.css une fois à l'init, puis à chaque
// bascule du toggle clair/sombre/auto de la navbar (événement
// « benbb96:themechange » émis par assets/js/theme.js). Même patron que
// tracker/static/tracker/js/common.js pour Chart.js.
//
// Ce que la charte impose et qui est respecté ici :
//  - le jaune de marque (--ds-primary) ne sert QU'EN APLAT — c'est le joueur —
//    avec un contour foncé dessus (--ds-primary-ink) ; jamais en trait fin ;
//  - murs et fond sont pris sur --ds-text / --ds-surface : ils s'inversent donc
//    d'eux-mêmes en thème sombre (labyrinthe clair sur fond sombre) ;
//  - départ et arrivée ne se distinguent pas QUE par la teinte — vert et rouge
//    sont confondus en daltonisme rouge-vert : Labyrinthe.js leur donne aussi
//    des formes différentes (carré évidé vs cible).

const PALETTE_TOKENS = {
    bg: '--ds-surface',            // fond du terrain de jeu
    wall: '--ds-text',             // murs + contour du terrain
    player: '--ds-primary',        // le joueur = le jaune de marque, en aplat
    playerInk: '--ds-primary-ink', // contour du joueur (foncé, posé sur le jaune)
    playerMoving: '--ds-warning',  // joueur en déplacement à la souris
    start: '--ds-success',
    end: '--ds-danger',
    path: '--ds-info',             // tracé du parcours + aplat des cases visitées
    panel: '--ds-surface',         // fond des pop-ups
    panelBorder: '--ds-border-strong',
    text: '--ds-text',
    // Couleurs des quatre boutons du menu, résolues à l'affichage (et non
    // stockées à la construction) pour suivre les bascules de thème.
    easy: '--ds-success',
    medium: '--ds-warning',
    hard: '--ds-danger',
    blind: '--ds-info',
}

const PALETTE = {}

// Attention : en p5 1.x, color(uneP5Color) RETOURNE LE MÊME OBJET (compatibilité
// ascendante) et setAlpha() le mute sur place. Une variante transparente doit
// donc repartir des composantes, sinon on altère la couleur partagée de la
// palette pour tout le reste du jeu.
function withAlpha(c, alpha) {
    return color(red(c), green(c), blue(c), constrain(alpha, 0, 255))
}

// À n'appeler qu'une fois p5 initialisé : color() n'existe pas avant setup().
function refreshPalette() {
    if (typeof color !== 'function') return
    const css = getComputedStyle(document.documentElement)
    for (const key in PALETTE_TOKENS) {
        PALETTE[key] = color(css.getPropertyValue(PALETTE_TOKENS[key]).trim() || '#888')
    }
    // Variantes dérivées
    // Aplat des cases déjà visitées (touche P) : il était opaque et masquait
    // à la fois les murs et le tracé du parcours — inutilisable en jeu.
    PALETTE.visited = withAlpha(PALETTE.path, 38)
    // Pop-ups : quasi opaques. Elles l'étaient bien moins (alpha 200) et les murs
    // du labyrinthe traversaient le message ; on n'en garde qu'un soupçon.
    PALETTE.panelFill = withAlpha(PALETTE.panel, 249)
}

window.addEventListener('benbb96:themechange', refreshPalette)
