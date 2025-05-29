"""Define the module to initialize Celery in combination to the flask app."""

from celery import Celery, Task
from flask import Flask


def celery_init_app(app: Flask) -> Celery:
    """Initiate celery to work in conjunction to the flask app.

    Args:
        app (Flask): The flask application.

    Returns:
        Celery: The instance of Celery app.
    """

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
