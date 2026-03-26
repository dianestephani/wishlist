"""
WSGI config for wishlist_app project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wishlist_app.settings")

application = get_wsgi_application()

# Wrap with WhiteNoise to serve media files in production
from whitenoise import WhiteNoise
from django.conf import settings

application = WhiteNoise(application, root=settings.STATIC_ROOT)
application.add_files(settings.MEDIA_ROOT, prefix="media/")
