#!/bin/sh
set -e

python manage.py migrate --noinput

echo "Startup complete"
exec gunicorn omarvip.wsgi:application --bind 0.0.0.0:$PORT
