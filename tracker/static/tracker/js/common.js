/* =============================================================================
   tracker — Logique commune des graphes & du filtre de dates (vanilla)
   =============================================================================
   Remplace jQuery / moment.js / bootstrap-daterangepicker / Chart v2 (vanilla + Intl + Chart v4).
   - dates : deux <input type="date"> natifs + presets calculés en Date ;
   - formatage : Intl.DateTimeFormat (plus de moment) ;
   - requêtes : window.http (fetch + CSRF, plus de $.post/$.ajax) ;
   - graphes : Chart.js v4.
   Les objets Chart (allTracks, trackByHourChart, trackByDayChart), trackerIds,
   trackerDataUrl et la fonction update_all sont fournis par chaque template
   (scope lexical global partagé entre scripts classiques).
   ============================================================================ */
const frequency_map = {
    h: 'heure',
    D: 'jour',
    W: 'semaine',
    ME: 'mois',
    QE: "quart d'année",
    YE: 'an',
}

let allTracks = undefined
let trackByHourChart = undefined
let trackByDayChart = undefined

// ── Theming Chart.js (suit le toggle clair/sombre/auto, sans dépendance) ────
// Chart.js dessine sur <canvas> : ses couleurs par défaut (texte des axes,
// grille, légende) ne suivent pas le CSS. On les recale sur les tokens du
// design system à l'init, puis à chaque changement de thème (voir
// assets/js/theme.js, événement "benbb96:themechange").
// Palette catégorielle (répartition par jour de la semaine, 7 tranches) :
// ordre fixe validé (séparation daltonisme + contraste), cf. skill dataviz.
const DAY_COLORS = {
    light: ['#2a78d6', '#008300', '#e87ba4', '#eda100', '#1baf7a', '#eb6834', '#4a3aa7'],
    dark: ['#3987e5', '#008300', '#d55181', '#c98500', '#199e70', '#d95926', '#9085e9'],
}
function currentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light'
}
function applyChartTheme() {
    if (typeof Chart === 'undefined') return
    const css = getComputedStyle(document.documentElement)
    const text = css.getPropertyValue('--ds-text-muted').trim()
    const grid = css.getPropertyValue('--ds-border').trim()

    Chart.defaults.color = text
    Chart.defaults.scale.grid.color = grid
    Chart.defaults.scale.border.color = grid
    Chart.defaults.scale.ticks.color = text
    Chart.defaults.plugins.legend.labels.color = text

    if (trackByDayChart) {
        trackByDayChart.data.datasets[0].backgroundColor = DAY_COLORS[currentTheme()]
    }
    ;[allTracks, trackByHourChart, trackByDayChart].forEach(chart => { if (chart) chart.update() })
}
applyChartTheme()
window.addEventListener('benbb96:themechange', applyChartTheme)

// Bornes de dates « start »/« end » envoyées au serveur, au format attendu
// par get_tracks_from_request : '%y-%m-%d %H:%M:%S' (année sur 2 chiffres).
let start = undefined
let end = undefined

const TRACK_LOCALE = document.documentElement.lang || 'fr'

function tkPad2(n) { return String(n).padStart(2, '0') }
function toServerDate(d) {
    return `${tkPad2(d.getFullYear() % 100)}-${tkPad2(d.getMonth() + 1)}-${tkPad2(d.getDate())} ` +
        `${tkPad2(d.getHours())}:${tkPad2(d.getMinutes())}:${tkPad2(d.getSeconds())}`
}
function toInputDate(d) {
    return `${d.getFullYear()}-${tkPad2(d.getMonth() + 1)}-${tkPad2(d.getDate())}`
}
// Formatage type moment('LLL') via Intl (utilisé aussi par les templates).
function formatTrackDate(date, options) {
    return new Intl.DateTimeFormat(TRACK_LOCALE, options || { dateStyle: 'long', timeStyle: 'short' })
        .format(new Date(date))
}

function activeFrequency() {
    const btn = document.querySelector('button.btn-frequency.is-active')
    return btn ? btn.dataset.frequency : 'D'
}

// ── Filtre de dates (remplace bootstrap-daterangepicker) ────────────────────
function subtractDate(date, n, unit) {
    const d = new Date(date)
    if (unit === 'days') d.setDate(d.getDate() - n)
    else if (unit === 'month') d.setMonth(d.getMonth() - n)
    else if (unit === 'year') d.setFullYear(d.getFullYear() - n)
    return d
}

let rangeMin = null
let rangeMax = null

const RANGE_PRESETS = {
    '7d': () => [subtractDate(new Date(), 6, 'days'), new Date()],
    '30d': () => [subtractDate(new Date(), 1, 'month'), new Date()],
    '3m': () => [subtractDate(new Date(), 3, 'month'), new Date()],
    '6m': () => [subtractDate(new Date(), 6, 'month'), new Date()],
    '12m': () => [subtractDate(new Date(), 1, 'year'), new Date()],
    '2y': () => [subtractDate(new Date(), 2, 'year'), new Date()],
    '3y': () => [subtractDate(new Date(), 3, 'year'), new Date()],
    '5y': () => [subtractDate(new Date(), 5, 'year'), new Date()],
    'all': () => [rangeMin || new Date(0), rangeMax || new Date()],
}

// Initialise le filtre de dates et déclenche la 1re mise à jour.
function initTrackerDateRange(minIso, maxIso) {
    rangeMin = minIso ? new Date(minIso) : null
    rangeMax = maxIso ? new Date(maxIso) : null

    const startInput = document.getElementById('dateStart')
    const endInput = document.getElementById('dateEnd')
    const preset = document.getElementById('dateRangePreset')
    if (!startInput || !endInput) return

    // Bornes = plage réelle des données trackées, pour éviter de choisir une
    // date hors historique (le navigateur grise les jours interdits).
    if (rangeMin) startInput.min = toInputDate(rangeMin)
    if (rangeMax) endInput.max = toInputDate(rangeMax)

    function syncFromInputs() {
        if (startInput.value) start = toServerDate(new Date(startInput.value + 'T00:00:00'))
        if (endInput.value) end = toServerDate(new Date(endInput.value + 'T23:59:59'))
        // Empêche une fin avant le début (et inversement).
        if (startInput.value) endInput.min = startInput.value
        if (endInput.value) startInput.max = endInput.value
    }
    function setRange(s, e) {
        startInput.value = toInputDate(s)
        endInput.value = toInputDate(e)
        syncFromInputs()
    }
    function applyAndUpdate() {
        syncFromInputs()
        if (typeof update_all === 'function') update_all(activeFrequency())
    }

    if (preset) {
        preset.addEventListener('change', function () {
            const fn = RANGE_PRESETS[preset.value]
            if (fn) {
                const [s, e] = fn()
                setRange(s, e)
                applyAndUpdate()
            }
        })
    }
    startInput.addEventListener('change', function () { if (preset) preset.value = ''; applyAndUpdate() })
    endInput.addEventListener('change', function () { if (preset) preset.value = ''; applyAndUpdate() })

    // Par défaut : les 30 derniers jours (comportement historique).
    const [s, e] = RANGE_PRESETS['30d']()
    if (preset) preset.value = '30d'
    setRange(s, e)
    applyAndUpdate()
}

const update_track_graph = (frequency = 'D') => {
    const body = new FormData()
    trackerIds.forEach(id => body.append('id[]', id))
    body.append('frequency', frequency)
    if (start) body.append('start', start)
    if (end) body.append('end', end)

    window.http.json(trackerDataUrl, { method: 'POST', body: body })
        .then(response => {
            const noTracks = document.getElementById('noTracks')
            const graph = document.getElementById('track_graph')
            if (response.labels.length > 0) {
                if (noTracks) noTracks.classList.add('ds-hidden')
                if (graph) graph.classList.remove('ds-hidden')

                const chartDatasets = []
                response.datasets.forEach(dataset => {
                    if (dataset.trackerType === 'mesure' && dataset.minData && dataset.maxData) {
                        // Zone ombragée entre min et max
                        chartDatasets.push({
                            label: '',
                            data: dataset.minData,
                            borderColor: dataset.backgroundColor,
                            backgroundColor: 'transparent',
                            borderDash: [4, 4],
                            fill: false,
                            pointRadius: 0,
                            borderWidth: 1,
                        })
                        chartDatasets.push({
                            label: '',
                            data: dataset.maxData,
                            borderColor: dataset.backgroundColor,
                            backgroundColor: dataset.backgroundColor,
                            borderDash: [4, 4],
                            fill: '-1',
                            pointRadius: 0,
                            borderWidth: 1,
                        })
                        // Ligne principale (moyenne)
                        chartDatasets.push({
                            label: dataset.label,
                            data: dataset.data,
                            backgroundColor: dataset.backgroundColor,
                            borderColor: dataset.backgroundColor,
                            fill: false,
                        })
                    } else {
                        chartDatasets.push({
                            label: dataset.label,
                            data: dataset.data,
                            backgroundColor: dataset.backgroundColor,
                            borderColor: dataset.backgroundColor,
                        })
                    }
                })

                allTracks.data.labels = response.labels
                allTracks.data.datasets = chartDatasets
                allTracks.update()

                const freqEl = document.getElementById('frequency')
                if (freqEl) freqEl.textContent = frequency_map[frequency]
                if (response.averages.length > 0) {
                    const avg = response.averages[0]
                    const avgEl = document.getElementById('avg')
                    if (avgEl) avgEl.textContent = avg.avg
                    if (avg.isValeur) {
                        const minEl = document.getElementById('valMin')
                        const maxEl = document.getElementById('valMax')
                        if (minEl) minEl.textContent = avg.min
                        if (maxEl) maxEl.textContent = avg.max
                    }
                }
                document.querySelectorAll('.btn-frequency').forEach(b => b.classList.remove('is-active'))
                const activeBtn = document.querySelector('.btn-frequency[data-frequency="' + frequency + '"]')
                if (activeBtn) activeBtn.classList.add('is-active')
            } else {
                if (graph) graph.classList.add('ds-hidden')
                if (noTracks) noTracks.classList.remove('ds-hidden')
            }
        })
        .catch(error => {
            console.error('Erreur de chargement du graphe', error)
        })
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.btn-frequency').forEach(function (btn) {
        btn.addEventListener('click', function () {
            update_track_graph(btn.dataset.frequency)
        })
    })
})

// Onglets maison (.ds-tabs[data-tabs]) — bascule vanilla des panneaux .ds-tab-panel,
// avec sémantique ARIA (tablist/tab/tabpanel) et navigation clavier (flèches, Home/End).
// Remplace le comportement data-toggle="tab" de Bootstrap. Sans JS, les onglets
// restent des ancres pointant vers les panneaux (dégradation propre).
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.ds-tabs[data-tabs]').forEach(function (tabs) {
        const links = Array.from(tabs.querySelectorAll('.ds-tabs__item > a[href^="#"]'));
        if (!links.length) return;

        tabs.setAttribute('role', 'tablist');

        function panelFor(link) {
            return document.getElementById(link.getAttribute('href').slice(1));
        }

        // Rôles ARIA + état initial (roving tabindex : seul l'onglet actif est tabulable).
        links.forEach(function (link) {
            const panel = panelFor(link);
            const selected = link.parentElement.classList.contains('is-active');
            link.setAttribute('role', 'tab');
            link.setAttribute('aria-selected', selected ? 'true' : 'false');
            link.setAttribute('tabindex', selected ? '0' : '-1');
            if (panel) {
                if (!link.id) link.id = panel.id + '-tab';
                panel.setAttribute('role', 'tabpanel');
                panel.setAttribute('aria-labelledby', link.id);
                panel.setAttribute('tabindex', '0');
                link.setAttribute('aria-controls', panel.id);
            }
        });

        function activate(link, setFocus) {
            links.forEach(function (other) {
                const isActive = other === link;
                other.parentElement.classList.toggle('is-active', isActive);
                other.setAttribute('aria-selected', isActive ? 'true' : 'false');
                other.setAttribute('tabindex', isActive ? '0' : '-1');
                const panel = panelFor(other);
                if (panel) panel.classList.toggle('is-active', isActive);
            });
            if (setFocus) link.focus();
        }

        links.forEach(function (link, index) {
            link.addEventListener('click', function (event) {
                event.preventDefault();
                activate(link, false);
            });
            link.addEventListener('keydown', function (event) {
                let target = null;
                switch (event.key) {
                    case 'ArrowRight':
                    case 'ArrowDown':
                        target = links[(index + 1) % links.length];
                        break;
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        target = links[(index - 1 + links.length) % links.length];
                        break;
                    case 'Home':
                        target = links[0];
                        break;
                    case 'End':
                        target = links[links.length - 1];
                        break;
                    default:
                        return;
                }
                event.preventDefault();
                activate(target, true);
            });
        });
    });
});
