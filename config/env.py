import os
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()

BASE_DIR: Path = Path(__file__).resolve().parent.parent
APPS_DIR: str = os.path.join(BASE_DIR, "core")


def env_to_enum(enum_cls, value):
    for x in enum_cls:
        if x.value == value:
            return x

    raise ImproperlyConfigured(f"Env value {repr(value)} could not be found in {repr(enum_cls)}")
