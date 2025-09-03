from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery


sys.path.append("/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_management.settings")

app = Celery("user_management")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
