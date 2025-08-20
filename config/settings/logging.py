import os

from config.env import BASE_DIR

# Ensure logs directory exists
os.makedirs(f"{BASE_DIR}/logs", exist_ok=True)

# Rich logging configuration
try:
    import rich
    import rich.theme

    # Custom theme for better log colors
    my_theme = rich.theme.Theme({
        "logging.level.debug": "dim white",
        "logging.level.info": "bold blue",
        "logging.level.warning": "bold yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold red on white",
    })
    rich.reconfigure(theme=my_theme)

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

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
        "class": "rich.logging.RichHandler" if RICH_AVAILABLE else "logging.StreamHandler",
        "formatter": "simple" if not RICH_AVAILABLE else None,
        "rich_tracebacks": True,
        "show_time": True,
        "show_path": False,
    },
    "my_handler": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/django.log",
        "mode": "a",
        "encoding": "utf-8",
        "formatter": "simple",
        "backupCount": 5,
        "maxBytes": 1024 * 1024 * 5,  # 5 MB
    },
    "my_handler_detailed": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f"{BASE_DIR}/logs/django_detailed.log",
        "mode": "a",
        "formatter": "simple",
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
