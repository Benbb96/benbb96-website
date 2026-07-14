# benbb96

[![Deploy to PythonAnywhere](https://github.com/Benbb96/benbb96-website/actions/workflows/deploy-to-pythonanywhere.yml/badge.svg)](https://github.com/Benbb96/benbb96-website/actions/workflows/deploy-to-pythonanywhere.yml)
![GitHub repo size](https://img.shields.io/github/repo-size/benbb96/benbb96-website)
![GitHub contributors](https://img.shields.io/github/contributors/benbb96/benbb96-website)
![issues](https://img.shields.io/github/issues/benbb96/benbb96-website)
![GitHub stars](https://img.shields.io/github/stars/benbb96/benbb96-website?style=social)
![GitHub forks](https://img.shields.io/github/forks/benbb96/benbb96-website?style=social)
![Twitter Follow](https://img.shields.io/twitter/follow/benbb96?style=social)

This is my very personal Django project where I want to put all of my ideas to make my life easier.

### Why is it public ?

I'm always open to remarks and suggestions in order to progress in Python and Django !

## Tech Stack
Benbb96/benbb96-website is built on the following main stack:

**Backend**
- <img width='25' height='25' src='https://img.stackshare.io/service/993/pUBY5pVj.png' alt='Python'/> [Python](https://www.python.org) – Language
- <img width='25' height='25' src='https://img.stackshare.io/service/994/4aGjtNQv.png' alt='Django'/> [Django](https://www.djangoproject.com/) 5.2 – Web framework (full stack)
- [Django REST Framework](https://www.django-rest-framework.org/) + [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) – REST API + JWT auth (mobile app & external Vue frontends)
- <img width='25' height='25' src='https://img.stackshare.io/service/2180/1284191.png' alt='Pandas'/> [Pandas](http://pandas.pydata.org/) (via [django-pandas](https://github.com/chrisdev/django-pandas)) – Time-series resampling (tracker)
- <img width='25' height='25' src='https://img.stackshare.io/service/2375/default_1f67b0ca7416a9f52beb655f90b5602d5ef74b75.jpg' alt='Pillow'/> [Pillow](https://python-pillow.github.io/) – On-upload image optimization (resize + WebP)

**Data & storage**
- [SQLite](https://www.sqlite.org/) – Database (development **and** production)
- [django-storages](https://django-storages.readthedocs.io/) + [Google Cloud Storage](https://cloud.google.com/storage) – Uploaded media (production)

**Front-end** (no build step, no front-end framework)
- <img width='25' height='25' src='https://img.stackshare.io/service/1209/javascript.jpeg' alt='JavaScript'/> [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) – Vanilla JS (`fetch` helper, no jQuery)
- Home-grown CSS design system (custom properties, flexbox/grid, `:has()`, `<dialog>`) — no CSS framework
- [Tom Select](https://tom-select.js.org/) – Enhanced select widgets (vanilla, no jQuery)
- [Chart.js](https://www.chartjs.org/) – Charts (tracker, kendama)
- [FontAwesome 6](https://fontawesome.com/) – Icons

**Tooling**
- <img width='25' height='25' src='https://img.stackshare.io/service/11563/actions.png' alt='GitHub Actions'/> [GitHub Actions](https://github.com/features/actions) – CI/CD (deploy to PythonAnywhere)

Full tech stack [here](/techstack.md)

## Installing benbb96

To install and use my website, follow these steps:

```
git clone https://github.com/Benbb96/benbb96-website.git
cd benbb96
```

Create a file here which will store all secrets settings : `secrets.json`.  
You can configure it like this :

```
{
  "SECRET_KEY": "[YOUR SECRET_KEY]",
  "GOOGLE_API_KEY": "[YOUR GOOGLE_API_KEY]",
  "GOOGLE_ANALYTICS_KEY": "[YOUR GOOGLE_ANALYTICS_KEY]",
  "EMAIL_HOST_USER": "[YOUR EMAIL_HOST_USER]",
  "EMAIL_HOST_PASSWORD": "[YOUR EMAIL_HOST_PASSWORD]"
}
```

> In **development**, uploaded images are stored locally (`FileSystemStorage` / `MEDIA_ROOT`),
> so no extra configuration is needed.

### Media storage (Google Cloud Storage)

Uploaded images (avatars, project/game pictures, reviews, tasks, kendamas…) are served from a
**Google Cloud Storage** bucket via [`django-storages`](https://django-storages.readthedocs.io/).
The GCS backend is enabled **only in production** (`config/settings/prod.py` → `STORAGES`).

To enable it, add the **service account** credentials to `secrets.json` under `GCS_CREDENTIALS`
(the full JSON key downloaded from Google Cloud → IAM → Service Accounts, with at least the *Storage Object Admin* role on the bucket):

```
{
  ...
  "GCS_CREDENTIALS": { ...service account JSON... }
}
```

The bucket name and options live in `config/settings/prod.py`
(`GS_BUCKET_NAME`, `GS_LOCATION = 'media'`, `GS_DEFAULT_ACL = 'publicRead'`), next to the `STORAGES`
setting that enables the GCS backend. Bucket objects must be publicly readable (grant `allUsers` the
*Storage Object Viewer* role on the bucket).

Images are optimized on upload (resized to 1280 px max + WebP) by `base.image_utils`. Two
management commands help maintain the bucket:
`optimize_existing_photos` (batch resize/WebP of existing images) and `clean_orphan_media`
(remove files no longer referenced in the database — dry-run by default, `--apply` to delete).

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (single source of truth:
`pyproject.toml` + `uv.lock`; Python version in `.python-version`). Install uv, then let it build
the virtual environment (`.venv`), load the migrations to build the database (`db.sqlite3`), create a
superuser to access the administration module, and finally run the server:

```
# install uv (once): https://docs.astral.sh/uv/getting-started/installation/
uv sync                       # creates .venv from uv.lock (prod + dev deps)
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py collectstatic --noinput
uv run manage.py runserver
```

`uv sync` installs the dev group too (django-debug-toolbar, coverage, ruff, pre-commit, pyright,
djlint); add `--no-dev` for a production-only environment. `uv run <cmd>` runs a command inside the
environment without activating it. To add or bump a dependency, edit `pyproject.toml` then run
`uv lock` (and commit the updated `uv.lock`).

You can then create projects in [127.0.0.1:8000/admin/base/projet/](http://127.0.0.1:8000/admin/base/projet/) that will be displayed on the homepage.

## Contact 

If you want to contact me you can reach me at <benbb96@gmail.com>.

## License 

This project uses the following license: [MIT License](LICENSE).
