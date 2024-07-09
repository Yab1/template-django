import os

from config.env import BASE_DIR

MEDIA_ROOT_NAME = "media"
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_ROOT_NAME)
MEDIA_URL = f"/{MEDIA_ROOT_NAME}/"
