#!/bin/bash
echo python3 --version

# gunicorn app:app -c gunicorn.conf
supervisord -n -c supervisord.conf
# supervisorctl update
# echo_supervisord_conf