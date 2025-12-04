import os
import sys
from user_service_config.third_party.celery import *
from user_service_config.third_party.spectacular import *
from user_service_config.third_party.cache import *
from user_service_config.env import BASE_DIR, env


# Load environment variables from .env file
env.read_env(os.path.join(BASE_DIR, ".env"))

sys.path.append("/app")


DJANGO_ENV = env("DJANGO_SETTINGS_MODULE")

DEBUG = env.bool("DEBUG", default=True)
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
ALLOWED_HOSTS = ["*"]
CONTENT_SERVICE_URL = env("CONTENT_SERVICE_URL")

# Switching between development and production environments secrets
if DJANGO_ENV == "user_service_config.django.dev":
    CLERK_PUBLISHABLE_KEY = env("CLERK_PUBLISHABLE_KEY")
    CLERK_WEBHOOK_SECRET = env("CLERK_WEBHOOK_SECRET")
    CLERK_FRONTEND_API_URL = env(
        "CLERK_FRONTEND_API_URL", default="https://api.clerk.com"
    )
    CLERK_API_URL = env("CLERK_API_URL", default="https://api.clerk.com")
    CLERK_AUDIENCE = env.list("CLERK_AUDIENCE", default=[])
else:
    CLERK_PUBLISHABLE_KEY = env("CLERK_PUBLISHABLE_KEY")
    CLERK_WEBHOOK_SECRET = env("CLERK_WEBHOOK_SECRET")
    CLERK_FRONTEND_API_URL = env(
        "CLERK_FRONTEND_API_URL", default="https://api.clerk.com"
    )
    CLERK_API_URL = env("CLERK_API_URL", default="https://api.clerk.com")
    CLERK_AUDIENCE = env.list("CLERK_AUDIENCE", default=[])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party librararies
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # local apps
    "users",
    "dashboard",
]

AUTH_USER_MODEL = "users.User"


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "user_service_config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates/users"],
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

WSGI_APPLICATION = "user_service_config.wsgi.application"

# Switching databases based on environment
if DJANGO_ENV == "user_service_config.django.dev":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DEV_DB_NAME"),
            "USER": env("DEV_DB_USER"),
            "PASSWORD": env("DEV_DB_PASSWORD"),
            "HOST": env("DEV_DB_HOST"),
            "PORT": env("DEV_DB_PORT"),
            "OPTIONS": {
                "sslmode": env("DEV_DB_SSLMODE", default="require"),
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("PROD_DB_NAME"),
            "USER": env("PROD_DB_USER"),
            "PASSWORD": env("PROD_DB_PASSWORD"),
            "HOST": env("PROD_DB_HOST"),
            "PORT": env("PROD_DB_PORT"),
            "OPTIONS": {
                "sslmode": env("PROD_DB_SSLMODE", default="require"),
            },
        }
    }

# Email configuration
EMAIL_BACKEND = "users.utils.email_backend.AzureEmailBackend"
AZURE_EMAIL_CONNECTION_STRING = env("AZURE_EMAIL_CONNECTION_STRING")
AZURE_EMAIL_SENDER = env("AZURE_EMAIL_SENDER", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)

DOMAIN = env("DOMAIN", default="localhost:3000")
SITE_NAME = env("SITE_NAME", default="LinguAfrika")
SITE_ID = 1

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Enable compression and caching
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_CREDENTIALS = True

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.auth.ClerkJWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
