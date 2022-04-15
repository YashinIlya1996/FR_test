import os

from celery import Celery

# config path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FR_test.settings')

app = Celery('FR_test')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Need import app in project's __init__.py
