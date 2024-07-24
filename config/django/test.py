import os

os.environ.setdefault("DEBUG_TOOLBAR_ENABLED", "False")

from .base import *  # noqa

# Based on https://www.hacksoft.io/blog/optimize-django-build-to-run-faster-on-github-actions

DEBUG = False