
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 1000
timeout = 300
accesslog = "logs/api_access.log"
errorlog = "logs/api_error.log"
loglevel = "info"
preload_app = True
