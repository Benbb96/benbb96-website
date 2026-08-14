// HUD, records et commandes tactiles — la partie du jeu qui vit hors du canvas
//
// Niveau, chrono et record sont du HTML plutôt que du texte dessiné dans le
// canvas : ils sont ainsi thémés par le CSS, sélectionnables, et annoncés par un
// lecteur d'écran. draw() tourne à 60 fps, donc on n'écrit dans le DOM que
// lorsqu'une valeur change réellement.

const BEST_STORAGE_KEY = 'benbb96-labyrinthe-best'

const MODE_NAMES = { 1: 'Easy', 2: 'Medium', 3: 'Hard', 4: 'Blind' }

let soundEnabled = true

// Records par mode : { "<mode>": { level: n, time: ms } }.
// level = plus haut niveau atteint, time = meilleur temps sur un seul labyrinthe.
let bests = {}

function loadBests() {
    try {
        bests = JSON.parse(localStorage.getItem(BEST_STORAGE_KEY)) || {}
    } catch (e) {
        bests = {} // localStorage indisponible (navigation privée) : on joue sans records
    }
}

function persistBests() {
    try {
        localStorage.setItem(BEST_STORAGE_KEY, JSON.stringify(bests))
    } catch (e) {
        /* stockage refusé : le record reste valable pour la session en cours */
    }
}

function bestFor(gameMode) {
    return bests[gameMode] || { level: 0, time: 0 }
}

// Enregistre le plus haut niveau atteint dans le mode courant.
function recordLevel(reachedLevel) {
    const best = bestFor(mode)
    if (reachedLevel > best.level) {
        bests[mode] = { level: reachedLevel, time: best.time }
        persistBests()
    }
}

// Enregistre le meilleur temps sur un labyrinthe unique.
function recordMazeTime(ms) {
    const best = bestFor(mode)
    if (ms > 0 && (best.time === 0 || ms < best.time)) {
        bests[mode] = { level: best.level, time: ms }
        persistBests()
    }
}

// Déblocage de l'AudioContext.
// Les navigateurs le créent en état « suspended » et p5.sound ne le réveille
// PAS tout seul (il expose userStartAudio() mais ne l'appelle jamais) : sans
// cela, loadSound() réussit, play() est bien appelé… et aucun son ne sort. Le
// symptôme visible est l'avertissement « An AudioContext was prevented from
// starting automatically » dans la console. L'appel doit se faire depuis un
// VRAI geste utilisateur, d'où les écouteurs ci-dessous plutôt qu'un appel au
// chargement.
let audioUnlocked = false

function unlockAudio() {
    if (audioUnlocked || typeof userStartAudio !== 'function') return
    audioUnlocked = true
    const resumed = userStartAudio()
    // En cas d'échec, on retentera au geste suivant.
    if (resumed && resumed.catch) resumed.catch(() => { audioUnlocked = false })
}

// En capture et sans { once: true } : un seul point d'entrée qui couvre le
// canvas, le pavé directionnel, les boutons du HUD et le clavier. unlockAudio()
// sort immédiatement une fois le déblocage acquis.
document.addEventListener('pointerdown', unlockAudio, true)
document.addEventListener('keydown', unlockAudio, true)

// Joue un son en respectant le bouton muet (les sons se déclenchaient sans
// qu'on puisse les couper).
function playSound(sound) {
    if (soundEnabled && sound && sound.isLoaded()) sound.play()
}

// ── Écriture du HUD ─────────────────────────────────────────────────────────

const hudCache = {}

function hudSet(name, value) {
    if (hudCache[name] === value) return // évite un accès DOM par frame
    hudCache[name] = value
    const el = document.querySelector('[data-laby-' + name + ']')
    if (el) el.textContent = value
}

function updateHud() {
    const inGame = state !== MENU
    // Dans le menu, on affiche le mode SURLIGNÉ et son record : sinon on lisait
    // « mode — » à côté d'un record dont on ne savait pas à quel mode il se
    // rapportait. En partie, c'est le mode réellement chargé.
    const shownMode = inGame ? mode : buttons[selectedButton].buttonMode

    hudSet('mode', MODE_NAMES[shownMode] || '—')
    hudSet('level', inGame ? String(niveau) : '—')
    hudSet('time', inGame && timer ? timer.getDisplay() : '—')

    const best = bestFor(shownMode)
    hudSet(
        'best',
        best.level ? 'niveau ' + best.level + (best.time ? ' · ' + formatDuration(best.time) : '') : '—'
    )
}

// ── Commandes tactiles & boutons du HUD ─────────────────────────────────────
// Le pavé directionnel est du HTML : sur mobile, le jeu n'avait aucune commande
// (ni clavier, ni tactile) et était donc simplement injouable.

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-laby-dir]').forEach(function (btn) {
        // pointerdown plutôt que click : réponse immédiate, et les appuis
        // répétés d'un joueur pressé ne sont pas avalés par la détection de
        // double-tap des navigateurs mobiles.
        btn.addEventListener('pointerdown', function (event) {
            event.preventDefault()
            inputDirection(DIRECTION_KEYS[btn.dataset.labyDir])
        })
    })

    const pauseBtn = document.querySelector('[data-laby-pause]')
    if (pauseBtn) pauseBtn.addEventListener('click', inputPause)

    const confirmBtn = document.querySelector('[data-laby-confirm]')
    if (confirmBtn) confirmBtn.addEventListener('click', inputConfirm)

    const soundBtn = document.querySelector('[data-laby-sound]')
    if (soundBtn) {
        soundBtn.addEventListener('click', function () {
            soundEnabled = !soundEnabled
            soundBtn.setAttribute('aria-pressed', String(soundEnabled))
            soundBtn.classList.toggle('is-off', !soundEnabled)
        })
    }
})
