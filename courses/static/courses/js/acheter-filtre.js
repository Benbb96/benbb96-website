/* Courses — filtre de « À acheter », côté client (cf. inventaire-filtre.js).
   Le DOM est réinterrogé à chaque passe : acheter-lignes.js remplace les rangées. */
(function (document) {
    'use strict';

    var conteneur = document.querySelector('[data-liste-acheter]');
    var champ = document.querySelector('[data-filtre-acheter]');
    var masquer = document.querySelector('[data-masquer-cochees]');
    var vider = document.querySelector('[data-vider-recherche]');
    if (!conteneur || !champ) return;

    var aucunResultat = conteneur.querySelector('[data-aucun-resultat]');

    // Même normalisation que _sans_accents() côté Python : « creme » trouve « Crème ».
    function normalise(texte) {
        return (texte || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }

    function correspondAuNom(ligne, recherche) {
        return ligne.dataset.recherche.indexOf(recherche) > -1;
    }

    function appliquer() {
        var recherche = normalise(champ.value);
        var masquerCochees = masquer && masquer.checked;
        var lignes = conteneur.querySelectorAll('[data-ligne-row]');
        var nbVisibles = 0;

        // Le nom prime sur le rayon : « creme » doit donner « Crème fraîche », pas toute
        // la Crèmerie. Le rayon n'élargit que si aucun nom d'article ne correspond.
        var parNom = !recherche || Array.prototype.some.call(lignes, function (l) {
            return correspondAuNom(l, recherche);
        });

        lignes.forEach(function (ligne) {
            var section = ligne.closest('[data-rayon-section]');
            var correspond =
                !recherche ||
                (parNom
                    ? correspondAuNom(ligne, recherche)
                    : section.dataset.recherche.indexOf(recherche) > -1);
            var visible = correspond && !(masquerCochees && ligne.dataset.cochee === '1');
            ligne.hidden = !visible;
            if (visible) nbVisibles += 1;
        });

        conteneur.querySelectorAll('[data-rayon-section]').forEach(function (section) {
            section.hidden = !Array.prototype.some.call(
                section.querySelectorAll('[data-ligne-row]'),
                function (ligne) { return !ligne.hidden; }
            );
        });

        if (aucunResultat) aucunResultat.hidden = nbVisibles !== 0;
        if (vider) vider.hidden = !champ.value;
    }

    champ.addEventListener('input', appliquer);
    if (masquer) masquer.addEventListener('change', appliquer);
    if (vider) {
        vider.addEventListener('click', function () {
            champ.value = '';
            champ.focus();
            appliquer();
        });
    }
    // Rangée substituée par acheter-lignes.js : rejouer le filtre sur le DOM neuf.
    document.addEventListener('courses:ligne-maj', appliquer);
    appliquer();
})(document);
