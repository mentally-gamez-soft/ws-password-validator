"""Define the module to handle user authentication/login workflow."""

import base64
import logging

from core.models import User

logger = logging.getLogger(__name__)


def login_with_id(user_id: str) -> User | None:
    """Log a user in according to its ID string.

       Refer to flask-login  https://flask-login.readthedocs.io/en/latest/#alternative-tokens

    Args:
        user_id (str): The ID string to identify a user.

    Returns:
        User: Return an instance of the user having this ID string or None otherwise.
    """
    user = User.get_by_api_token(user_id)
    return user if user else None


def login_with_api_key_in_payload(request) -> dict:
    """Log in a user according to its token api key in the payload.

       Refer to flask-login https://flask-login.readthedocs.io/en/latest/#custom-login-using-request-loader

    Args:
        request (flask.request): The originating request to this endpoint.

    Returns:
        User: Return the user of the api token key if exists.
    """
    result = {}
    try:
        data = request.json
        api_key = data.get("api_key")
        if api_key:
            user = User.get_by_api_token(api_key)
            if user:
                logger.info("login user -> {}".format(user))
                result["user"] = user
                result["status"] = True
            else:
                result["status"] = False
    except Exception as e:
        result["status"] = False
        logger.error(
            "Exception when searching for the user through JSON: {}".format(e)
        )
    return result


def login_with_api_key_in_url_args(request):
    """Log in a user according to its token api key passed in the url as arg.

    Args:
        request (flask.request): The originating request to this endpoint.

    Returns:
        User: Return the user of the api token key if exists.
    """
    result = {}
    api_key = request.args.get("api_key")
    if api_key:
        user = User.query.filter_by(token=api_key).first()
        if user:
            logger.info("login user -> {}".format(user))
            result["user"] = user
            result["status"] = True
        else:
            result["status"] = False
    else:
        result["status"] = False
    return result


def login_with_basic_auth_header(request):
    """Log in a user according to its token api key passed in the headers as basic auth.

    Args:
        request (flask.request): The originating request to this endpoint.

    Returns:
        User: Return the user of the api token key if exists.
    """
    result = {}
    api_key = request.headers.get("Authorization")
    if api_key:
        api_key = api_key.replace("Basic ", "", 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(token=api_key).first()
        if user:
            logger.info("login user -> {}".format(user))
            result["user"] = user
            result["status"] = True
        else:
            result["status"] = False
    else:
        result["status"] = False
    return result
