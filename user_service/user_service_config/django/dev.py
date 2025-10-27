from .base import *
from user_service_config.env import env


DEBUG = env.bool("DEBUG", default=True)

