"""
ASGI config for Kyly Picking project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kyly_picking.settings')

application = get_asgi_application()
