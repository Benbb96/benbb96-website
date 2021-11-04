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

function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip();
}

$(() => {
    $('#modalDetailTache').on('shown.bs.modal', function (e) {
        // Focus le cham commentaire après l'ouverture de la modal
        $('input#commentaire').focus()
    });

    initTooltips()
})

Vue.component('apexchart', VueApexCharts)

let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        searchText: "",
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
            photo_url: "",
            tracks: [],
            point_profils: [],
            displayProgress: "none"
        },
        trackEditee: {
            id: null,
            commentaire: "",
            datetime: "",
            profil: null
        },
        bootstrapClassColors: [
            'success', 'info', 'danger', 'warning', 'primary'
        ]
    },
    computed: {
        categoriesFiltrees: function() {
            const ap = this
            if (ap.searchText) {
                return ap.logement.categories.filter(categorie => {
                    return categorie.nom.toLowerCase().includes(ap.searchText.toLowerCase()) ||
                        categorie.taches.filter(tache => tache.nom.toLowerCase().includes(ap.searchText.toLowerCase())).length
                })
            }
            return ap.logement.categories
        },
        chartOptions: function () {
            return  {
                chart: {
                    type: 'donut',
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
                            width: 300
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
        nombreProfilTracks: function (profil, tache) {
            return tache.tracks.filter(track => track.profil === profil.id).length
        },
        categorieTachesFiltrees: function(categorie) {
            const ap = this
            if (ap.searchText) {
                return categorie.taches.filter(tache => {
                    return tache.nom.toLowerCase().includes(ap.searchText.toLowerCase())
                })
            }
            return categorie.taches
        },
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
            setTimeout(initTooltips, 10);  // Wait to have the DOM changed by vue
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
                method: 'PATCH',
                headers: headers,
                body: body
            })
                .then(function status(response) {
                    console.log(response)
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
        supprimerCategorie: function(categorie) {
            const ap = this
            if (confirm(`Êtes-vous certain de vouloir supprimer la catégorie ${categorie.nom} ?`)) {
                fetch(`${apiUrl}/categories/${categorie.id}`, {
                    method: 'delete',
                    headers: headers,
                })
                    .then(status)
                    .then(function () {
                        // Retire la catégorie qui vient d'être supprimée
                        ap.logement.categories = ap.logement.categories.filter(cat => cat.id !== categorie.id)
                    })
                    .catch(catchError);
            }
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
        editerTrack: function(track) {
            this.trackEditee.id = track.id
            this.trackEditee.commentaire = track.commentaire
            this.trackEditee.profil = track.profil
            this.trackEditee.datetime = moment(track.datetime).format("YYYY-MM-DDTHH:mm")
        },
        enregistreEditionTrack: function(track) {
            const ap = this
            const body = JSON.stringify(ap.trackEditee)
            fetch(`${apiUrl}/track-taches/${track.id}`, {
                method: 'PATCH',
                headers: headers,
                body: body
            })
                .then(status)
                .then(json)
                .then(function (trackEditee) {
                    // Met à jour le track avec les nouvelles valeurs
                    ap.tacheEditee.tracks = ap.tacheEditee.tracks.map(track => track.id === trackEditee.id ? trackEditee: track)
                    // Met à jour aussi le track dans la tâche originale
                    ap.tacheEditee.tacheOriginale.tracks = ap.tacheEditee.tacheOriginale.tracks.map(track => track.id === trackEditee.id ? trackEditee: track)
                    // Ré-initialise le track en édition
                    ap.trackEditee.id = null
                    ap.trackEditee.commentaire = ""
                    ap.trackEditee.datetime = ""
                    ap.trackEditee.profil = null
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
            return tache.tracks.filter(pointProfil => pointProfil.profil === profil.id).length * pointParDefaut
        },
        pointsCategorieProfil: function (categorie, profil) {
            return categorie.taches.reduce((totalPoints, tache) => totalPoints + this.pointsTacheProfil(tache, profil), 0)
        },
        pointsDefautCategorieProfil: function (categorie, profil) {
            return categorie.taches.reduce((totalPointsDefaut, tache) => totalPointsDefaut + this.pointParDefautProfil(tache, profil), 0)
        },
        pointsProfil: function (profil) {
            return this.logement.categories.reduce(
                (totalPoints, categorie) => totalPoints + this.pointsCategorieProfil(categorie, profil),
                0
            )
        },
        totalPointsParDefautProfil: function (profil) {
            return this.logement.categories.reduce(
                (totalPointsDefaut, categorie) => totalPointsDefaut + this.pointsDefautCategorieProfil(categorie, profil),
                0
            )
        },
        totalPointsTache: function(tache) {
            return this.logement.habitants.reduce(
                (total, habitant) => total + this.pointsTacheProfil(tache, habitant),
                0
            )
        },
        totalPointsCategorie: function(categorie) {
            return this.logement.habitants.reduce(
                (total, habitant) => total + this.pointsCategorieProfil(categorie, habitant),
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
        pourcentagePointProfilCategorie: function(profil, categorie) {
            if (this.totalPointsCategorie(categorie) === 0) return 0
            return (this.pointsCategorieProfil(categorie, profil) / this.totalPointsCategorie(categorie)) * 100
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
        detailTache: function (tache, tabId='tracks') {
            // Effectue une copie profonde de la tâche pour l'éditer sans toucher à l'originale
            this.tacheEditee = _.cloneDeep(tache)
            this.tacheEditee.tacheOriginale = tache
            // Ré-initialise le commentaire d'ajout de Track
            this.commentaireTrack = ""
            // Ouvre la modale d'édition
            $('#modalDetailTache').modal()
            // Sélectionne l'onglet à ouvrir
            $('a[href=#' + tabId + ']').trigger('click')
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
                        // Retire la tâche qui vient d'être supprimée
                        categorie.taches = categorie.taches.filter(task => task.id !== tache.id)
                        $('#modalDetailTache').modal('hide')
                    })
                    .catch(catchError);
            }
        },
        updatePhotoUrl: function(url) {
            if (url.startsWith('http')) {
                const ap = this
                // Essaye de récupérer l'image pour voir si on l'affiche
                fetch("https://cors-anywhere.herokuapp.com/" + url)
                    .then(function (response) {
                        if (response.status === 200) {
                            ap.tacheEditee.photo_url = url
                        } else {
                            alert("Impossible de récupérer l'image via cette URL...")
                        }
                    }).catch(function (error) {
                        alert(error)
                })
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
                            method: 'PATCH',
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
        },
        orderCategories: function () {
            const ap = this
            // Parcourt toutes les catégories et remet à jour leur ordre en fonction du nouveau tri
            for (let [key, value] of Object.entries(this.$refs.categories)) {
                key = parseInt(key)
                const categorieId = parseInt(value.dataset.id);
                // Effectue la mise à jour seulement si sa position a changée
                if (ap.logement.categories.find(categorie => categorie.id === categorieId).order !== key) {
                    fetch(`${apiUrl}/categories/${categorieId}`, {
                        method: 'PATCH',
                        headers: headers,
                        body: JSON.stringify({order: key})
                    })
                        .then(status)
                        .then(json)
                        .then(function(categorieEditee) {
                            ap.logement.categories.find(categorie => categorie.id === categorieId).order = categorieEditee.order
                        })
                        .catch(catchError)
                }
            }
        },
        orderTaches: function (categorie) {
            // Parcourt toutes les tâches et remet à jour leur ordre en fonction du nouveau tri
            for (let [key, value] of Object.entries(this.$refs['taches' + categorie.id])) {
                key = parseInt(key)
                const tacheId = parseInt(value.dataset.id);
                // Effectue la mise à jour seulement si sa position a changée
                if (categorie.taches.find(tache => tache.id === tacheId).order !== key) {
                    fetch(`${apiUrl}/taches/${tacheId}`, {
                        method: 'PATCH',
                        headers: headers,
                        body: JSON.stringify({order: key})
                    })
                        .then(status)
                        .then(json)
                        .then(function(tacheEditee) {
                            categorie.taches.find(tache => tache.id === tacheId).order = tacheEditee.order
                        })
                        .catch(catchError)
                }
            }
        }
    },
    filters: {
        moment: function (date, format='LLL') {
            return moment(date).format(format);
        },
        fromNow: function (date) {
            return moment(date).fromNow();
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