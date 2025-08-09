#!/usr/bin/env bash
set -euo pipefail

echo ">>> Python version:"
python --version || true

echo ">>> Pip version:"
pip --version || true

echo ">>> Installing requirements"
pip install -r requirements.txt

echo ">>> Running django checks"
python manage.py check

echo ">>> Running collectstatic"
python manage.py collectstatic --noinput

echo ">>> Copying static into public/static"
mkdir -p public/static
cp -a staticfiles/. public/static/ || true

echo ">>> Build script finished"
