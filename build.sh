#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

pip install face-recognition==1.3.0 --no-deps

python manage.py collectstatic --no-input

python manage.py migrate --no-input