/* =============================================================================
   Courses — steppers et « Recompter » de l'Inventaire, sans rechargement de page.
   =============================================================================
   Sans ce script, ces formulaires font un POST classique (redirect + ancre
   #a-<id>) : ça marche, mais un aller-retour serveur par tape de +/- fait perdre
   la position de scroll et l'état d'ouverture des AUTRES articles — irritant sur
   une liste de ~200 lignes. Avec le script, la réponse JSON met juste à jour les
   quelques éléments concernés, sans repeindre la page. Retombe sur l'envoi natif
   du formulaire si la requête échoue (offline, erreur serveur).
   ============================================================================= */
(function (document) {
    'use strict';

    function majEtatArticle(details, donnees) {
        if (donnees.stock_cible !== undefined) {
            var formCible = details.querySelector('form[data-role="cible"]');
            if (formCible) {
                formCible.querySelector('.courses-stepper__val').textContent = donnees.stock_cible;
            }
        }
        if (donnees.ponctuel !== undefined) {
            var formPonctuel = details.querySelector('form[data-role="ponctuel"]');
            if (formPonctuel) {
                formPonctuel.querySelector('.courses-stepper__val').textContent = donnees.ponctuel;
            }
        }

        var badge = details.querySelector('[data-besoin-badge]');
        if (badge) {
            if (donnees.besoin) {
                badge.textContent = '× ' + donnees.besoin;
                badge.classList.add('ds-badge--primary');
            } else {
                badge.textContent = badge.dataset.okLabel;
                badge.classList.remove('ds-badge--primary');
            }
        }

        var jauge = details.querySelector('[data-jauge]');
        if (jauge) {
            jauge.style.width = donnees.pct + '%';
            jauge.classList.toggle('is-bas', donnees.pct < 34);
        }

        // Le libellé (« Stock estimé », traduit) est fourni par le template plutôt que
        // codé en dur ici, pour rester dans la langue active après une mise à jour AJAX.
        var stockEstime = details.querySelector('[data-stock-estime]');
        if (stockEstime) {
            stockEstime.textContent = stockEstime.dataset.stockEstimeLabel + ' : ' + donnees.stock_estime;
        }
    }

    function intercepter(form) {
        form.addEventListener('submit', function (event) {
            var details = form.closest('[data-article-row]');
            if (!details || typeof window.http === 'undefined') return; // dégradation native

            event.preventDefault();
            var corps = new FormData(form);
            if (event.submitter && event.submitter.name) {
                corps.set(event.submitter.name, event.submitter.value);
            }

            window.http
                .json(form.action, { method: 'POST', body: corps })
                .then(function (donnees) {
                    majEtatArticle(details, donnees);
                    if (form.dataset.role === 'recompter') {
                        form.reset();
                    }
                })
                .catch(function () {
                    form.submit(); // repli : comportement classique (redirect + ancre)
                });
        });
    }

    document.querySelectorAll(
        'form[data-role="cible"], form[data-role="ponctuel"], form[data-role="recompter"]'
    ).forEach(intercepter);
})(document);
