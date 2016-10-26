#!/usr/bin/env python
 
# some original codes we need
import os
 
virtenv = os.environ['APPDIR'] + '/virtenv/'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python3.3/site-packages')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except:
    pass
 
# new codes we adding for Django
import sys
import django.core.handlers.wsgi
 
os.environ['DJANGO_SETTINGS_MODULE'] = os.environ['OPENSHIFT_APP_NAME']+'.settings'
sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'wsgi', os.environ['OPENSHIFT_APP_NAME']))
application = django.core.handlers.wsgi.WSGIHandler()