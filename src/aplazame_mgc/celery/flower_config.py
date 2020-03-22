# coding=utf-8
import os

# http://flower.readthedocs.io/en/latest/config.html
# Extra configuration for Flower. Basic celery setup is still required.

# RabbitMQ management api
broker_api = 'http://aplazame_mgc_rabbitmq_user:1234_password_extra_safe@rabbitmq:15672/api/'


# Set logging level
logging = 'INFO'
