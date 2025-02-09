#!/bin/bash
set -e

echo "Downloading models..."
python src/config/preparation.py

echo "Starting server..."
exec gunicorn main:app -c gunicorn.conf.py