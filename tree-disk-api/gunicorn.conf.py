import multiprocessing
import os

# Basic config
pythonpath = "src"
bind = "0.0.0.0:3100"
workers = multiprocessing.cpu_count()  # * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout config
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "120"))
keepalive = int(os.getenv("GUNICORN_KEEP_ALIVE", "5"))

# Production settings
preload_app = True  # Load application code before worker processes are forked
