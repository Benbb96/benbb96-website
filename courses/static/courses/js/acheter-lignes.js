/* =============================================================================
   Courses — actions de « À acheter » sans rechargement de page.
   =============================================================================
   Même motif que inventaire-steppers.js, mais la mise à jour est structurelle
   plutôt que champ par champ : cocher un article fait apparaître le champ
   quantité et le bouton « Pas trouvé ». Le serveur renvoie donc la rangée
   re-rendue, qu'on substitue en place — pas de balisage dupliqué ici.

   Sans ce script, chaque coche fait un POST + redirect : ça marche (le serveur
   pose une ancre #ligne-<id>), mais on repart en haut de page à chaque tape,
   irritant en plein magasin sur une liste de plusieurs écrans.
   ============================================================================= */
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
