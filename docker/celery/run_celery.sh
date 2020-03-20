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
umask 000

# Celery CONFIGURATION with flower
# http://docs.celeryproject.org/en/latest/reference/celery.bin.worker.html
# http://docs.celeryproject.org/en/latest/reference/celery.bin.beat.html
ARG_LOG_LEVEL="--loglevel=info"
CELERY_BEAT_ARGS="$ARG_LOG_LEVEL --logfile='${LOGGING_ROOT_DIR}/celery_beat.log'"
CELERY_FLOWER_ARGS="--port=5555 --address=0.0.0.0 --url-prefix=flower $ARG_LOG_LEVEL --logfile='${LOGGING_ROOT_DIR}/flower.log'"
CELERY_FLOWER_ARGS="$CELERY_FLOWER_ARGS --max_tasks=500" # limit maximum number of tasks to keep in memory

# Celery run
rm -f celerybeat.pid
su -m celery -c "nice -n 5 celery beat -A django_project_config.uncelery  $CELERY_BEAT_ARGS" &

sleep 5
su -m celery -c "nice -n 5 celery flower -A django_project_config.uncelery --conf=aplazame_mgc/celery/flower_config.py $CELERY_FLOWER_ARGS" &

echo "## Wait for self services (sanity-check)"
dockerize -wait tcp://localhost:5555 -timeout 30s # flower
# ToDo: check beat
echo "## DEPLOY: SUCCESS ##"


# SIGTERM-handler + watchdog
PIDS_WATCHDOG="$(pgrep -d ' ' -f 'celery beat') $(pgrep -d ' ' -f 'celery flower')"
echo "Watchdog over PIDs: ${PIDS_WATCHDOG}"

term_handler() {
  echo "SIGTERM called"
  for pid in ${PIDS_WATCHDOG}; do
    kill -9 $pid || kill -15 $pid
  done
}
trap "term_handler" SIGTERM SIGINT

set +e
set +x
while true; do
  sleep 10
  for pid in ${PIDS_WATCHDOG} ; do
    ps -p $pid > /dev/null || (term_handler; exit 2)
  done
done
