#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd backend
python manage.py collectstatic --noinput
