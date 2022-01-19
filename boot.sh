#!/bin/bash
echo "Running server..."
source venv/bin/activate
flask db upgrade
exec gunicorn -b :5050 --access-logfile - --error-logfile - icecompass:application