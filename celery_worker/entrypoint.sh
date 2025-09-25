#!/bin/ash

# Wait for redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "Redis is ready!"

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ..."
while ! nc -z rabbitmq 5672; do
    sleep 1
done
echo "RabbitMQ is ready!"

# Wait for services to be ready
echo "Waiting for services..."
sleep 10

# Check if this is beat, flower, or worker
if [ "$1" = "beat" ]; then
    echo "Starting Celery Beat..."
    exec celery -A worker_app beat --loglevel=info
elif [ "$1" = "flower" ]; then
    echo "Starting Flower..."
    exec celery -A worker_app flower --port=5555
else
    echo "Starting Celery Worker..."
    exec celery -A worker_app worker --loglevel=info --concurrency=4 --queues=default,user_queue,content_queue
fi
