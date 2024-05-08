"""Define the api application."""

from flask import Blueprint, request

from core.service.password_scoring import PasswordConfig
from core.service.payload_validator import is_valid_payload

urls_blueprint = Blueprint("api_urls", __name__)


@urls_blueprint.route("/", methods=["GET"])
def default():
    """Define a test page to check the webservice status."""
    return "Welcome to this service for scoring a password.", 200


@urls_blueprint.route("/score", methods=["POST"])
def score():
    """Define the endpoint to the scoring password API.

    Returns:
        dict: The payload indicating the status and the score strength of the password.
    """
    try:
        data = request.json
        if not is_valid_payload(data):
            return {
                "message": "The input data is invalid!",
                "error": "Bad request.",
            }, 400

        password_scoring = PasswordConfig(
            has_digits=data.get("characteristics").get("has_digits"),
            has_lowercase=data.get("characteristics").get("has_lowercase"),
            has_spaces=data.get("characteristics").get("has_spaces"),
            has_symbols=data.get("characteristics").get("has_symbols"),
            has_uppercase=data.get("characteristics").get("has_uppercase"),
            max_characters=data.get("characteristics").get("max_length"),
            min_characters=data.get("characteristics").get("min_length"),
            min_score=data.get("min_accepted_score"),
        )
        return password_scoring.validate_password(data.get("password")), 200

    except Exception as e:
        return {"message": "Something went wrong!", "error": str(e)}, 500
