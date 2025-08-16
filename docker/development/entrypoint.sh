#!/bin/sh
set -e

echo "Waiting for database..."
sleep 10

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start main Django app on port 8000
echo "Starting main Django app on port 8000..."
python manage.py runserver 0.0.0.0:8000 &

# Start Celery worker.
echo "Starting Celery worker..."
celery -A config.settings.celery.app worker --loglevel=info --pool=solo &

# Start Celery beat
echo "Starting Celery beat..."
celery -A config.settings.celery.app beat --loglevel=info &

# Wait for all background jobs (optional, for long-running script)
wait



