#!/bin/bash

# shellcheck disable=SC2164
cd /run

rm /run/alembic/versions/*.py

current_date=$(date +"%Y-%m-%d %H:%M:%S")
alembic revision --autogenerate -m "revision generated on ${current_date}"
alembic upgrade head
