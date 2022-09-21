"""Django settings for summers_api project.

Generated by 'django-admin startproject' using Django 4.0.3.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import json
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
# Read .env file and set os envs.
env.read_env(str(BASE_DIR / ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="yjpMJooCUHQWmtToTV42qwtXtpZ40KsMXdqOgHDgU0Iz8PdiunWAzys0lyr0RAUg",
)
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"],
)

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "social_django",
    "rest_social_auth",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.users",
    "apps.tube2drive",
    "apps.news",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = (
    "social_core.backends.open_id.OpenIdAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.google.GoogleOAuth",
    "django.contrib.auth.backends.ModelBackend",
)

ROOT_URLCONF = "summers_api.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "summers_api.wsgi.application"
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "djongo",
        "NAME": "summersapi",
        "ENFORCE_SCHEMA": False,
        "ATOMIC_REQUESTS": True,
        "CLIENT": {
            "host": env("DATABASE_URL"),
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# STATIC AND MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_FILE_STORAGE = "apps.common.storage.CustomFileStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:8080", "http://127.0.0.1:8080"],
)

# CSRF
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# AWS S3 bucket
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION")
AWS_S3_BUCKET = env("AWS_S3_BUCKET")
AWS_S3_ORIGIN = env("AWS_S3_ORIGIN")

CORS_ALLOWED_ORIGINS.append(AWS_S3_ORIGIN)

# GCP
GCP_SERVICE_ACCOUNT_CONTENT: str = env("GCP_SERVICE_ACCOUNT_CONTENT")
GCP_SERVICE_ACCOUNT_JSON: dict[str, str] = json.loads(GCP_SERVICE_ACCOUNT_CONTENT)

# Uses this service account when first one exceedes GCP API usage limit
GCP_SERVICE_ACCOUNT_CONTENT1: str = env("GCP_SERVICE_ACCOUNT_CONTENT1")
GCP_SERVICE_ACCOUNT_JSON1: dict[str, str] = json.loads(GCP_SERVICE_ACCOUNT_CONTENT1)

# Social auth

# For google
# https://accounts.google.com/o/oauth2/v2/auth?
# scope=https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile&
# access_type=offline&
# include_granted_scopes=true&
# response_type=code&
# redirect_uri=redirect_uri&
# client_id=client_id

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Imgur API
IMGUR_CLIENT_ID = env("IMGUR_CLIENT_ID")
IMGUR_UPLOAD_ENDPOINT = env("IMGUR_UPLOAD_ENDPOINT")
IMGUR_SUPPORTED_FORMAT = [
    # image formats
    "image/png",
    "image/jpg",
    "image/jpeg",
    # video formats
    "video/mp4",
    "video/webm",
    "video/x-matroska",
    "video/quicktime",
    "video/x-flv",
    "video/x-msvideo",
    "video/x-ms-wmv",
    "video/mpeg",
]

# For news
OPEN_WEATHER_API_KEY = env("OPEN_WEATHER_API_KEY")
NEWS_DATA_IO_API_KEY = env("NEWS_DATA_IO_API_KEY")
DEFAULT_NEWS_IMAGE_URL = env("DEFAULT_NEWS_IMAGE_URL")


# Utils
CURRENT_DOMAIN = env("CURRENT_DOMAIN")
YOUTUBE_DL_FILE_LIMIT = env("YOUTUBE_DL_FILE_LIMIT", cast=int)
