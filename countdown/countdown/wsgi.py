"""
WSGI config for countdown project.
Production deployment uses countdown.settings.prod.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'countdown.settings.prod')

application = get_wsgi_application()
