/* =============================================================================
   Courses — filtre d'inventaire, entièrement côté client.
   =============================================================================
   ~200 articles maximum par foyer (conception.md) : pas besoin d'aller-retour
   serveur. Le texte de recherche (nom + rayon + étiquettes) est précalculé côté
   Python dans data-recherche, en minuscules — on se contente ici d'un indexOf.
   Un article sans JS reste simplement non filtrable : la liste complète (avec
   ses sections par rayon) s'affiche quand même.
   ============================================================================= */
(function (document) {
    'use strict';

    function normalise(texte) {
        return (texte || '').toLowerCase();
    }

    function init(input) {
        var conteneur = document.querySelector('[data-inventaire]');
        if (!conteneur) return;
        var lignes = conteneur.querySelectorAll('[data-article-row]');
        var sections = conteneur.querySelectorAll('[data-rayon-section]');
        var aucunResultat = conteneur.querySelector('[data-aucun-resultat]');

        function appliquer() {
            var recherche = normalise(input.value);
            var nbVisibles = 0;

            lignes.forEach(function (ligne) {
                var visible = !recherche || ligne.dataset.recherche.indexOf(recherche) > -1;
                ligne.hidden = !visible;
                if (visible) nbVisibles += 1;
            });

            sections.forEach(function (section) {
                var uneLigneVisible = Array.prototype.some.call(
                    section.querySelectorAll('[data-article-row]'),
                    function (ligne) { return !ligne.hidden; }
                );
                section.hidden = !uneLigneVisible;
            });

            if (aucunResultat) aucunResultat.hidden = nbVisibles !== 0;
        }

        input.addEventListener('input', appliquer);
        appliquer();
    }

    var input = document.querySelector('[data-filtre-inventaire]');
    if (input) init(input);
})(document);
