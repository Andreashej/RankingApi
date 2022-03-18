#!/bin/bash

source venv/bin/activate

exec rq worker -u redis://redis:6379/0 iceranking-tasks --with-scheduler