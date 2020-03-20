#!/bin/bash

set -e
set +x

# Add group (500) to share volume permissions like the sftp
grep -q "^celerygroup:" /etc/group || groupadd -g 500 celerygroup

# Add plain user and assign ownership
id -u celery &>/dev/null || useradd celery -G 500
chown -R celery "/aplazame_mgc"

# Setting broad permissions to share log volume
umask 000

# Ready to apply commands
exec "$@"