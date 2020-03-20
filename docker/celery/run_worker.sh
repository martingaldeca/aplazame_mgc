#!/bin/bash

set -e
set -u
set -x

# Wait for services
dockerize -wait tcp://aplazame_postgres:5432 -timeout 30s
dockerize -wait tcp://rabbitmq:5672 -timeout 30s

LOGGING_ROOT_DIR="${LOGGING_ROOT_DIR:-.}"

# Share log files
chmod g+rw,o+rw -R ${LOGGING_ROOT_DIR}
chmod g+w,o+w -R /media
umask 000

# Celery config
# http://docs.celeryproject.org/en/latest/reference/celery.bin.worker.html
ARG_LOG_LEVEL="--loglevel=info"
CELERY_WORKER_ARGS="-E -Ofair $ARG_LOG_LEVEL --logfile='${LOGGING_ROOT_DIR}/%p.log'"
CELERY_WORKER_ARGS="$CELERY_WORKER_ARGS --time-limit 86400" # additional hard time limit (fallback), 3 days

if [ "${WORKER_QUEUES:-x}" != "x" ]; then
  CELERY_WORKER_ARGS="$CELERY_WORKER_ARGS -Q $WORKER_QUEUES"
fi
if [ "${WORKER_CONCURRENCY:-x}" != "x" ]; then
  CELERY_WORKER_ARGS="$CELERY_WORKER_ARGS --concurrency $WORKER_CONCURRENCY"
fi


echo "Starting worker '$WORKER_NAME'"
su -m celery -c "celery -A aplazame_mgc.celery worker -n $WORKER_NAME $CELERY_WORKER_ARGS"
