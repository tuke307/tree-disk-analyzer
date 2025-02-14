#!/bin/bash
set -e

echo "Downloading models..."
python -m src.config.preparation

echo "Starting server..."
exec gunicorn src.main:app -c gunicorn.conf.py