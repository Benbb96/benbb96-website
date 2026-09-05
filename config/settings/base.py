import json
import os
from datetime import timedelta
from typing import Any

import soundcloud
import spotipy
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from spotipy.oauth2 import SpotifyClientCredentials

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

with open(os.path.join(BASE_DIR, "secrets.json")) as f:
    secrets = json.loads(f.read())


# Sentinelle : distingue « pas de défaut » de « défaut à None/"" ».
_REQUIRED = object()


def get_secret_setting(setting, json_conf=secrets, default=_REQUIRED) -> Any:
    """Lit un secret de `secrets.json`. Un `default` le rend optionnel."""
    try:
        val = json_conf[setting]
    except KeyError:
        if default is not _REQUIRED:
            return default
        raise ImproperlyConfigured(f"Set the {setting} setting") from None
    if val == "True":
        val = True
    elif val == "False":
        val = False
    return val


# Application definition

INSTALLED_APPS = [
    "storages",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "avis.apps.AvisConfig",
    "base.apps.BaseConfig",
    "tracker.apps.TrackerConfig",
    "versus.apps.VersusConfig",
    "music.apps.MusicConfig",
    "my_spot.apps.MySpotConfig",
    "super_moite_moite.apps.SuperMoiteMoiteConfig",
    "kendama.apps.KendamaConfig",
    "courses.apps.CoursesConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "geoposition",
    "fontawesome_6",
    "django_filters",
    "colorfield",
    "adminsortable",
    "simple_history",
    "anymail",
    "corsheaders",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Sert /static/ depuis l'app avec les bons en-têtes de cache : le nginx de
    # PythonAnywhere n'envoie aucun Cache-Control. Doit rester juste après
    # SecurityMiddleware. Inerte en dev, où runserver sert les statiques.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "base.ajax_middleware.AjaxMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ALLOWED_ORIGINS = [
    "https://www.benbb96.com",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "https://vue-trackers.onrender.com",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "base.context_processors.base_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "fr"

LANGUAGES = [
    ("fr", _("French")),
    ("en", _("English")),
]

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# default static files settings for PythonAnywhere.
# see https://help.pythonanywhere.com/pages/DjangoStaticFiles for more info
MEDIA_URL = "/media/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

GOOGLE_ANALYTICS_KEY = ""

GOOGLE_API_KEY = get_secret_setting("GOOGLE_API_KEY")
GEOPOSITION_GOOGLE_MAPS_API_KEY = GOOGLE_API_KEY

SOUNDCLOUD_CLIENT = soundcloud.Client(
    client_id=get_secret_setting("SOUNDCLOUD_CLIENT_ID")
)

SPOTIFY_CLIENT_ID = get_secret_setting("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_secret_setting("SPOTIFY_CLIENT_SECRET")
auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
)
SPOTIFY = spotipy.Spotify(auth_manager=auth_manager)

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
}

SIMPLE_JWT = {
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=7
    ),  # Allow to stay connected one week on the mobile app
    "ROTATE_REFRESH_TOKENS": True,
}

# Framework MAILERS (Django 6+) : remplace les réglages EMAIL_* dépréciés
# (RemovedInDjango70). En dev, on écrit les mails dans des fichiers.
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.filebased.EmailBackend",
        "OPTIONS": {"file_path": os.path.join(BASE_DIR, "test_mails")},
    },
}

# Le format (nom, e-mail) est déprécié (RemovedInDjango70Warning).
ADMINS = ["benbb96@gmail.com"]

# Contact publié sur les pages légales (droits RGPD) : dérivé d'ADMINS pour
# n'avoir qu'un seul endroit à modifier.
CONTACT_EMAIL = ADMINS[0]
EMAIL_SUBJECT_PREFIX = "[Benbb96] "
DEFAULT_FROM_EMAIL = "webmaster@benbb96.com"
SERVER_EMAIL = "benbb96@benbb96.com"

# `DEFAULT_LOGGING` de Django, au handler `mail_admins` près (cf. config/log.py).
# À recopier en entier : Django ne fusionne pas, il enchaîne deux `dictConfig()`.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "config.log.SafeAdminEmailHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "mail_admins"], "level": "INFO"},
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1500
