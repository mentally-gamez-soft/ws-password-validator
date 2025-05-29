"""Configure the application with envs."""

import logging
import os
import sys
from logging import handlers

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from core.celery_init import celery_init_app
from core.configuration.env.env_config import load_env_variables

login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def register_blueprints(app):
    """Register all the blue prints of the entry points.

    Args:
        app (Flask): the flask app.

    Returns:
        app: the flask app.
    """
    # Register the blueprints
    from .api import api_bp

    app.register_blueprint(api_bp)


def logging_formatter():
    """Define the logger formatter for the output."""
    return logging.Formatter(
        "[%(asctime)s.%(msecs)d]\t %(levelname)s"
        " \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )


def configure_logging(app):
    """Configure the loggers for the application."""
    LOG_LEVEL_DEBUG = logging.DEBUG
    LOG_LEVEL_INFO = logging.INFO
    LOG_LEVEL = None
    LOG_MAX_BYTES = 1048576 * 1.5
    LOG_BACKUP_COUNT = 9

    # erase all existing loggers
    del app.logger.handlers[:]

    # Add the default logger
    loggers = [
        app.logger,
    ]
    handlers = []

    # -------------------------------------------------------------------
    # Creation of a handlers for the console
    # -------------------------------------------------------------------
    # -----------------  STD OUT handler --------------------------------
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(LOG_LEVEL_DEBUG)
    console_handler.setFormatter(logging_formatter())

    # -----------------  File handler -----------------------------------
    # Add file rotating handler, with level DEBUG
    file_rotating_handler = None
    if app.config["APP_ENV"] != app.config["APP_ENV_TESTING"]:
        file_rotating_handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(
                app.config.get("LOG_PATH"), app.config.get("LOG_FILENAME")
            ),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
        )
        file_rotating_handler.setLevel(LOG_LEVEL_DEBUG)
        file_rotating_handler.setFormatter(logging_formatter())

    # print(app.config)
    if app.config["APP_ENV"] in (
        app.config["APP_ENV_LOCAL"],
        app.config["APP_ENV_TESTING"],
        app.config["APP_ENV_DEVELOPMENT"],
    ):
        LOG_LEVEL = LOG_LEVEL_DEBUG
    elif app.config["APP_ENV"] in (
        app.config["APP_ENV_PRODUCTION"],
        app.config["APP_ENV_STAGING"],
    ):
        LOG_LEVEL = LOG_LEVEL_INFO

    console_handler.setLevel(LOG_LEVEL)
    handlers.append(console_handler)

    if file_rotating_handler:
        file_rotating_handler.setLevel(LOG_LEVEL)
        handlers.append(file_rotating_handler)

    # Bind each handlers to each loggers
    for l in loggers:
        for handler in handlers:
            l.addHandler(handler)
        l.propagate = False
        l.setLevel(LOG_LEVEL)


def create_app(test_config: dict = None) -> Flask:
    """Create the application.

    Returns:
        app: the flask application.
    """
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="static",
        instance_relative_config=True,
    )

    # read the configuration
    if test_config:
        config = test_config
    else:
        config = load_env_variables()
    app.config.from_mapping(config)
    app.config["CELERY"] = {
        "result_backend": app.config["CELERY_URL_RESULT"],
        "broker_url": app.config["CELERY_URL_BROKER"],
    }

    configure_logging(app)

    login_manager.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    celery_init_app(app)

    from core.api import ROUTE_INIT_SESSION_TOKEN

    csrf.exempt(ROUTE_INIT_SESSION_TOKEN)

    CORS(
        app,
        resources={
            r"/password-scoring/api/v1.0/score": {
                "origins": [
                    origin
                    for origin in app.config.get("CORS_ORIGINS_ROUTE_SCORING")
                ]
            },
            r"/password-scoring/api/v1.0": {
                "origins": [
                    origin
                    for origin in app.config.get("CORS_ORIGINS_ROUTE_WELCOME")
                ]
            },
        },
    )
    app.config["MAX_CONTENT_LENGTH"] = (
        int(app.config["MAX_FILE_SIZE"]) * 1000 * 1000
    )

    register_blueprints(app)

    app.json.compact = False

    return app
