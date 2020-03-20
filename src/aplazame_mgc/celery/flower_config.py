# coding=utf-8
import os

# http://flower.readthedocs.io/en/latest/config.html
# Extra configuration for Flower. Basic celery setup is still required.

# RabbitMQ management api
broker_api = 'http://{user}:{password}@rabbitmq:15672/api/'.format(
    user=os.environ.get('RABBITMQ_DEFAULT_USER'),
    password=os.environ.get('RABBITMQ_DEFAULT_PASS'),
)


# Set logging level
logging = 'INFO'
