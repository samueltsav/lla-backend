#!/bin/ash
until curl -s http://user-service:8000/health; do
  echo "Waiting for User Service..."
  sleep 2
done

until curl -s http://content-service:8000/health; do
  echo "Waiting for Content Service..."
  sleep 2
done

exec "$@"