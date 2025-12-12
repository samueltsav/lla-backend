import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service_config.django.dev")

application = get_wsgi_application()
