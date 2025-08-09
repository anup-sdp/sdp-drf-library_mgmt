#!/usr/bin/env bash
set -euo pipefail

echo ">>> Installing requirements"
pip install -r requirements.txt

echo ">>> Running collectstatic"
python manage.py collectstatic --noinput

echo ">>> Copying collected static into public/static for Vercel"
# Create public/static and copy
mkdir -p public/static
# use cp -a to preserve structure; if cp fails for empty, continue
cp -a staticfiles/. public/static/ || true

echo ">>> Done build script"