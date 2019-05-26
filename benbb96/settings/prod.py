import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret_setting('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', '192.168.42.62', 'benbb96.pythonanywhere.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_secret_setting('DATABASE_NAME'),
        'USER': get_secret_setting('DATABASE_USER'),
        'PASSWORD': get_secret_setting('DATABASE_PASSWORD'),
        'HOST': get_secret_setting('DATABASE_HOST'),
        'PORT': get_secret_setting('DATABASE_PORT'),
    }
}

MEDIA_ROOT = '/home/benbb96/media'