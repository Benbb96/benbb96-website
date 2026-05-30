# 05 — Roadmap phasée

Ordre d'exécution conseillé, pensé pour livrer par incréments **déployables** et limiter les risques.
Chaque phase peut être confiée à un agent distinct avec le document de chantier correspondant.

## Phase 0 — Filet de sécurité (recommandé avant tout)

- Sauvegarder `db.sqlite3` et les images (export Firebase) avant toute migration.
- Ajouter quelques **tests de smoke** (status 200 des vues clés, non-régression des endpoints API
  tracker & smm). Sécurise toutes les phases suivantes.
- Vérifier l'environnement : `python manage.py check`, `makemigrations --check --dry-run`.

## Phase 1 — Nettoyage sec des dépendances (doc 4)

- Retirer `django-avatar`, `django-redis`. (`redis` finalement conservé : dépendance transitive
  obligatoire de `spotipy` — voir doc 4.)
- Mettre à jour `google-api-python-client` (1.12.11 → 2.x) et tester le fetch YouTube (music).
- **Faible risque, gain immédiat.** Déployable seul.

## Phase 2 — Modernisation du stockage d'images (doc 3)

> Indépendant du chantier front. Peut tourner en parallèle de la Phase 3.

**Décision actée** : on garde le bucket **Firebase = GCS** existant, mais via `django-storages`
(backend `GoogleCloudStorage`) + `ImageField` standard + optimisation **Pillow** (resize + WebP) à la
sauvegarde. Gratuit, images existantes en place, disque PythonAnywhere plus jamais sollicité.

1. Ajouter/config `django-storages[google]` + credentials compte de service GCS (dans `secrets.json`).
2. `PhotoAbstract` : `ImageField` sur storage GCS + `photo_url` rétrocompatible + optimisation Pillow.
3. Remplacer `FirebaseUploadWidget` par un upload serveur standard dans les 4 `forms.py`.
4. Adapter les templates d'affichage des photos (retrait du JS Firebase).
5. Management command de **normalisation** des chemins (les fichiers ne bougent pas du bucket), testée
   sur copie de prod.
6. Déployer code → normaliser en prod → vérifier → retirer Pyrebase4 + SDK Firebase JS + config exposée.

## Phase 3 — Front : design system + layout global (doc 2) — ✅ FAITE

1. ✅ Design system CSS maison (`assets/css/main.css` : tokens, reset, base, layout, composants `.ds-*`).
2. ✅ Chrome global réécrit : `base.html`, `navbar.html`, `footer.html` (menu mobile sans JS, footer
   social `.ds-social`).
3. ✅ Composants `components/form.html` (prêt, branché en Phase 4), messages Django en `.ds-alert`
   (`components/messages.html`), `components/pagination.html` restylé `.ds-pagination`.
4. ✅ Helper `fetch` + CSRF (`assets/js/http.js`, `window.http`). Le `$.ajaxSetup` jQuery est
   **conservé** pour music/tracker jusqu'à leur migration (Phase 4) ; retiré ensuite.

**Stratégie de coexistence retenue** (détail en doc 2) : namespace `ds-` pour tous les composants
maison (aucune classe Bootstrap redéfinie) ; `main.css` chargé en dernier (les sélecteurs d'éléments
modernisent le rendu « nu », les classes Bootstrap gardent la priorité sur les pages d'app) ; JS
ajouté sans rien retirer. Validé : `check` OK, `makemigrations --check` sans changement, 27 smoke
tests OK, pages home/profil/login/signup/listes d'app servies en 200 avec Bootstrap encore actif.

> ⚠️ **Bootstrap et jQuery restent chargés** pendant toute la transition (Phases 3 → 4). Les
> templates des apps utilisent encore les classes Bootstrap : les retirer maintenant casserait
> toutes les pages non migrées. Leur **retrait définitif se fait en Phase 5**, une fois la Phase 4
> terminée. Le design system de la Phase 3 doit donc **coexister** avec Bootstrap (éviter de
> redéfinir de façon destructive les classes Bootstrap encore utilisées : `.btn`, `.row`, `.col-*`,
> `.container`, `.panel`, `.alert`… — préférer des sélecteurs d'éléments + de nouvelles classes, ou
> un préfixe). Le site doit rester **fonctionnel et déployable** après la Phase 3.

## Phase 4 — Migration des templates app par app (doc 2)

Ordre conseillé (du plus simple/visible au plus complexe) :

1. `registration/` (login, signup) + `base` (home, profils, about, gallery, rallye).
2. `avis`, `versus`.
3. `music` (beaucoup de templates + AJAX `.platformLink` à passer en fetch).
4. `tracker` (Chart.js + AJAX `common.js` + éventuel moment.js à remplacer).
5. `super_moite_moite` (attention au composant Vue.js embarqué — ne styler que l'enveloppe).
6. `my_spot` : **conservé, effort minimal** (décision actée). Migration cosmétique a minima pour que
   les pages restent lisibles + **corriger `request.is_ajax()`** (déprécié, cassé depuis Django 4.1 :
   remplacer par `request.headers.get('x-requested-with') == 'XMLHttpRequest'`). Pas d'effort de
   modernisation poussé.
7. `kendama` : **uniquement** retirer `{% bootstrap_form %}` des templates de formulaire (doc 6).
   Ne rien changer d'autre.

## Phase 5 — Suppression de Bootstrap & jQuery (doc 2)

- Une fois **tous** les `{% bootstrap_* %}` éliminés (apps + kendama) :
  retirer `django-bootstrap3` de `INSTALLED_APPS` + requirements, supprimer le CDN Bootstrap,
  `bootstrap-social.css`, et le jQuery global.
- **Supprimer `moment-with-locales.js` (541 Ko) + `bootstrap-daterangepicker`** : remplacés par
  `Intl.DateTimeFormat` / `Intl.RelativeTimeFormat` / `Date` natifs (fait en Phase 4 sur tracker &
  super_moite_moite). Monter **Chart.js → v4**. Pas de Temporal (non fiable en natif début 2026).

## Phase 6 — Finitions

- Évaluer `soundcloud` (fork git, API dépréciée) → garder ou retirer (doc 4).
- Mettre à jour `README.md` et régénérer/supprimer `techstack.md`/`techstack.yml` (obsolètes :
  mentionnent encore Bootstrap, Redis, etc.).
- Revue d'accessibilité / Lighthouse / poids des pages.
- Nettoyer le code mort éventuel des apps abandonnées.

## Dépendances entre phases

```
Phase 0 (filet) ─┬─> Phase 1 (deps sèches)            [indépendant]
                 ├─> Phase 2 (images/Firebase)        [indépendant du front]
                 └─> Phase 3 (design system) ─> Phase 4 (templates apps) ─> Phase 5 (suppr. Bootstrap)
                                                                                      │
                                                          Phase 6 (finitions) <───────┘
```

Les phases 1 et 2 peuvent avancer en parallèle du front (3→4→5). La Phase 5 ne peut se faire
qu'après la fin de la Phase 4 (kendama forms inclus).

## Rappels opérationnels

- Déploiement : push sur `master` déclenche le déploiement PythonAnywhere. Travailler sur la
  branche `refonte`, fusionner par incréments testés.
- Pas de trailer `Co-Authored-By` dans les commits ; ne pas utiliser le skill `/commit`.
- Vérifier `makemigrations --check` et `python manage.py check` à chaque phase.
- **Rejouer la suite de tests de smoke (27 tests, livrés en Phase 0) après chaque phase**, en
  particulier les phases front 3→5 et la Phase 2 (non-régression des endpoints API tracker & smm).
- Filet de sécurité Phase 0 en place : backup DB OK + backup bucket dans
  `~/backups/bucket-refonte-2026-05-29/media/` (325 fichiers, ~827 Mo).
</content>
