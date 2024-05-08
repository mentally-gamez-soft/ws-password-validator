"""Validate the payload for the API."""

def __is_payload_empty(payload):
    return True if payload else False


def __has_password(payload):
    return True if payload.get("password") else False


def __has_min_length(payload):
    return True if payload.get("characteristics").get("min_length") else False


def __has_max_length(payload):
    return True if payload.get("characteristics").get("max_length") else False


def __has_uppercase(payload):
    return (
        True
        if payload.get("characteristics").get("has_uppercase") is not None
        else False
    )


def __has_lowercase(payload):
    return (
        True
        if payload.get("characteristics").get("has_lowercase") is not None
        else False
    )


def __has_digit(payload):
    return (
        True
        if payload.get("characteristics").get("has_digits") is not None
        else False
    )


def __has_symbol(payload):
    return (
        True
        if payload.get("characteristics").get("has_symbols") is not None
        else False
    )


def __has_space(payload):
    return (
        True
        if payload.get("characteristics").get("has_spaces") is not None
        else False
    )


def __has_min_score(payload):
    return True if payload.get("min_accepted_score") else False


def is_valid_payload(payload):
    """Validate the input payload data.

    Args:
        payload (dict): The data input for this payload.

    Returns:
        bool: True if the payload format is valid.
    """
    return (
        __is_payload_empty(payload)
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
