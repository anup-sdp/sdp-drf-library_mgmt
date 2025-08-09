#!/bin/bash

# Install requirements
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Move them to Vercel's public folder so they can be served
mkdir -p public/static
cp -r staticfiles/* public/static/