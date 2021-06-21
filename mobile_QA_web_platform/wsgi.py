"""
WSGI config for mobile_QA_web_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from google_appstore_reviews.crawler_tools.run_crawler import crawler_start


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mobile_QA_web_platform.settings.base")

application = get_wsgi_application()


# crawler startup entry
crawler_start(hour=0, minute=0, model='forever')





