# import multiprocessing
import os

# bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 1
accesslog = "-" # "/log/access.log"
errorlog = "-" # "/log/error.log"
loglevel = os.getenv("LOG_LEVEL", "info")  # default to 'info' if not set in .env
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(a)s" %(L)s'

keepalive = 120
timeout = 30



