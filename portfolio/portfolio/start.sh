#!/usr/bin/env bash
set -o errexit

cd backend
python manage.py migrate --noinput
python manage.py ensure_superuser
gunicorn portfolio_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}
