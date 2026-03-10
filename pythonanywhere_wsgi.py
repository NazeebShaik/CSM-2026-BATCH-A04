# PythonAnywhere WSGI template
# Copy this to /var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py
# Replace YOUR_USERNAME with your PythonAnywhere username

import os
import sys

# Production settings - REQUIRED for security
os.environ['DJANGO_DEBUG'] = '0'
os.environ['DJANGO_SECRET_KEY'] = 'CHANGE-THIS-GENERATE-WITH-python-c-import-secrets-print-secrets-token_urlsafe-50'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'YOUR_USERNAME.pythonanywhere.com,.pythonanywhere.com'

path = '/home/YOUR_USERNAME/forensic'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ImprovingDigitalForensicSecurity.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
