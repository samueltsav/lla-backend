from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery


sys.path.append("/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_management.settings")

app = Celery("content_management")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
