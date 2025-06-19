import os

from config.env import BASE_DIR

# Ensure logs directory exists
os.makedirs(f"{BASE_DIR}/logs", exist_ok=True)

FORMATTERS = {
    "verbose": {
        "format": "{levelname} {asctime:s} {threadName} {thread:d} {module} {filename} {lineno:d} {name} {funcName} {process:d} {message}",  # noqa: E501
        "style": "{",
    },
    "simple": {
        "format": "{levelname} {asctime:s} {module} {filename} {lineno:d} {funcName} {message}",
        "style": "{",
    },
}

HANDLERS = {
    "console_handler": {
        "class": "logging.StreamHandler",
        "formatter": "simple",
    },
    "my_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/tena_adam.log",
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "simple",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "my_handler_detailed": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/tena_adam_detailed.log",
        "mode": "a",
        "formatter": "verbose",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
}

LOGGERS = {
    "django": {
        "handlers": ["console_handler", "my_handler_detailed"],
        "level": "INFO",
        "propagate": False,
    },
    "django.request": {
        "handlers": ["my_handler"],
        "level": "WARNING",
        "propagate": False,
    },
    "core": {
        "handlers": ["console_handler", "my_handler_detailed"],
        "level": "INFO",
        "propagate": False,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS,
    "handlers": HANDLERS,
    "loggers": LOGGERS,
}
