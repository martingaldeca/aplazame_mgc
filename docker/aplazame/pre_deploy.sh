#!/bin/sh

set -e
set -u
set -x

# Wait for DB
dockerize -wait tcp://aplazame_postgres:5432 -timeout 30s