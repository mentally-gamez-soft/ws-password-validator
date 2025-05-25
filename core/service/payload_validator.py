"""Validate the payload for the API."""

from functools import wraps

from core.service.email_validator import EmailValidator

PAYLOAD_TYPE_SCORING: str = "password_scoring"
PAYLOAD_TYPE_EMAIL: str = "email"


def has_characteristics(f):
    """Define a decorator to verify the existence of the key characteristics in the payload.

    Args:
        f (function): the call back function for this decorator.

    Returns:
        function | bool: Return False when the key is not present. Proceed to the callback function otherwise.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if not args[0].get("characteristics"):
            return False
        return f(*args, **kwargs)

    return decorated


def __is_payload_empty(payload: dict):
    return True if payload is None else False


def __has_password(payload: dict):
    return True if payload.get("password") else False


def __has_email(payload: dict):
    return True if payload.get("email") else False


@has_characteristics
def __has_min_length(payload: dict):
    return True if payload.get("characteristics").get("min_length") else False


@has_characteristics
def __has_max_length(payload: dict):
    return True if payload.get("characteristics").get("max_length") else False


@has_characteristics
def __has_uppercase(payload: dict):
    return (
        True
        if payload.get("characteristics").get("has_uppercase") is not None
        else False
    )


@has_characteristics
def __has_lowercase(payload: dict):
    return (
        True
        if payload.get("characteristics").get("has_lowercase") is not None
        else False
    )


@has_characteristics
def __has_digit(payload: dict):
    return (
        True
        if payload.get("characteristics").get("has_digits") is not None
        else False
    )


@has_characteristics
def __has_symbol(payload: dict):
    return (
        True
        if payload.get("characteristics").get("has_symbols") is not None
        else False
    )


@has_characteristics
def __has_space(payload: dict):
    return (
        True
        if payload.get("characteristics").get("has_spaces") is not None
        else False
    )


def __has_min_score(payload: dict):
    return True if payload.get("min_accepted_score") else False


def __is_valid_password_to_score(payload) -> bool:
    return (
        not __is_payload_empty(payload)
        and __has_password(payload)
        and __has_min_length(payload)
        and __has_max_length(payload)
        and __has_uppercase(payload)
        and __has_lowercase(payload)
        and __has_digit(payload)
        and __has_symbol(payload)
        and __has_space(payload)
        and __has_min_score(payload)
    )


def __is_valid_email(payload: dict) -> bool:
    return (
        not __is_payload_empty(payload)
        and __has_email(payload)
        and EmailValidator.is_valid_email(payload.get("email")).get("status")
    )


def is_valid_payload(payload_type: str, payload: dict):
    """Validate the input payload data.

    Args:
        payload_type (str): password_scoring or email
        payload (dict): The data input for this payload.

    Returns:
        bool: True if the payload format is valid.
    """
    if payload_type == PAYLOAD_TYPE_SCORING:
        return __is_valid_password_to_score(payload)
    elif payload_type == PAYLOAD_TYPE_EMAIL:
        return __is_valid_email(payload)
