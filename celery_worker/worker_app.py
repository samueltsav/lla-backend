from __future__ import absolute_import, unicode_literals
import sys
from datetime import timedelta
from celery import Celery
from shared import celery_settings

# paths
sys.path.insert(0, "/app/user_service")
sys.path.insert(0, "/app/content_service")

from task_discovery import discover_tasks, setup_django_environments


setup_django_environments()

app = Celery("central_worker")


app.conf.update(
    broker_url=celery_settings.CELERY_BROKER_URL,
    result_backend=celery_settings.CELERY_RESULT_BACKEND,
    task_routes=celery_settings.CELERY_TASK_ROUTES,
    task_default_queue=celery_settings.CELERY_TASK_DEFAULT_QUEUE,
    task_queues=celery_settings.CELERY_TASK_QUEUES,
    worker_prefetch_multiplier=celery_settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    task_acks_late=celery_settings.CELERY_TASK_ACKS_LATE,
    worker_max_tasks_per_child=celery_settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    task_serializer=celery_settings.CELERY_TASK_SERIALIZER,
    result_serializer=celery_settings.CELERY_RESULT_SERIALIZER,
    accept_content=celery_settings.CELERY_ACCEPT_CONTENT,
    timezone=celery_settings.CELERY_TIMEZONE,
    enable_utc=celery_settings.CELERY_ENABLE_UTC,
    task_time_limit=celery_settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=celery_settings.CELERY_TASK_SOFT_TIME_LIMIT,
    task_reject_on_worker_lost=celery_settings.CELEY_TASK_REJECT_ON_WORKER_LOST,
)

app.conf.beat_schedule = {
    "daily-progress-analysis": {
        "task": "analyze_user_progress",
        "schedule": timedelta(days=1),
        "options": {"queue": "users"},
    },
    "cleanup-old-results": {
        "task": "cleanup_old_results",
        "schedule": timedelta(days=7),
        "options": {"queue": "users"},
    },
}

discovered_tasks = discover_tasks()
app.conf.include = discovered_tasks

if __name__ == "__main__":
    app.start()
