const apiUrl = '/fr/super-moite-moite/api'
const headers = {
    "Content-type": "application/json; charset=UTF-8",
    "X-CSRFToken": Cookies.get('csrftoken')
}
const idProfilConnecte = JSON.parse($('#idProfilConnecte').text())
const logement = JSON.parse($('#logement').text())

function status(response) {
    if (response.status >= 200 && response.status < 300) {
        return Promise.resolve(response)
    } else {
        return Promise.reject(new Error(response.statusText))
    }
}

function json(response) {
    return response.json()
}

function catchError(error) {
    console.log('Request failed', error);
    alert("Une erreur s'est produite lors de la requête")
}

$(() => {
    $('#modalDetailTache').on('shown.bs.modal', function (e) {
        // Focus le cham commentaire après l'ouverture de la modal
        $('input#commentaire').focus()
    });
})

Vue.component('apexchart', VueApexCharts)

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        idProfilConnecte: parseInt(idProfilConnecte),
        logement: logement,
        nomNouvelleCategorie: "",
        commentaireTrack: "",
        nomsNouvelleTache: {},
        categorieEnEdition: null,
        nomCategorieEdition: "",
        erreursNomCategorieEdition: [],
        couleurCategorieEdition: "",
        erreursCouleurCategorieEdition: [],
        tacheEditee: {
            id: null,
            nom: "",
            description: "",
            categorie: null,
            photo: "",
            get_photo_url: "",
            tracks: [],
            point_profils: [],
            displayProgress: "none"
        },
        bootstrapClassColors: [
            'success', 'primary', 'danger', 'warning', 'info'
        ]
    },
    computed: {
        chartOptions: function () {
            return  {
                chart: {
                    width: 350,
                    type: 'pie',
                },
                labels: this.logement.categories.map(categorie => categorie.nom),
                colors: this.logement.categories.map(categorie => categorie.couleur),
                tooltip: {
                    theme: 'dark',
                    fillSeriesColor: false,
                    y: {
                        formatter: function(value, { series, seriesIndex, dataPointIndex, w }) {
                            return value + ' point' + (value > 1 ? 's' : '')
                        }
                    }
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            width: 200
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            }
        }
    },
    methods: {
        chartSeriesHabitant: function(habitant) {
            const ap = this
            return ap.logement.categories.map(categorie =>
                ap.pointsCategorieProfil(categorie, habitant)
            )
        },
        chartSeriesTotal: function() {
            const ap = this
            return this.logement.categories.map(categorie =>
                ap.logement.habitants.reduce((total, profil) => total + ap.pointsCategorieProfil(categorie, profil), 0)
            )
        },
        nouvelleCategorie: function () {
            const ap = this
            if (ap.nomNouvelleCategorie === '') {
                alert('Veuillez saisir un nom pour la nouvelle catégorie.')
                return
            }
            const body = JSON.stringify({
                nom: ap.nomNouvelleCategorie,
                logement: ap.logement.id
            })
            fetch(`${apiUrl}/categories`, {
                method: 'post',
                headers: headers,
                body: body
            })
                .then(status)
                .then(json)
                .then(function (newCategory) {
                    logement.categories.push(newCategory)
                    ap.nomNouvelleCategorie = ''
                })
                .catch(catchError);
        },
        editionCategorie: function(categorie) {
            this.categorieEnEdition = categorie.id
            this.nomCategorieEdition = categorie.nom
            this.couleurCategorieEdition = categorie.couleur
            this.erreursNomCategorieEdition = []
            this.erreursCouleurCategorieEdition = []
        },
        enregistreEditionCategorie: function(categorie) {
            const ap = this
            ap.erreursNomCategorieEdition = []
            ap.erreursCouleurCategorieEdition = []
            const body = JSON.stringify({
                nom: ap.nomCategorieEdition,
                couleur: ap.couleurCategorieEdition
            })
            fetch(`${apiUrl}/categories/${this.categorieEnEdition}`, {
                method: 'patch',
                headers: headers,
                body: body
            })
                .then(function status(response) {
                    if (response.status >= 200 && response.status < 300) {
                        json(response)
                            .then(categorieEditee => {
                                categorie.nom = categorieEditee.nom
                                categorie.couleur = categorieEditee.couleur
                                ap.categorieEnEdition = null
                                ap.nomCategorieEdition = ""
                                ap.couleurCategorieEdition = ""
                            })
                    } else if (response.status === 400) {
                        console.log('Request failed', response.statusText);
                        json(response)
                            .then(error => {
                                if ('nom' in error) {
                                    ap.erreursNomCategorieEdition = error.nom
                                }
                                if ('couleur' in error) {
                                    ap.erreursCouleurCategorieEdition = error.couleur
                                }
                            })
                    } else {
                        catchError(new Error(response.statusText))
                    }
                })
        },
        allLogementTaches : function() {
            let taches = []
            logement.categories.forEach(categorie => taches = taches.concat(categorie.taches))
            return taches
        },
        nouvelleTache: function (categorie) {
            const ap = this
            if (ap.nomsNouvelleTache[categorie.id] === '') {
                alert('Veuillez saisir un nom pour la nouvelle tâche.')
                return
            }
            const body = JSON.stringify({
                nom: ap.nomsNouvelleTache[categorie.id],
                categorie: categorie.id
            })
            fetch(`${apiUrl}/taches`, {
                method: 'post',
                headers: headers,
                body: body
            })
                .then(status)
                .then(json)
                .then(function (newTask) {
                    categorie.taches.push(newTask)
                    ap.nomsNouvelleTache[categorie.id] = ''
                })
                .catch(catchError);
        },
        ajoutTrack: function (tache, datetime=undefined) {
            const ap = this
            const body = JSON.stringify({
                tache: tache.id,
                commentaire: ap.commentaireTrack,
                datetime: datetime
            })
            fetch(`${apiUrl}/track-taches`, {
                method: 'post',
                headers: headers,
                body: body
            })
                .then(status)
                .then(json)
                .then(function (newTrack) {
                    // Ajoute le nouveau track à la tâche
                    tache.tracks.unshift(newTrack)
                    if (tache.tacheOriginale) {
                        // A la tache originale dans le cas d'une édition
                        tache.tacheOriginale.tracks.unshift(newTrack)
                    }
                    // Et à la liste des tracks de l'habitant
                    logement.habitants.find(profil => profil.id === newTrack.profil).tache_tracks.unshift(newTrack)
                    ap.commentaireTrack = ""
                })
                .catch(catchError);
        },
        supprimerTrack: function(track) {
            const ap = this
            if (confirm('Êtes-vous certain de vouloir supprimer ce track ?')) {
                fetch(`${apiUrl}/track-taches/${track.id}`, {
                    method: 'delete',
                    headers: headers,
                })
                    .then(status)
                    .then(function () {
                        ap.tacheEditee.tracks = ap.tacheEditee.tracks.filter(t => track.id !== t.id)
                        ap.tacheEditee.tacheOriginale.tracks = ap.tacheEditee.tacheOriginale.tracks.filter(t => track.id !== t.id)
                    })
                    .catch(catchError);
            }
        },
        pointParDefautProfil: function (tache, profil) {
            // Trouve le nombre de point que vaut cette tâche pour ce profil (1 par défaut)
            const pointProfil = tache.point_profils.find(pointProfil => pointProfil.profil === profil.id)
            if (pointProfil !== undefined) {
                return pointProfil.point
            }
            return 1
        },
        changePointParDefautProfil: function (tache, profil, point) {
            point = parseInt(point)
            let pointProfil = tache.point_profils.find(pointProfil => pointProfil.profil === profil.id)
            if (pointProfil !== undefined) {
                // Met à jour la valeur de point
                pointProfil.point = point
            } else {
                // Ajoute le point par profil
                tache.point_profils.push({
                    tache: tache.id,
                    profil: profil.id,
                    point: point
                })
            }
        },
        pointsTacheProfil: function (tache, profil) {
            // Récupère le nombre de point par défaut de ce profil pour cette tâche
            const pointParDefaut = this.pointParDefautProfil(tache, profil)
            // Parcours les tâches du profil et fait le total de ces points
            return tache.tracks.filter(pointProfil => pointProfil.profil === profil.id)
                .reduce(totalPoints => totalPoints + pointParDefaut, 0)
        },
        pointsCategorieProfil: function (categorie, profil) {
            return categorie.taches.reduce((totalPoints, tache) => totalPoints + this.pointsTacheProfil(tache, profil), 0)
        },
        pointsProfil: function (profil) {
            return this.logement.categories.reduce(
                (totalPoints, categorie) => totalPoints + this.pointsCategorieProfil(categorie, profil),
                0
            )
        },
        totalPoints: function() {
            return this.logement.habitants.reduce(
                (total, habitant) => total + this.pointsProfil(habitant),
                0
            )
        },
        pourcentagePointProfil: function(profil) {
            if (this.totalPoints() === 0) return 0
            return (this.pointsProfil(profil) / this.totalPoints()) * 100
        },
        totalCategorieTracks: (categorie) =>
            categorie.taches.reduce((total, tache) => total + tache.tracks.length, 0)
        ,
        totalTracks: function() {
            return this.logement.categories.reduce(
                (total, categorie) => total + this.totalCategorieTracks(categorie),
                0
            )
        },
        totalProfilTracks: function(profil) {
            const ap = this
            return profil.tache_tracks.filter(
                track => ap.allLogementTaches().some(tache => tache.id === track.tache)
            ).length
        },
        detailTache: function (tache, ouvreTracks=false) {
            // Effectue une copie profonde de la tâche pour l'éditer sans toucher à l'originale
            this.tacheEditee = _.cloneDeep(tache)
            this.tacheEditee.tacheOriginale = tache
            if (ouvreTracks) {
                // Ouvre l'onglet des tracks
                $('a[href=#tracks]').trigger('click')
            } else {
                // L'onglet détail doit être affiché en premier par défaut
                $('a[href=#detail]').trigger('click')
            }
            // Ré-initialise le commentaire d'ajout de Track
            this.commentaireTrack = ""
            // Ouvre la modale d'édition
            $('#modalDetailTache').modal()
        },
        supprimerTache: function (tache) {
            if (confirm('Êtes-vous certain de vouloir supprimer cette tâche ?')) {
                fetch(`${apiUrl}/taches/${tache.id}`, {
                    method: 'delete',
                    headers: headers,
                })
                    .then(status)
                    .then(function () {
                        let categorie = logement.categories.find(categorie => categorie.id === tache.categorie)
                        // Retire la tâche qui vientr d'être supprimée
                        categorie.taches = categorie.taches.filter(task => task.id !== tache.id)
                        $('#modalDetailTache').modal('hide')
                    })
                    .catch(catchError);
            }
        },
        enregistrerModifTache: function (tache) {
            let logement = this.logement
            // Enregistre les points par profil
            logement.habitants.forEach(function (habitant) {
                let pointProfil = tache.point_profils.find(pointProfil => pointProfil.profil === habitant.id)
                if (pointProfil !== undefined) {
                    if (pointProfil.id) {
                        fetch(`${apiUrl}/point-taches/${pointProfil.id}`, {
                            method: 'patch',
                            headers: headers,
                            body: JSON.stringify({point: pointProfil.point})
                        })
                            .then(status)
                            .catch(catchError);
                    } else {
                        fetch(`${apiUrl}/point-taches`, {
                            method: 'post',
                            headers: headers,
                            body: JSON.stringify(pointProfil)
                        })
                            .then(status)
                            .then(json)
                            .then(function (newPointProfil) {
                                tache.point_profils.push(newPointProfil)
                            })
                            .catch(catchError);
                    }
                }
            })

            // Enregistre les modifications des infos de la tâche
            fetch(`${apiUrl}/taches/${tache.id}`, {
                method: 'put',
                headers: headers,
                body: JSON.stringify({
                    categorie: tache.categorie,
                    nom: tache.nom,
                    description: tache.description,
                    photo: tache.photo
                })
            })
                .then(status)
                .then(json)
                .then(function (editTache) {
                    let categorie = logement.categories.find(categorie => categorie.id === editTache.categorie)
                    // Met à jour la tâche avec les nouvelles valeurs
                    categorie.taches = categorie.taches.map(tache => tache.id === editTache.id ? editTache : tache)

                    // Ferme la modal
                    $('#modalDetailTache').modal('hide')
                })
                .catch(catchError);
        }
    },
    filters: {
        moment: function (date) {
            return moment(date).format('LLL');
        },
        round: function (value, decimals) {
            if (!value) {
                value = 0;
            }
            if (!decimals) {
                decimals = 0;
            }
            value = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
            return value;
        }
    }
});