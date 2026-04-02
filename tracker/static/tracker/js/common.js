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
                $('div#noTracks').addClass('hidden')
                $('div#track_graph').removeClass('hidden')
                allTracks.data.labels = response.labels
                allTracks.data.datasets = response.datasets
                allTracks.update()
                $('span#frequency').text(frequency_map[frequency])
                $('strong#avg').text(response.averages[0].avg)
                $('.btn-frequency').removeClass('btn-primary')
                $('.btn-frequency[data-frequency=' + frequency + ']').addClass('btn-primary')
            } else {
                $('div#track_graph').addClass('hidden')
                $('div#noTracks').removeClass('hidden')
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