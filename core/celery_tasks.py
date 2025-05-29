"""Define in this module the async tasks that will be sent to Celery."""

import os

from celery import shared_task

from core.service.password_scoring import PasswordConfig


@shared_task
def multiple_password_scoring(passwords: list):
    """Analyze a list of passwords for scoring in async mode.

    Args:
        passwords (list): A list of passwords. The file could contain thousands of passwords.
    """
    password_scoring = PasswordConfig(
        has_digits=True,
        has_lowercase=True,
        has_spaces=False,
        has_symbols=True,
        has_uppercase=True,
        max_characters=50,
        min_characters=12,
        min_score=80,
    )
    for password in [p.decode("utf-8") for p in passwords]:
        result = password_scoring.validate_password(password)
        # if result["status"]:
        #    print("password => {}, scoring => {}".format(password, result["score"]))
