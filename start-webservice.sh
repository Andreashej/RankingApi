#!/bin/bash
source venv/bin/activate
flask db upgrade
exec gunicorn --worker-class eventlet -w 1 -b :5050 --access-logfile - --error-logfile - icecompass:application