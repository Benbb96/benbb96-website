/* =============================================================================
   benbb96 — Helper HTTP vanilla (fetch + CSRF)
   =============================================================================
   Toutes les requêtes AJAX du site (a remplacé l'ancien jQuery $.ajax / $.ajaxSetup).

   API exposée sur window.http :
     - http.getCookie(name)            → valeur du cookie (ou null)
     - http.csrfToken()               → jeton CSRF courant
     - http.request(url, options)     → fetch() avec header X-CSRFToken auto
     - http.json(url, options)        → idem + parse la réponse JSON
   Usage :
     await http.json('/endpoint/', { method: 'POST', body: JSON.stringify(data) });
   ============================================================================ */
(function (window) {
    'use strict';

    var SAFE_METHODS = /^(GET|HEAD|OPTIONS|TRACE)$/i;

    function getCookie(name) {
        if (!document.cookie) return null;
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var c = cookies[i].trim();
            if (c.substring(0, name.length + 1) === name + '=') {
                return decodeURIComponent(c.substring(name.length + 1));
            }
        }
        return null;
    }

    function csrfToken() {
        return getCookie('csrftoken');
    }

    function request(url, options) {
        options = options || {};
        var method = (options.method || 'GET').toUpperCase();
        var headers = new Headers(options.headers || {});

        // Ajoute le header CSRF pour les méthodes non sûres (same-origin).
        if (!SAFE_METHODS.test(method)) {
            var token = csrfToken();
            if (token && !headers.has('X-CSRFToken')) {
                headers.set('X-CSRFToken', token);
            }
        }
        // Marqueur AJAX (compat avec d'éventuelles vues qui le testent).
        if (!headers.has('X-Requested-With')) {
            headers.set('X-Requested-With', 'XMLHttpRequest');
        }

        var config = Object.assign({ credentials: 'same-origin' }, options, { headers: headers });
        return fetch(url, config);
    }

    function json(url, options) {
        options = options || {};
        var headers = new Headers(options.headers || {});
        if (!headers.has('Accept')) headers.set('Accept', 'application/json');
        // Sérialise automatiquement un body objet (hors FormData).
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
            options = Object.assign({}, options, { body: JSON.stringify(options.body) });
        }
        options.headers = headers;
        return request(url, options).then(function (response) {
            if (!response.ok) {
                var err = new Error('HTTP ' + response.status);
                err.response = response;
                throw err;
            }
            return response.status === 204 ? null : response.json();
        });
    }

    window.http = {
        getCookie: getCookie,
        csrfToken: csrfToken,
        request: request,
        json: json
    };

    // ── Shim de compatibilité js-cookie ────────────────────────────────────
    // Remplace la lib externe js-cookie (CDN), souvent bloquée par les extensions
    // de confidentialité (script nommé « js.cookie »). Implémente l'API minimale
    // utilisée par le projet (window.Cookies.get/set/remove). Ne s'installe que
    // si une vraie lib n'est pas déjà présente.
    if (!window.Cookies) {
        window.Cookies = {
            get: function (name) {
                if (name === undefined) return null;
                var v = getCookie(name);
                return v === null ? undefined : v;
            },
            set: function (name, value, options) {
                options = options || {};
                var str = encodeURIComponent(name) + '=' + encodeURIComponent(value);
                if (options.expires) {
                    var d = options.expires;
                    if (typeof d === 'number') {
                        d = new Date();
                        d.setTime(d.getTime() + options.expires * 864e5);
                    }
                    str += '; expires=' + d.toUTCString();
                }
                str += '; path=' + (options.path || '/');
                document.cookie = str;
                return value;
            },
            remove: function (name, options) {
                options = options || {};
                document.cookie = encodeURIComponent(name) + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=' + (options.path || '/');
            }
        };
    }
})(window);
