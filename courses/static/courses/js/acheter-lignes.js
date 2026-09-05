/* Courses — actions de « À acheter » sans rechargement (cf. inventaire-steppers.js).
   Cocher fait apparaître le champ quantité : le serveur renvoie la rangée re-rendue
   plutôt que des champs à recomposer ici. Sans JS : POST + redirect ancré. */
(function (document) {
    'use strict';

    var SELECTEUR_FORMS = '[data-ligne-row] form';

    function majCompteur() {
        var compteur = document.querySelector('[data-panier-compteur]');
        if (!compteur) return;
        var rangees = document.querySelectorAll('[data-ligne-row]');
        var cochees = document.querySelectorAll('[data-ligne-row].is-checked');
        compteur.textContent = cochees.length + ' / ' + rangees.length;
    }

    function remplacer(rangee, html) {
        var gabarit = document.createElement('div');
        gabarit.innerHTML = html.trim();
        var neuve = gabarit.firstElementChild;
        if (!neuve) return;
        rangee.replaceWith(neuve);
        brancher(neuve);
        majCompteur();
        // acheter-filtre.js réapplique « Masquer le panier » sur la rangée neuve.
        document.dispatchEvent(new CustomEvent('courses:ligne-maj'));
    }

    function intercepter(form) {
        form.addEventListener('submit', function (event) {
            var rangee = form.closest('[data-ligne-row]');
            if (!rangee || typeof window.http === 'undefined') return; // dégradation native

            event.preventDefault();
            window.http
                .json(form.action, { method: 'POST', body: new FormData(form) })
                .then(function (donnees) {
                    // Conflit §5.1 : l'avertissement n'existe qu'au rendu complet.
                    if (donnees.recharger) {
                        window.location.reload();
                    } else if (donnees.html) {
                        remplacer(rangee, donnees.html);
                    }
                })
                .catch(function () {
                    form.submit(); // repli : POST classique (redirect + ancre)
                });
        });
    }

    function brancher(racine) {
        racine.querySelectorAll('form').forEach(intercepter);
    }

    document.querySelectorAll(SELECTEUR_FORMS).forEach(intercepter);
})(document);
