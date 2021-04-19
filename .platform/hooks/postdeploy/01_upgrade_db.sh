#!/usr/bin/env bash

export RDS_USERNAME=iceapp
export RDS_PASSWORD=YqJh1os3oMiu8fZ53p0N
export RDS_HOSTNAME=iceranking-qa.c8fmxoomvwpn.eu-central-1.rds.amazonaws.com
export RDS_DB_NAME=iceranking
export FLASK_APP=application.py

cd /var/app/current
/var/app/venv/staging-LQM1lest/bin/flask db upgrade