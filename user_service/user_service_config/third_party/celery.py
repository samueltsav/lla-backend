from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery


sys.path.append("/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service_config.django.dev")

app = Celery("user_service_config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
