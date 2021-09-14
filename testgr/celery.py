import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testgr.settings')

app = Celery('testgr')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Manual task example
# app.conf.beat_schedule = {
#     'Clean every 30 seconds': {
#         'task': 'main.tasks.task_stop_running_jobs',
#         'schedule': 30.0
#     },
# }

