#!/bin/bash
echo python --version

# gunicorn app:app -c gunicorn.conf
# supervisord -n -c supervisord.conf
# supervisorctl update
# echo_supervisord_conf
python app.py