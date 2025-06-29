#!/bin/sh

echo "Waiting for database..."
sleep 10

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000