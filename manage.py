"""Django's command-line utility for administrative tasks."""

import sys
from pathlib import Path

import environ


def main():
    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent
    env = environ.Env()
    env.read_env(str(BASE_DIR / ".env"))
    # Reading env to set `DJANGO_SETTINGS_MODULE`

    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
