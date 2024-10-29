import multiprocessing

pythonpath = "src"
bind = "0.0.0.0:3100"
workers = multiprocessing.cpu_count()  # * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
