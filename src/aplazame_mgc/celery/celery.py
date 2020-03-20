# coding=utf-8
from celery import Celery
from . import celery_config
import os

__module_dir__ = str(__name__).split('.')[:-1]
os.environ.setdefault('CELERY_CONFIG_MODULE', '%s.celeryconfig' % __module_dir__)

app = Celery('tasks')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(celeryconfig)

CELERY_TIMEZONE = 'UTC'

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
