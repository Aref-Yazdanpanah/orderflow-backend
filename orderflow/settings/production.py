from .base import *  # noqa
from .base import env

# ------------------------------------------------------------------------------
# GENERAL
# ------------------------------------------------------------------------------
DEBUG = False
ALLOWED_HOSTS = ["*"]  # Consider setting real domains in production

# ------------------------------------------------------------------------------
# CORSHEADERS
# ------------------------------------------------------------------------------
INSTALLED_APPS = ["corsheaders"] + INSTALLED_APPS

MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    "content-type",
    "authorization",
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
