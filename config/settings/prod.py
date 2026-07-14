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

STORAGES = {
    "default": {"BACKEND": "storages.backends.gcloud.GoogleCloudStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
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

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": get_secret_setting("ACCESS-KEY"),
    "MAILGUN_SENDER_DOMAIN": get_secret_setting("SERVER-NAME"),
}
