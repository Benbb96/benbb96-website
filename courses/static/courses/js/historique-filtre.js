/* Courses — filtre de l'Historique, côté client (cf. inventaire-filtre.js).
   Texte, magasin et mois se cumulent ; un mois sans sortie visible se replie. */
(function (document) {
    'use strict';

    var conteneur = document.querySelector('[data-historique]');
    var champ = document.querySelector('[data-filtre-historique]');
    if (!conteneur || !champ) return;

    var magasin = document.querySelector('[data-filtre-magasin]');
    var mois = document.querySelector('[data-filtre-mois]');
    var vider = document.querySelector('[data-vider-recherche]');
    var aucunResultat = conteneur.querySelector('[data-aucun-resultat]');

    // Même normalisation que _sans_accents() côté Python : « creme » trouve « Crème ».
    function normalise(texte) {
        return (texte || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }

    function appliquer() {
        var recherche = normalise(champ.value);
        var cleMagasin = magasin ? magasin.value : '';
        var cleMois = mois ? mois.value : '';
        var nbVisibles = 0;

        conteneur.querySelectorAll('[data-sortie-row]').forEach(function (ligne) {
            var visible =
                (!recherche || ligne.dataset.recherche.indexOf(recherche) > -1) &&
                (!cleMagasin || ligne.dataset.magasin === cleMagasin) &&
                (!cleMois || ligne.dataset.mois === cleMois);
            ligne.hidden = !visible;
            if (visible) nbVisibles += 1;
        });

        conteneur.querySelectorAll('[data-mois-section]').forEach(function (section) {
            section.hidden = !Array.prototype.some.call(
                section.querySelectorAll('[data-sortie-row]'),
                function (ligne) { return !ligne.hidden; }
            );
        });

        if (aucunResultat) aucunResultat.hidden = nbVisibles !== 0;
        if (vider) vider.hidden = !champ.value;
    }

    champ.addEventListener('input', appliquer);
    if (magasin) magasin.addEventListener('change', appliquer);
    if (mois) mois.addEventListener('change', appliquer);
    if (vider) {
        vider.addEventListener('click', function () {
            champ.value = '';
            champ.focus();
            appliquer();
        });
    }
    appliquer();
})(document);
