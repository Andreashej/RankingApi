#!/usr/bin/env bash

RDS_USERNAME=iceapp
RDS_PASSWORD=YqJh1os3oMiu8fZ53p0N
RDS_HOSTNAME=iceranking-qa.c8fmxoomvwpn.eu-central-1.rds.amazonaws.com
RDS_DB_NAME=iceranking
FLASK_APP=/var/app/current/application.py

/var/app/venv/staging-LQM1lest/bin/flask db migrate