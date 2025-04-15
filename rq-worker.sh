#!/bin/bash

source venv/bin/activate

exec rq worker -u $REDIS_URL iceranking-tasks --with-scheduler