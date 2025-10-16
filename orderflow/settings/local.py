import socket

from .base import *  # noqa F403
from .base import REST_FRAMEWORK

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
# ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
ALLOWED_HOSTS = ["*"]

# Django Debug Toolbar
# https://docs.djangoproject.com/en/4.2/intro/tutorial08/#installing-django-debug-toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]

# django-debug-toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405

MIDDLEWARE += [  # noqa F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# Enable Browsable API Renderer for local development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] += [
    "rest_framework.renderers.BrowsableAPIRenderer",
]


# Serve static locally in DEBUG
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


# Local static URL
STATIC_URL = "/static/"
