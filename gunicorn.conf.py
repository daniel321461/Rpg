"""Railway/production Gunicorn settings."""
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = max(1, int(os.getenv("WEB_CONCURRENCY", "1")))
threads = 4
timeout = 180
accesslog = "-"
errorlog = "-"
