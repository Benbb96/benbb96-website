/* =============================================================================
   benbb96 — Initialisation Tom Select (vanilla, sans jQuery)
   =============================================================================
   Remplace django-select2 / select2 (qui dépendait de jQuery). Initialise tous
   les <select class="js-tomselect"> de la page. Deux modes, pilotés par data-* :

     - jeu de données rendu côté serveur (toutes les <option>) → filtrage client ;
     - data-ts-url="/endpoint/" → chargement distant : Tom Select interroge
       l'endpoint JSON (?q=…) qui renvoie [{id, text}, …] (via window.http).

   data-* lus :
     data-placeholder   texte d'invite
     data-ts-url        URL de recherche JSON (active le mode distant)
     data-min-input     longueur min. de saisie avant recherche (0 = précharge)
     data-create-url    POST {nom: saisie} -> {id, nom} : crée l'option à la volée
   ============================================================================ */
(function (window, document) {
    'use strict';

    function buildOptions(el) {
        var isMultiple = el.multiple;
        var minInput = parseInt(el.dataset.minInput, 10);
        if (isNaN(minInput)) minInput = el.dataset.tsUrl ? 1 : 0;

        var options = {
            plugins: isMultiple ? ['remove_button'] : [],
            placeholder: el.dataset.placeholder || el.getAttribute('placeholder') || '',
            allowEmptyOption: true,
            maxOptions: null,
            // Conserve l'ordre du serveur plutôt qu'un tri alphabétique imposé.
            sortField: { field: '$order' }
        };

        var url = el.dataset.tsUrl;
        if (url) {
            // Mode distant : on ne rend que les options sélectionnées côté serveur,
            // le reste est chargé à la frappe via l'endpoint JSON.
            options.valueField = 'id';
            options.labelField = 'text';
            options.searchField = 'text';
            options.shouldLoad = function (query) { return query.length >= minInput; };
            options.preload = minInput === 0 ? 'focus' : false;
            options.load = function (query, callback) {
                var sep = url.indexOf('?') > -1 ? '&' : '?';
                window.http.json(url + sep + 'q=' + encodeURIComponent(query))
                    .then(function (data) {
                        callback(Array.isArray(data) ? data : (data.results || []));
                    })
                    .catch(function () { callback(); });
            };
        }

        var createUrl = el.dataset.createUrl;
        if (createUrl) {
            options.create = function (input, callback) {
                window.http.json(createUrl, { method: 'POST', body: { nom: input } })
                    .then(function (data) { callback({ value: String(data.id), text: data.nom }); })
                    .catch(function () { callback(); });
            };
            options.createOnBlur = true;
        }
        return options;
    }

    function init(el) {
        if (el.tomselect) return;
        new TomSelect(el, buildOptions(el));
    }

    function initAll(root) {
        if (typeof TomSelect === 'undefined') return;
        (root || document).querySelectorAll('select.js-tomselect').forEach(init);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { initAll(); });
    } else {
        initAll();
    }

    // Exposé pour ré-initialiser après ajout dynamique (formsets versus).
    window.tomSelectInit = initAll;
})(window, document);
