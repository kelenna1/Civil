"""
Development settings for CandlesDown.
Usage: python manage.py runserver --settings=countdown.settings.dev
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Use the same PostgreSQL database (Railway) for consistency
import dj_database_url

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
}

# Relax security for local dev
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
