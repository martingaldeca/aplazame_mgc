# coding=utf-8
import os

from kombu import Queue, Exchange

# Docs:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
# https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html
# http://www.madhur.co.in/blog/2015/11/17/celery-tips-and-tricks.html


# >> Celery Tasks configuration
task_default_queue = 'aplazame_queue'
task_queues = (
    Queue('aplazame_queue', Exchange('aplazame_queue'), routing_key='aplazame_queue'),
)

# >> Periodic Tasks configuration
# http://docs.celeryproject.org/en/v4.1.0/userguide/periodic-tasks.html#using-custom-scheduler-classes
beat_scheduler = 'celery.beat.PersistentScheduler'  # default scheduler
# beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler' # 3rd-party scheduler


# >> broker config (Rabbit MQ)
RABBIT_HOSTNAME = 'rabbitmq'
RABBIT_AMPQ_HOST = '%s:5672' % RABBIT_HOSTNAME
RABBIT_MANAGEMENT_HOST = '%s:15672' % RABBIT_HOSTNAME
RABBIT_USER = os.environ.get('RABBITMQ_DEFAULT_USER')
RABBIT_PASSWORD = os.environ.get('RABBITMQ_DEFAULT_PASS')
RABBIT_ENV_VHOST = os.environ.get('RABBIT_ENV_VHOST', '')

broker_url = 'pyamqp://{user}:{password}@{hostname}/{vhost}'.format(
    user=RABBIT_USER,
    password=RABBIT_PASSWORD,
    hostname=RABBIT_AMPQ_HOST,
    vhost=RABBIT_ENV_VHOST,
)

broker_pool_limit = 10
broker_connection_timeout = 60
broker_heartbeat = 30

# Enable "publisher confirms" to allow application to be sure when a message has been sent
# http://www.rabbitmq.com/blog/2011/02/10/introducing-publisher-confirms/
# https://tech.labs.oliverwyman.com/blog/2015/04/30/making-celery-play-nice-with-rabbitmq-and-bigwig/
broker_transport_options = {'confirm_publish': True}

# Sensible settings for celery
task_always_eager = False
task_publish_retry = True
worker_disable_rate_limits = False

task_ignore_result = False
result_expires = 600

# Policy of task ACK.
# > normal:
# task_acks_late = False
# task_reject_on_worker_lost = False
# > late with countermeasures
# task_acks_late = True
# task_reject_on_worker_lost = True
# > current:
task_acks_late = True

# Don't use pickle as serializer, json is much safer
task_serializer = "json"
result_serializer = "json"
accept_content = ['application/json']

worker_hijack_root_logger = False
worker_prefetch_multiplier = 1  # Default: 4. Set it to '1' to disable prefetching
worker_max_tasks_per_child = 1000  # Default: nolimit

# >> Events
# Send task-related events so that tasks can be monitored using tools like flower.
# Default: disabled. Expected override by `celery worker -E`
worker_send_task_events = True
# If enabled, a task-sent event will be sent for every task so tasks can be tracked before they’re consumed by a worker.
task_send_sent_event = True

# >> result_backend
# Default: No result backend enabled by default.
# The backend used to store task results (tombstones).
result_backend = 'django-db'

# >> result_persistent
# Default: Disabled by default (transient messages).
# If set to True, result messages will be persistent. This means the messages won’t be lost after a broker restart.
# result_persistent = True
