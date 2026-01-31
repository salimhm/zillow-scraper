"""
WSGI config for zillow_scraper project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zillow_scraper.settings')

application = get_wsgi_application()
