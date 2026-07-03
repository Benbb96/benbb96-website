/* Amélioration progressive du menu mobile (.ds-nav).
   Le menu fonctionne sans JS via le « checkbox-hack » (#ds-nav-toggle) ; ce
   script ajoute l'accessibilité que la case cachée ne peut pas fournir :
   - synchronise aria-expanded du burger avec l'état ouvert/fermé ;
   - rend le burger opérable au clavier (Entrée / Espace), la case étant hidden. */
(function () {
    var toggle = document.getElementById('ds-nav-toggle');
    var burger = document.querySelector('.ds-nav__burger');
    if (!toggle || !burger) return;

    function sync() {
        burger.setAttribute('aria-expanded', toggle.checked ? 'true' : 'false');
    }

    toggle.addEventListener('change', sync);

    burger.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ' || event.key === 'Spacebar') {
            event.preventDefault();
            toggle.checked = !toggle.checked;
            sync();
        }
    });

    sync();
})();
