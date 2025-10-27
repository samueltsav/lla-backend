from __future__ import absolute_import, unicode_literals
from user_service_config.third_party.celery import app as celery_app
import sys

sys.path.append("/app")

__all__ = ("celery_app",)
