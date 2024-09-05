from kettlebell_app.settings.base import *

DEBUG = False

SECRET_KEY = "REMOVED"

ALLOWED_HOSTS = ["ppkettlebell.toadres.pl", "localhost"]

LOG_PATH = "../logs"
DBBACKUP_PATH = "../dbbackup"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

STATIC_ROOT = BASE_DIR.joinpath("public")
