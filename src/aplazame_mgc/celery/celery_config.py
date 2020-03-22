# coding=utf-8
import os

from kombu import Queue, Exchange

task_default_queue = 'aplazame_task'
task_queues = (
    Queue('aplazame_task', Exchange('aplazame_task'), routing_key='aplazame_task'),
)
beat_scheduler = 'celery.beat.PersistentScheduler'  # default scheduler
RABBIT_HOSTNAME = 'rabbitmq'
RABBIT_AMPQ_HOST = 'rabbitmq:5672'
RABBIT_MANAGEMENT_HOST = '%rabbitmq:15672'
RABBIT_USER = 'aplazame_mgc_rabbitmq_user'
RABBIT_PASSWORD = '1234_password_extra_safe'
RABBIT_ENV_VHOST = ''

broker_url = f'pyamqp://{RABBIT_USER}:{RABBIT_PASSWORD}@{RABBIT_AMPQ_HOST}/{RABBIT_ENV_VHOST}'

broker_pool_limit = 10
broker_connection_timeout = 60
broker_heartbeat = 30

# Enable "publisher confirms" to allow application to be sure when a message has been sent
broker_transport_options = {'confirm_publish': True}

# Sensible settings for celery
task_always_eager = False
task_publish_retry = True
worker_disable_rate_limits = False
task_acks_late = True

# Don't use pickle as serializer, json is much safer
task_serializer = "json"
result_serializer = "json"
accept_content = ['application/json']

worker_hijack_root_logger = False
worker_prefetch_multiplier = 1  # Default: 4. Set it to '1' to disable prefetching
worker_max_tasks_per_child = 1000  # Default: nolimit

# >> Events
worker_send_task_events = True
task_send_sent_event = True
result_backend = 'django-db'

