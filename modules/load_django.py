import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'braincom_project')))

os.environ['DJANGO_SETTINGS_MODULE'] = 'braincom_project.settings'

django.setup()