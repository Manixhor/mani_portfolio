#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn portfolio_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}
