from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qk0ynkcp0jux=jd8^oh!6gq86bbgc07a#!aex7h9x5%m*73cm#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')