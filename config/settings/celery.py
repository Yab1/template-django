from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from config.env import env

# https://docs.celeryproject.org/en/stable/userguide/configuration.html


CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="amqp://guest:guest@localhost//")
CELERY_RESULT_BACKEND = "django-db"

CELERY_TIMEZONE = "UTC"

CELERY_TASK_SOFT_TIME_LIMIT = 20  # seconds
CELERY_TASK_TIME_LIMIT = 30  # seconds
CELERY_TASK_MAX_RETRIES = 3

# Celery Beat Schedule
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.base")

app = Celery("django-celery")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks()
