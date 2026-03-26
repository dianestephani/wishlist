"""
ASGI config for wishlist_app project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wishlist_app.settings")

application = get_asgi_application()
