from datetime import timedelta

# Simple JWT settings
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html

# Access token lifetime: 1 hour
ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)

# Refresh token lifetime: 30 days
REFRESH_TOKEN_LIFETIME = timedelta(days=5)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": ACCESS_TOKEN_LIFETIME,
    "REFRESH_TOKEN_LIFETIME": REFRESH_TOKEN_LIFETIME,
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
