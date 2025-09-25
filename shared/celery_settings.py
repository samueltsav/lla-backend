from dotenv import load_dotenv
from kombu import Queue


load_dotenv()
# Broker settings
CELERY_BROKER_URL = "amqp://tecvinson:linguafrika@rabbitmq:5672//"
CELERY_RESULT_BACKEND = "redis://redis:6379/1"

# Task discovery settings
CELERY_IMPORTS = [
    "users.tasks",
    "content.tasks",
]

# Queue configuration
CELERY_TASK_ROUTES = {
    "users.tasks.*": {"queue": "users_queue"},
    "content.tasks.*": {"queue": "content_queue"},
}

CELERY_TASK_DEFAULT_QUEUE = "default"

CELERY_TASK_QUEUES = (
    Queue("default", routing_key="default"),
    Queue("users_queue", routing_key="users"),
    Queue("content_queue", routing_key="content"),
)

# Worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Serialization
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Timezone
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task execution settings
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_IGNORE_RESULT = False
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60
CELEY_TASK_REJECT_ON_WORKER_LOST = True

# Result backend settings
RESULT_EXPIRES = 3600  # 1 hour
RESULT_PERSISTENT = True

# Monitoring
WORKER_SEND_TASK_EVENTS = True
TASK_SEND_SENT_EVENTS = True

# Security
WORKER_HIJACK_ROOT_LOGGER = False
WORKER_LOG_COLOR = False
