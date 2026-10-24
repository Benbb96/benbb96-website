/* Courses — focus automatique du champ de recherche.
   Écarté sur écran tactile : le clavier virtuel s'ouvrirait à l'arrivée et masquerait
   la moitié de la liste, alors qu'en magasin on vient d'abord lire, pas chercher. */
(function (document, window) {
    'use strict';

    var champ = document.querySelector('[data-autofocus]');
    if (!champ) return;
    if (!window.matchMedia || !window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    // `preventScroll` : focaliser ne doit pas faire sauter la page sous la barre collante.
    champ.focus({ preventScroll: true });
})(document, window);
