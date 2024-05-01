import datetime
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = bool(int(os.getenv("DEBUG")))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # extensions
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",

    # apps
    "common.apps.CommonConfig",
    "users.apps.UsersConfig",
    "blog.apps.BlogConfig",
    "notifications.apps.NotificationsConfig"
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'common.api.pagination.PageCountPagination',
    'PAGE_SIZE': 10,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    "TEST_REQUEST_DEFAULT_FORMAT": "json"
}

# Rest Framework Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=5),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": os.getenv("JWT_ALGORITHM"),
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY"),
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": datetime.timedelta(0),

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",

    "JTI_CLAIM": "jti",
}

# Auth
PASSWORD_RESET_TIMEOUT = int(os.getenv("PASSWORD_RESET_TIMEOUT", 60 * 60 * 24 * 3))  # Default: 3 days.
CONFIRM_EMAIL_TIMEOUT = int(os.getenv("CONFIRM_EMAIL_TIMEOUT", 60 * 60 * 24 * 10))  # Default 10 days.

# Hosts
HOST = "http://web:8000"
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "REPLACE_ME").rstrip("/")

ALLOWED_HOSTS = [
    "web"
]
## CSRF
CSRF_TRUSTED_ORIGINS = [
    # Local
    "http://0.0.0.0:8000",
]

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "REPLACE_ME")
EMAIL_PORT = os.getenv("EMAIL_PORT", "REPLACE_ME")

EMAIL_USE_LOCALTIME = False

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "REPLACE_ME")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "REPLACE_ME")
EMAIL_USE_TLS = bool(int(os.getenv("EMAIL_USE_TLS", 0)))
EMAIL_USE_SSL = bool(int(os.getenv("EMAIL_USE_SSL", 0)))
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "REPLACE_ME")

# Test configuration
TEST_RUNNER = 'common.tests.TestRunner'
TEST_OUTPUT_VERBOSE = 1
TEST_OUTPUT_DIR = ".github/reports/tests"
TEST_OUTPUT_DESCRIPTIONS = False
