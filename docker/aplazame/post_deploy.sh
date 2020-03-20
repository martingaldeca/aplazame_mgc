#! /bin/sh

# Set the default config for gunicorn
CONF_GUNICORN_TIMEOUT=900
CONF_GUNICORN_EXTRA_ARGS=''

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://aplazame_postgres:5432 -timeout 30s

umask 000 # setting broad permissions to share log volume

# Migrate models
python3 manage.py migrate --noinput

# Collect static files to serve them with nginx
python3 manage.py collectstatic --noinput -c

# Set the number of Django threads to use
num_threads=2

# Set auto-reload on source code
CONF_GUNICORN_EXTRA_ARGS="$CONF_GUNICORN_EXTRA_ARGS --reload"

# Start the gunicorn server
/usr/local/bin/gunicorn aplazame_mgc.wsgi:application --workers ${num_threads} --bind :3141 --timeout $CONF_GUNICORN_TIMEOUT $CONF_GUNICORN_EXTRA_ARGS

