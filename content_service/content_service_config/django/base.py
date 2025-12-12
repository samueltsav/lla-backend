import os
import sys
import django_mongodb_backend
from content_service_config.third_party.celery import *
from content_service_config.third_party.spectacular import *
from content_service_config.third_party.cache import *
from content_service_config.env import BASE_DIR, env


sys.path.append("/app")

env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("DJANGO_SECRET_KEY")
SERVICE_INTERNAL_TOKEN = env("SERVICE_INTERNAL_TOKEN")

DJANGO_ENV = env("DJANGO_SETTINGS_MODULE", default="content_service_config.django.dev")


DEBUG = env.bool("DEBUG", default=True)

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
ALLOWED_HOSTS = ["*"]
USER_SERVICE_URL = env("USER_SERVICE_URL")


# Switching between development and production environments secrets
if DJANGO_ENV == "user_service_config.django.dev":
    CLERK_PUBLISHABLE_KEY = env("CLERK_PUBLISHABLE_KEY")
    CLERK_WEBHOOK_SECRET = env("CLERK_WEBHOOK_SECRET")
    CLERK_FRONTEND_API_URL = env(
        "CLERK_FRONTEND_API_URL", default="https://api.clerk.com"
    )
    CLERK_API_URL = env("CLERK_API_URL", default="https://api.clerk.com")
    CLERK_AUDIENCE = env.list("CLERK_AUDIENCE", default=[])
    CLERK_SECRET_KEY = env("CLERK_SECRET_KEY")
else:
    CLERK_PUBLISHABLE_KEY = env("CLERK_PUBLISHABLE_KEY")
    CLERK_WEBHOOK_SECRET = env("CLERK_WEBHOOK_SECRET")
    CLERK_FRONTEND_API_URL = env(
        "CLERK_FRONTEND_API_URL", default="https://api.clerk.com"
    )
    CLERK_API_URL = env("CLERK_API_URL", default="https://api.clerk.com")
    CLERK_AUDIENCE = env.list("CLERK_AUDIENCE", default=[])
    CLERK_SECRET_KEY = env("CLERK_SECRET_KEY")


# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Application definition
INSTALLED_APPS = [
    "content_service_config.apps.MongoAdminConfig",
    "content_service_config.apps.MongoAuthConfig",
    "content_service_config.apps.MongoContentTypesConfig",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-Party apps
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # local apps
    "content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "content_service_config.urls"

# Rest Framework Settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "content.auth.ClerkAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

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

WSGI_APPLICATION = "content_service_config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# Datatase configuation

# Switching databases based on environment
if DJANGO_ENV == "user_service_config.django.dev":
    DATABASES = {
        "default": django_mongodb_backend.parse_uri(env("DEV_CONNECTION_STRING"))
    }
else:
    DATABASES = {
        "default": django_mongodb_backend.parse_uri(env("PROD_CONNECTION_STRING"))
    }

# Database routers
# https://docs.djangoproject.com/en/dev/ref/settings/#database-routers
DATABASE_ROUTERS = ["django_mongodb_backend.routers.MongoRouter"]

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


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

MIGRATION_MODULES = {
    "admin": "mongo_migrations.admin",
    "auth": "mongo_migrations.auth",
    "contenttypes": "mongo_migrations.contenttypes",
}
