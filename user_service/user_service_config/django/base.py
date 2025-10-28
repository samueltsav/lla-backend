import os
import sys
from datetime import timedelta
from user_service_config.third_party.axes import *
from user_service_config.third_party.celery import *
from user_service_config.third_party.djoser import *
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
JWT_ALGORITHM = env("JWT_ALGORITHM")
CONTENT_SERVICE_URL = env("CONTENT_SERVICE_URL")

# Switching JWT_KEY and SECRET_KEY based on environment
if DJANGO_ENV == "user_service_config.django.dev":
    JWT_KEY = env("DEV_JWT_KEY")
    SECRET_KEY = env("DEV_SECRET_KEY")
elif DJANGO_ENV == "user_service_config.django.stag":
    JWT_KEY = env("STAG_JWT_KEY")
    SECRET_KEY = env("STAG_SECRET_KEY")
else:
    JWT_KEY = env("PROD_JWT_KEY")
    SECRET_KEY = env("PROD_SECRET_KEY")

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
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "djoser",
    "axes",
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
    "axes.middleware.AxesMiddleware",
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
elif DJANGO_ENV == "user_service_config.django.stag":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("STAG_DB_NAME"),
            "USER": env("STAG_DB_USER"),
            "PASSWORD": env("STAG_DB_PASSWORD"),
            "HOST": env("STAG_DB_HOST"),
            "PORT": env("STAG_DB_PORT"),
            "OPTIONS": {
                "sslmode": env("STAG_DB_SSLMODE", default="require"),
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
    "axes.backends.AxesStandaloneBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Simple JWT Settings for JWT Authentication
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": JWT_ALGORITHM,
    "SIGNING_KEY": JWT_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "uid",
    "USER_ID_CLAIM": "uid",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(days=1),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
    "TOKEN_OBTAIN_SERIALIZER": "users.serializers.MyTokenCreateSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}
