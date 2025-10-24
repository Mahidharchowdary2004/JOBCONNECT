#!/bin/bash
# Exit on error
set -e

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --verbosity=0

# Run migrations
python manage.py migrate --noinput