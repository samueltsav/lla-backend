from .base import *
import django_mongodb_backend
from content_service_config.env import env

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]