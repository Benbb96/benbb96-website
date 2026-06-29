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
let start = moment().subtract(1, 'month')
let end = moment()

const dateRangeOptions = {
    showDropdowns: true,
    timePicker: true,
    timePicker24Hour: true,
    startDate: start,
    endDate: end,
    minDate: minDate,
    maxDate: maxDate,
    locale: {
        format: 'LLLL',
        applyLabel: "OK",
        cancelLabel: "Annuler",
        fromLabel: "De",
        toLabel: "A",
        customRangeLabel: "Personnalisé",
        weekLabel: "W",
        daysOfWeek: [
            "Di",
            "Lu",
            "Ma",
            "Me",
            "Je",
            "Ve",
            "Sa"
        ],
        monthNames: [
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre"
        ]
    },
    ranges: {
       'Les 7 derniers jours': [moment().subtract(6, 'days'), moment()],
       'Les 30 derniers jours': [moment().subtract(1, 'month'), moment()],
       'Les 3 derniers mois': [moment().subtract(3, 'month'), moment()],
       'Les 6 derniers mois': [moment().subtract(6, 'month'), moment()],
       'Les 12 derniers mois': [moment().subtract(1, 'year'), moment()],
       'Les 2 dernières années': [moment().subtract(2, 'year'), moment()],
       'Les 3 dernières années': [moment().subtract(3, 'year'), moment()],
       'Les 5 dernières années': [moment().subtract(5, 'year'), moment()],
       'Tous': [minDate, maxDate],
    }
}

const update_track_graph = (frequency = 'D') => {
    $.post(trackerDataUrl, {id: trackerIds, frequency, start, end})
        .done(response => {
            if (response.labels.length > 0) {
                $('div#noTracks').addClass('ds-hidden')
                $('div#track_graph').removeClass('ds-hidden')

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
                            fill: false,
                        })
                    } else {
                        chartDatasets.push({
                            label: dataset.label,
                            data: dataset.data,
                            backgroundColor: dataset.backgroundColor,
                        })
                    }
                })

                allTracks.data.labels = response.labels
                allTracks.data.datasets = chartDatasets
                allTracks.update()

                $('span#frequency').text(frequency_map[frequency])
                if (response.averages.length > 0) {
                    const avg = response.averages[0]
                    $('strong#avg').text(avg.avg)
                    if (avg.isValeur) {
                        $('span#valMin').text(avg.min)
                        $('span#valMax').text(avg.max)
                    }
                }
                $('.btn-frequency').removeClass('is-active')
                $('.btn-frequency[data-frequency=' + frequency + ']').addClass('is-active')
            } else {
                $('div#track_graph').addClass('ds-hidden')
                $('div#noTracks').removeClass('ds-hidden')
            }
        })
        .fail((xhr, textStatus, errorThrown) => {
            console.error('(' + errorThrown + ') ' + (xhr.responseJSON !== undefined ? xhr.responseJSON.error : textStatus))
        })
}

$(() => {
    $('.btn-frequency').click(function () {
        update_track_graph($(this).data('frequency'))
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