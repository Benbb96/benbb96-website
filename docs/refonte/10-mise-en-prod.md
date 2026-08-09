# 10 — Première mise en prod de la refonte (+ renommage `master` → `main`)

> Checklist du **premier déploiement** de toute la refonte (Phases 1→9 + passe design), qui bascule
> aussi la branche principale `master` → `main`. Cocher au fur et à mesure.

## Contexte

- Tout le travail est sur la branche `refonte` (jamais déployé). `origin/master` ne contenait que
  3 bumps Dependabot (django 5.2.15, pillow 12.3.0, setuptools 83.0.0) visant `requirements/*.txt`
  (supprimés en Phase 9) → **réconciliés** dans `pyproject.toml` + `uv.lock` (merge de `origin/master`
  dans `refonte`).
- Déploiement = `push` sur la branche par défaut → GitHub Actions SSH → `uv sync` (voir
  [08-deploiement-uv.md](08-deploiement-uv.md)). uv est **déjà installé** sur PythonAnywhere.
- Le renommage force : trigger workflow `main`, re-tracking du clone PA, refs docs → **déjà faits**
  côté repo (workflow deploy + codeql + docs). Reste le côté GitHub + local + PA.

## Étapes

### En local (préparation) — FAIT
- [x] Réconcilier `origin/master` dans `refonte` (bumps → `pyproject.toml`/`uv.lock`).
- [x] Trigger deploy `master`→`main` (+ codeql) ; refs `master`→`main` dans docs/CLAUDE.md.
- [x] Valider : `uv sync`, `check`, `makemigrations --check`, 27 smoke tests.
- [ ] Pousser `refonte` sur origin.

### Sur GitHub
- [ ] **Renommer la branche** `master` → `main` :
      `gh api -X POST repos/Benbb96/benbb96-website/branches/master/rename -f new_name=main`
      (bascule le défaut sur `main`, retargette les PR, crée des redirections).
- [ ] **Ouvrir la PR** `refonte` → `main` (merge commit — **garder les commits**, pas de squash).
      NE PAS merger tout de suite.

### En local (après renommage)
- [ ] `git branch -m master main` ; `git fetch origin` ; `git branch -u origin/main main`
      ; `git remote set-head origin -a`.

### Sur PythonAnywhere (SSH) — validation AVANT merge
- [ ] Backup : copier `db.sqlite3`.
- [ ] Re-pointer le clone sur `main` : `git fetch origin` puis `git checkout -B main origin/main`.
- [ ] **Tester la séquence uv contre `refonte`** :
      ```bash
      cd ~/benbb96-website
      git fetch origin refonte && git checkout refonte
      export UV_PROJECT_ENVIRONMENT="$HOME/.virtualenvs/benbb96"
      export UV_PYTHON_PREFERENCE=only-system
      ~/.local/bin/uv sync --frozen --no-dev
      "$UV_PROJECT_ENVIRONMENT/bin/python" manage.py migrate
      "$UV_PROJECT_ENVIRONMENT/bin/python" manage.py collectstatic --noinput
      touch /var/www/www_benbb96_com_wsgi.py
      ```
- [ ] Recharger le Web tab. Vérifier : pages publiques, **admin**, **kendama**, **toggle dark mode**,
      images (GCS), pas d'erreur dans le log PA. Forks OK :
      `"$UV_PROJECT_ENVIRONMENT/bin/python" -c "import adminsortable, soundcloud; print('forks OK')"`.
- [ ] `showmigrations` : confirmer que tout est appliqué.

### Go-live
- [ ] **Merger la PR** (merge commit) → push sur `main` → auto-déploiement (trigger `main`, séquence
      uv). Surveiller le run GitHub Actions.
- [ ] Vérif post-déploiement (site OK, dark mode, images, admin, kendama).

### Après (non bloquant)
- [ ] Reconfigurer **Dependabot** pour cibler `pyproject.toml`/`uv.lock` (sinon PR sur des
      `requirements/*.txt` inexistants).
- [ ] Sur PA, supprimer l'ancienne branche locale `master` si elle traîne.
- [ ] Envisager la suppression du backup bucket `backups/2026-05-30/` une fois tout stable.

## Rollback (si le déploiement casse)

- Le site tourne tant que le WSGI n'est pas rechargé sur du code cassé. En cas de souci :
  `git checkout <commit-précédent>` sur PA + `uv sync` (ou repli pip via `uv export`, cf. doc 08) +
  `touch wsgi`. La base a été sauvegardée avant le `migrate`.
</content>
