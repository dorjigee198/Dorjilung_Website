import os

from .base import *

DEBUG = False

# WhiteNoise serves static files directly from the WSGI app (via the
# middleware in base.py) — no nginx/reverse proxy required. Its storage
# backend also hashes filenames for cache-busting, same purpose as
# Django's ManifestStaticFilesStorage, plus gzip/brotli precompression.
# See https://whitenoise.readthedocs.io/en/latest/django.html
STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Config is read from environment variables when present — the standard
# pattern for Docker deployments (see "docker run -e ..." in the deploy
# notes). Falls back to a local.py file below for non-Docker deployments.
if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ["SECRET_KEY"]
if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")
if os.environ.get("WAGTAILADMIN_BASE_URL"):
    WAGTAILADMIN_BASE_URL = os.environ["WAGTAILADMIN_BASE_URL"]

try:
    from .local import *
except ImportError:
    pass
