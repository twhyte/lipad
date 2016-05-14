"""
WSGI config for dilipadsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
import site
from django.core.wsgi import get_wsgi_application

site.addsitedir('/opt/dpdev/env/local/lib/python2.7/site-packages')
sys.path.append('/opt/dpdev/dilipad/dilipadsite')
sys.path.append('/opt/dpdev/dilipad/dilipadsite/dilipadsite')

activate_env=os.path.expanduser("/opt/dpdev/env/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dilipadsite.settings")

application = get_wsgi_application()
