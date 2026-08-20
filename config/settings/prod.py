from .base import *

SECRET_KEY = get_secret_setting("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = [".benbb96.com"]

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': get_secret_setting('DATABASE_NAME'),
#         'USER': get_secret_setting('DATABASE_USER'),
#         'PASSWORD': get_secret_setting('DATABASE_PASSWORD'),
#         'HOST': get_secret_setting('DATABASE_HOST'),
#         'PORT': get_secret_setting('DATABASE_PORT'),
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

MEDIA_ROOT = "/home/benbb96/media"

# Stockage media via Google Cloud Storage (bucket Firebase existant = bucket GCS).
# Spécifique à la prod : en dev, le stockage reste local (FileSystemStorage + MEDIA_ROOT).
from google.oauth2 import service_account  # noqa: E402

GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
    get_secret_setting("GCS_CREDENTIALS")
)
GS_BUCKET_NAME = "eminent-airport-148108.appspot.com"
GS_LOCATION = "media"
GS_DEFAULT_ACL = "publicRead"
GS_QUERYSTRING_AUTH = False

# staticfiles : WhiteNoise hashe les noms de fichiers (manifest) et pré-compresse
# en gzip + brotli à collectstatic, ce qui permet de servir /static/ en
# `Cache-Control: max-age=315360000, public, immutable`.
#
# Deux prérequis vivent côté PythonAnywhere, hors dépôt — si l'un des deux saute,
# le site se retrouve sans CSS parce que le HTML réclame des noms hashés :
#
# 1. Le mapping statique /static/ du Web tab doit être SUPPRIMÉ, sinon nginx
#    intercepte les requêtes en amont et WhiteNoise ne les voit jamais.
# 2. /var/www/www_benbb96_com_wsgi.py doit exposer `get_wsgi_application()` NU.
#    Il enveloppait l'app dans un `StaticFilesHandler`, qui capte /static/ avant
#    la pile de middlewares et sert via les finders (donc depuis assets/, où les
#    noms hashés n'existent pas) : tous les fichiers hashés partaient en 404.
STORAGES = {
    "default": {"BACKEND": "storages.backends.gcloud.GoogleCloudStorage"},
    "staticfiles": {
        "BACKEND": "config.storages.NonStrictCompressedManifestStaticFilesStorage"
    },
}

GOOGLE_ANALYTICS_KEY = get_secret_setting("GOOGLE_ANALYTICS_KEY")

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 30
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# Framework MAILERS (Django 6+) : on surcharge le mailer par défaut de base.py
# pour envoyer via Anymail/Mailgun en prod. Le réglage ANYMAIL reste lu normalement
# (ce n'est pas un réglage EMAIL_* déprécié).
MAILERS = {
    "default": {
        "BACKEND": "anymail.backends.mailgun.EmailBackend",
    },
}
ANYMAIL = {
    "MAILGUN_API_KEY": get_secret_setting("ACCESS-KEY"),
    "MAILGUN_SENDER_DOMAIN": get_secret_setting("SERVER-NAME"),
}
