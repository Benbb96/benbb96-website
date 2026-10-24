/* Courses — filtre d'inventaire, entièrement côté client.
   ~200 articles par foyer : pas d'aller-retour serveur. Le texte cherché (nom +
   étiquettes sur la rangée, rayon sur la section) est précalculé côté Python.
   Sans JS, la liste complète reste affichée. */
(function (document) {
    'use strict';

    // Même normalisation que _sans_accents() côté Python : « creme » trouve « Crème ».
    function normalise(texte) {
        return (texte || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    }


    // Bouton « Créer cet article » : on y repasse la saisie pour ne pas la retaper.
    function majLienCreation(valeur) {
        var lien = document.querySelector('[data-creer-depuis-recherche]');
        if (!lien) return;
        if (!lien.dataset.base) lien.dataset.base = lien.getAttribute('href');
        lien.setAttribute(
            'href',
            lien.dataset.base + (valeur ? '?nom=' + encodeURIComponent(valeur) : '')
        );
    }

    function init(input) {
        var conteneur = document.querySelector('[data-inventaire]');
        if (!conteneur) return;
        var lignes = conteneur.querySelectorAll('[data-article-row]');
        var sections = conteneur.querySelectorAll('[data-rayon-section]');
        var aucunResultat = conteneur.querySelector('[data-aucun-resultat]');
        var vider = document.querySelector('[data-vider-recherche]');
        var nonOk = document.querySelector('[data-non-ok]');

        function correspondAuNom(ligne, recherche) {
            return ligne.dataset.recherche.indexOf(recherche) > -1;
        }

        function appliquer() {
            var recherche = normalise(input.value);
            var seulementManquants = nonOk && nonOk.checked;
            var nbVisibles = 0;

            // Le nom prime sur le rayon : « creme » doit donner « Crème fraîche », pas
            // toute la Crèmerie. Le rayon n'élargit que si aucun nom ne correspond.
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
                var visible =
                    correspond && !(seulementManquants && ligne.dataset.ok === '1');
                ligne.hidden = !visible;
                if (visible) nbVisibles += 1;
            });

            sections.forEach(function (section) {
                section.hidden = !Array.prototype.some.call(
                    section.querySelectorAll('[data-article-row]'),
                    function (ligne) { return !ligne.hidden; }
                );
            });

            if (aucunResultat) aucunResultat.hidden = nbVisibles !== 0;
            if (vider) vider.hidden = !input.value;
            majLienCreation(input.value.trim());
        }

        input.addEventListener('input', appliquer);
        if (nonOk) nonOk.addEventListener('change', appliquer);
        // Un stepper vient de changer le besoin : rejouer le filtre sur le nouvel état.
        document.addEventListener('courses:article-maj', appliquer);
        if (vider) {
            vider.addEventListener('click', function () {
                input.value = '';
                input.focus();
                appliquer();
            });
        }
        appliquer();
    }

    var input = document.querySelector('[data-filtre-inventaire]');
    if (input) init(input);
})(document);
