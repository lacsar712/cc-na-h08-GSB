"""Settings for running the test suite without PostgreSQL.

Usage: python manage.py test --settings=config.settings_test
"""

from config.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
