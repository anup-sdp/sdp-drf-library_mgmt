#!/bin/bash

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (optional, can be done separately)
python manage.py migrate --noinput
