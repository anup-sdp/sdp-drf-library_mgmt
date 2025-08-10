#!/usr/bin/env bash
set -euo pipefail
echo ">>> python --version"
python --version || true
echo ">>> pip --version"
pip --version || true

echo ">>> Installing requirements"
pip install -r requirements.txt

echo ">>> Running django checks"
python manage.py check || true

echo ">>> Collectstatic"
python manage.py collectstatic --noinput

echo ">>> Copying static to public/static"
mkdir -p public/static
cp -a staticfiles/. public/static/ || true

echo ">>> Listing public/static (first 50 entries)"
ls -la public/static | head -n 50 || true

echo ">>> Build script finished"
