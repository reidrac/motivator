# Django settings for motivator project.

DEV = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('yourname', 'your-mail@your-domain.local'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'data/database.sqlite3',
    }
}

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-gb'

SITE_ID = 1
SITE_BASE = 'http://motivator.your-domain.local/'

USE_I18N = False
USE_L10N = True

# FIXME: should be absolute
MEDIA_ROOT = './media/'

# FIXME: should be something like media-motivator.usebox.net
MEDIA_URL = '/mediax/'

ADMIN_MEDIA_PREFIX = '/media/'

# generate your own: https://gist.github.com/1002796
SECRET_KEY = '~Ei:FO Bd!C[?~d+wN31TH{BwlwT= ("pxq|M/.P X1~0^V#R{x>0LYXWEC8K1`}")}]'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'motivator.urls'

TEMPLATE_DIRS = (
    # FIXME: use absolute paths, not relative paths.
    './templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'motivator.public',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHE_BACKEND = 'file:///tmp/django_cache'

# load local settings (if available)
try:
    from local import *
except ImportError:
    pass

