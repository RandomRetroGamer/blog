#!/bin/bash
set -e

python manage.py migrate --noinput
exec gunicorn campus_connect.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-1}" \
    --access-logfile - \
    --error-logfile -