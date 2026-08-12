import os
from .base import *

# In production, require SECRET_KEY to be set in environment variables
SECRET_KEY = os.environ['SECRET_KEY']

# Never run with debug turned on in production
DEBUG = False

# Read allowed hosts from environment, separated by commas
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

import dj_database_url

# Database configuration: read DATABASE_URL from environment with SQLite fallback
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# HTTPS & Cookie Security Headers
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HTTP Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# Setup secure HSTS settings if SSL redirect is enabled
if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Production Email Backend
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    },
}

