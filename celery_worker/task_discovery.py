import os
import sys
import importlib


def discover_tasks():
    tasks = []

    user_service_path = "/app/user_service"
    content_service_path = "/app/content_service"

    if user_service_path not in sys.path:
        sys.path.insert(0, user_service_path)
    if content_service_path not in sys.path:
        sys.path.insert(0, content_service_path)

    try:
        importlib.import_module("users.tasks")
        tasks.extend(["users.tasks"])
    except ImportError as e:
        print(f"Could not import user management tasks: {e}")

    try:
        importlib.import_module("content.tasks")
        tasks.extend(["content.tasks"])
    except ImportError as e:
        print(f"Could not import content service tasks: {e}")

    return tasks


def setup_django_environments():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "content_service_config.django.dev"
    )
    try:
        import django
        from django.conf import settings

        if not settings.configured:
            django.setup()
    except Exception as e:
        print(f"Error setting up Django for user management: {e}")
