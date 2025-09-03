#!/bin/ash

echo "Making migrations"
python manage.py makemigrations --noinput

echo "Applying migrations"
python manage.py migrate --noinput

exec "$@"