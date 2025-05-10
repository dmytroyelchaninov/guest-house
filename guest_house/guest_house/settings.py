import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = config('DEBUG', default=True, cast=bool)

# --- security -------------------------------------------------
SECRET_KEY = config('SECRET_KEY', default='unsafe-dummy-key-change-me')

# Admin‑panel single‑key auth
HOTEL_ADMIN_KEY = config('HOTEL_ADMIN_KEY', default='longguesthouse')
TOKEN_SALT      = config('TOKEN_SALT',      default='hotel-admin-token')
COOKIE_NAME     = config('COOKIE_NAME',     default='hotel_admin_token')
MAX_AGE         = config('MAX_AGE',         default=60*60*8, cast=int)  # 8 h

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# --- Django core ---------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'bookings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'guest_house.urls'
WSGI_APPLICATION = 'guest_house.wsgi.application'

# --- database -------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     config('DB_NAME', default='guest_house'),
        'USER':     config('DB_USER', default='guest'),
        'PASSWORD': config('DB_PASS', default='guest'),
        'HOST':     config('DB_HOST', default='localhost'),
        'PORT':     config('DB_PORT', default='5432'),
    }
}

# --- email ----------------------------------------------------
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='hotel@example.com')

# --- static / media ------------------------------------------
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

# --- other ----------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N = True
USE_TZ   = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

