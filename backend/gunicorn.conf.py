import os

bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:5001")

workers = int(os.environ.get("GUNICORN_WORKERS", 2))
worker_class = "gthread"
threads = 2

timeout = 30
graceful_timeout = 20
keepalive = 5

max_requests = 1000
max_requests_jitter = 150

preload_app = True

accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "warning")

pidfile = os.environ.get("GUNICORN_PID", "/tmp/horta-escolar.pid")
