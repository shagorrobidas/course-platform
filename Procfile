# Daphne ASGI server (for WebSockets & HTTP)
web: daphne -b 0.0.0.0 -p $PORT core.asgi:application

# Celery worker
worker: celery -A core worker -l info

# Celery beat scheduler
beat: celery -A core beat -l info
