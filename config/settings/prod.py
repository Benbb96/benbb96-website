from .base import *

SECRET_KEY = get_secret_setting('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['.benbb96.com']

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
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT = '/home/benbb96/media'

GOOGLE_ANALYTICS_KEY = get_secret_setting('GOOGLE_ANALYTICS_KEY')

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 30
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# Configuration de l'envoi des mails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = get_secret_setting('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret_setting('EMAIL_HOST_PASSWORD')
