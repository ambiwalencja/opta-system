# import multiprocessing
# import os

# 1. Server Socket
# Bind to 0.0.0.0 so it's accessible externally (important for Docker/Production)
# bind = "0.0.0.0:8000"

# 2. Worker Processes
# Use the Uvicorn worker class for FastAPI/ASGI support
worker_class = "uvicorn.workers.UvicornWorker"

# Calculate workers: (2 x small_number_of_cores) + 1 is a common formula
# For development, you might just hardcode this to 1 or 2.
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1

# 3. Logging
# '-' means log to stdout/stderr (the console)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Valid level names are:
# 'debug'
# 'info'
# 'warning'
# 'error'
# 'critical'

# 4. Process Management
keepalive = 120
timeout = 30

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(a)s" %(L)s'


# to samo w terminalu w komendzie:
# gunicorn main:app \
#   --workers 1 \
#   --worker-class uvicorn.workers.UvicornWorker \
#   --bind 0.0.0.0:8000 \
#   --access-log - \
#   --error-log - \
#   --log-level debug
