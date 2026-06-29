/* =============================================================================
   tracker — Logique commune des graphes & du filtre de dates (vanilla)
   =============================================================================
   Phase 5a : remplace jQuery / moment.js / bootstrap-daterangepicker / Chart v2.
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

    function syncFromInputs() {
        if (startInput.value) start = toServerDate(new Date(startInput.value + 'T00:00:00'))
        if (endInput.value) end = toServerDate(new Date(endInput.value + 'T23:59:59'))
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

// Onglets maison (.ds-tabs) — bascule vanilla des panneaux .ds-tab-panel.
// Remplace le comportement data-toggle="tab" de Bootstrap.
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.ds-tabs[data-tabs]').forEach(function (tabs) {
        const items = tabs.querySelectorAll('.ds-tabs__item');
        items.forEach(function (item) {
            const link = item.querySelector('a[href^="#"]');
            if (!link) return;
            link.addEventListener('click', function (event) {
                event.preventDefault();
                const targetId = link.getAttribute('href').slice(1);
                items.forEach(i => i.classList.remove('is-active'));
                item.classList.add('is-active');
                const target = document.getElementById(targetId);
                if (target) {
                    const group = target.parentElement;
                    group.querySelectorAll(':scope > .ds-tab-panel').forEach(p => p.classList.remove('is-active'));
                    target.classList.add('is-active');
                }
            });
        });
    });
});
