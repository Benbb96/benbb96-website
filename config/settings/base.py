import json
import os
import soundcloud
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

with open(os.path.join(BASE_DIR, 'secrets.json')) as f:
    secrets = json.loads(f.read())


def get_secret_setting(setting, json_conf=secrets):
    try:
        val = json_conf[setting]
        if val == 'True':
            val = True
        elif val == 'False':
            val = False
        return val
    except KeyError:
        raise ImproperlyConfigured("Set the {} setting".format(setting))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'avis.apps.AvisConfig',
    'base.apps.BaseConfig',
    'tracker.apps.TrackerConfig',
    'versus.apps.VersusConfig',
    'music.apps.MusicConfig',
    'my_spot.apps.MySpotConfig',
    'super_moite_moite.apps.SuperMoiteMoiteConfig',
    'kendama.apps.KendamaConfig',
    'bootstrap3',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'geoposition',
    'fontawesome_6',
    'django_filters',
    'colorfield',
    'adminsortable',
    'django_select2',
    'simple_history',
    'anymail',
    'corsheaders'
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'base.ajax_middleware.AjaxMiddleware', 
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://www.benbb96.com",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "https://vue-trackers.onrender.com"
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'base.context_processors.base_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'fr'

LANGUAGES = [
  ('fr', _('French')),
  ('en', _('English')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

# default static files settings for PythonAnywhere.
# see https://help.pythonanywhere.com/pages/DjangoStaticFiles for more info
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets')
]

GOOGLE_ANALYTICS_KEY = ''

GOOGLE_API_KEY = get_secret_setting('GOOGLE_API_KEY')
GEOPOSITION_GOOGLE_MAPS_API_KEY = GOOGLE_API_KEY

FIREBASE_CONFIG = get_secret_setting('FIREBASE_CONFIG')

SOUNDCLOUD_CLIENT = soundcloud.Client(client_id=get_secret_setting('SOUNDCLOUD_CLIENT_ID'))

SPOTIFY_CLIENT_ID = get_secret_setting('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = get_secret_setting('SPOTIFY_CLIENT_SECRET')
auth_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
SPOTIFY = spotipy.Spotify(auth_manager=auth_manager)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Allow to stay connected one week on the mobile app
    'ROTATE_REFRESH_TOKENS': True
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'test_mails')

ADMINS = [('Benbb96', 'benbb96@gmail.com')]
EMAIL_SUBJECT_PREFIX = '[Benbb96] '
DEFAULT_FROM_EMAIL = 'webmaster@benbb96.com'
SERVER_EMAIL = 'benbb96@benbb96.com'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 1500
