# 08 — Déploiement sur uv (PythonAnywhere)

> Rédigé en Phase 9. Décrit la **nouvelle** procédure de déploiement après la bascule de
> `requirements/*.txt` (pip) vers `pyproject.toml` + `uv.lock` (uv). Source de vérité des
> dépendances : **`pyproject.toml` + `uv.lock`** (voir aussi `README.md`).

## Principe

- Déclencheur inchangé : un `push` sur `master` lance
  `.github/workflows/deploy-to-pythonanywhere.yml` (SSH via `appleboy/ssh-action`).
- On installe les dépendances **dans le virtualenv existant** de PythonAnywhere
  (`~/.virtualenvs/benbb96`), celui que pointe le **Web tab** de PA. Le Web tab n'est **pas** modifié.
- `uv sync --frozen --no-dev` installe **exactement** ce que décrit `uv.lock` (reproductible),
  **sans** les dépendances du groupe `dev`.

Variables d'environnement utilisées côté PA :

| Variable | Rôle |
|---|---|
| `UV_PROJECT_ENVIRONMENT=$HOME/.virtualenvs/benbb96` | cible le venv existant du Web tab au lieu de créer `.venv` |
| `UV_PYTHON_PREFERENCE=only-system` | réutilise le Python 3.13 de PA, **interdit** tout téléchargement de Python par uv |

`--frozen` : n'essaie pas de re-résoudre ni de mettre à jour `uv.lock` (échoue si le lock est
désynchronisé du `pyproject.toml` — c'est voulu). `--no-dev` : exclut le groupe `dev`
(django-debug-toolbar, coverage, ruff, pre-commit, pyright, djlint).

## Séquence exécutée par le workflow

```bash
set -e
cd "$HOME/benbb96-website"
git pull
export UV_PROJECT_ENVIRONMENT="$HOME/.virtualenvs/benbb96"
export UV_PYTHON_PREFERENCE=only-system
"$HOME/.local/bin/uv" sync --frozen --no-dev
"$UV_PROJECT_ENVIRONMENT/bin/python" manage.py migrate
"$UV_PROJECT_ENVIRONMENT/bin/python" manage.py collectstatic --noinput
touch /var/www/www_benbb96_com_wsgi.py
```

> ⚠️ Adapter `$HOME/.local/bin/uv` si l'installateur a placé le binaire ailleurs
> (vérifier avec `which uv` / `command -v uv` en SSH).

## ⚠️ PRÉREQUIS PROD — actions MANUELLES à faire AVANT de merger sur `master`

Ces étapes ne peuvent pas être exécutées par un agent (pas d'accès prod). **Le propriétaire doit les
faire à la main en SSH sur PythonAnywhere**, et ne merger sur `master` **qu'une fois le test OK**.

1. **Installer uv sur PythonAnywhere** (accès réseau sortant requis — OK sur les offres payantes PA) :
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv --version          # vérifier l'installation (binaire attendu : ~/.local/bin/uv)
   command -v uv         # confirmer le chemin ; adapter le workflow si différent
   ```

2. **Tester la séquence de déploiement à la main** (une fois, avant tout déploiement auto) :
   ```bash
   cd "$HOME/benbb96-website"
   git pull
   export UV_PROJECT_ENVIRONMENT="$HOME/.virtualenvs/benbb96"
   export UV_PYTHON_PREFERENCE=only-system
   ~/.local/bin/uv sync --frozen --no-dev
   "$UV_PROJECT_ENVIRONMENT/bin/python" manage.py migrate
   "$UV_PROJECT_ENVIRONMENT/bin/python" manage.py collectstatic --noinput
   touch /var/www/www_benbb96_com_wsgi.py
   ```
   Puis **recharger le Web tab** et vérifier que le site tourne (pages publiques + admin), qu'il
   n'y a pas d'erreur dans le log d'erreurs PA, et que les deux deps git forkées sont bien installées :
   ```bash
   "$UV_PROJECT_ENVIRONMENT/bin/python" -c "import adminsortable, soundcloud; print('forks OK')"
   ```

3. **Seulement une fois ce test OK → merger sur `master`.** Le déploiement automatique utilisera uv.

## Filet de secours (si installer uv sur PA pose problème)

`uv.lock` reste la source de vérité, mais on peut **générer** un `requirements.txt` figé (avec
hashes) et retomber sur pip côté serveur, sans réintroduire de fichier requirements versionné :

```bash
# en local ou en CI, à partir de pyproject.toml + uv.lock :
uv export --no-dev --format requirements-txt -o requirements.txt
# puis, côté PA :
"$HOME/.virtualenvs/benbb96/bin/python" -m pip install -r requirements.txt
```

À n'utiliser que comme repli documenté : le chemin nominal reste `uv sync --frozen --no-dev`.

## Notes

- Le local est aligné sur la prod : `.python-version = 3.13`. `uv sync` (sans `--no-dev`) recrée un
  `.venv` local en Python 3.13 (téléchargé/géré par uv si absent du système) avec les deps dev.
- Migrations & i18n : `collectstatic` est déjà dans le workflow ; si la Phase 8 (i18n) ajoute des
  `.mo` (re)générés au déploiement, ajouter `manage.py compilemessages` **avant** le `touch` du WSGI.
