"""Define the entry point to create the Celery application."""

from core import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
