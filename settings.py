from mezzanine.project_template.settings import *
import os
from datetime import timedelta

import djcelery
djcelery.setup_loader()

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIRNAME = PROJECT_ROOT.split(os.sep)[-1]
STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip("/").split("/"))
ROOT_URLCONF = "%s.urls" % PROJECT_DIRNAME
TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, "templates"),)

INSTALLED_APPS = (
    "main",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "mezzanine.boot",
    "mezzanine.conf",
    "mezzanine.core",
    "mezzanine.generic",
    "mezzanine.accounts",
    #for celery msg broker                                                                                                                                               
    'kombu.transport.django',

    "djcelery",
    "django_mailbox",
    "mail_reader"
)

MIDDLEWARE_CLASSES = (["mezzanine.core.middleware.UpdateCacheMiddleware"] +
                      list(MIDDLEWARE_CLASSES) +
                      ["mezzanine.core.middleware.FetchFromCacheMiddleware"])
MIDDLEWARE_CLASSES.remove("mezzanine.pages.middleware.PageMiddleware")

# Mezzanine
AUTH_PROFILE_MODULE = "main.Profile"
SITE_TITLE = "Drum"
RATINGS_RANGE = (-1, 1)
RATINGS_ACCOUNT_REQUIRED = True
COMMENTS_ACCOUNT_REQUIRED = True
ACCOUNTS_PROFILE_VIEWS_ENABLED = True

# Celery

# Broker
BROKER_URL = "django://"

# List of modules to import when celery starts.                                                                                                                          
CELERY_IMPORTS = ("mail_reader.tasks", )

# Using the database to store task state and results.                                                                                                                   
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "sqlite:///dev.db"

CELERY_TIMEZONE = 'UTC'
TIME_ZONE = 'Europe/London'

CELERY_ANNOTATIONS = {
    "tasks.checkMail": {"rate_limit": "10/s"}

}

CELERYBEAT_SCHEDULE = {
    'check-mail-every-10-minutes': {
        'task': 'mail_reader.tasks.checkMail',
        'schedule': timedelta(seconds=10),
        'args': ()
    },
}

# Drum
ALLOWED_DUPLICATE_LINK_HOURS = 24 * 7 * 3
ITEMS_PER_PAGE = 20

# External settings imports
try:
    from local_settings import *
except ImportError:
    pass

try:
    from logger_settings import *
except ImportError:
    pass

try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
