"""Define the api application."""

import logging
import os
from functools import wraps

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_user
from flask_wtf.csrf import generate_csrf
from minio import Minio
from werkzeug.utils import secure_filename

from core import csrf, login_manager
from core.auth import (
    login_with_api_key_in_payload,
    login_with_api_key_in_url_args,
    login_with_basic_auth_header,
    login_with_id,
)
from core.celery_tasks import multiple_password_scoring
from core.forms import UploadFileForm
from core.models import User
from core.service.file_validator import expected_file
from core.service.password_scoring import PasswordConfig
from core.service.payload_validator import (
    PAYLOAD_TYPE_EMAIL,
    PAYLOAD_TYPE_SCORING,
    is_valid_payload,
)
from core.service.s3_managers.S3_driver_interface import S3DriverInterface

logger = logging.getLogger(__name__)

API_PREFIX: str = "/password-scoring/api"
# API_VERSION:str = "/{}".format(current_app.config.get("APP_VERSION"))
API_VERSION: str = "/v1.0"
ROUTE_WELCOME: str = "".join([API_PREFIX, API_VERSION])
ROUTE_INIT_SESSION_TOKEN: str = "".join([API_PREFIX, API_VERSION, "/login"])
ROUTE_RESET_SESSION_TOKEN: str = "".join(
    [API_PREFIX, API_VERSION, "/reset-token"]
)
ROUTE_PASSWORD_SCORING: str = "".join([API_PREFIX, API_VERSION, "/score"])
ROUTE_BULK_PASSWORD_SCORING: str = "".join(
    [API_PREFIX, API_VERSION, "/bulk-scores"]
)
ROUTE_S3_BULK_PASSWORD_SCORING: str = "".join(
    [API_PREFIX, API_VERSION, "/s3-bulk-scores"]
)

ROUTE_TEST_USE_API: str = "".join(
    [API_PREFIX, API_VERSION, "/test-count-use-api"]
)

api_bp = Blueprint("api_urls", __name__, template_folder="templates")


def token_usage_reached(f):
    """Define a decorator function to evaluate if the token api key has reached its limit.

    Args:
        f (function): the original function which called the decorator

    Returns:
        _type_: _description_
    """

    @wraps(f)
    def _decorated_function(*args, **kwargs):
        data = request.get_json()
        token = data.get("api_key", None)
        if not data or not token:
            return (
                jsonify(
                    {
                        "status": False,
                        "message": "The API key is missing!",
                        "api_key": token,
                    }
                ),
                401,
                {"API-TOKEN": token},
            )

        if token and not User.has_reached_usage_limit(
            token, int(current_app.config.get("API_MAX_USAGE_LIMIT"))
        ):
            return f(*args, **kwargs)
        else:
            return (
                jsonify(
                    {
                        "status": False,
                        "message": "The API key limit is reached!",
                        "api_key": token,
                    }
                ),
                401,
                {"API-TOKEN": token},
            )

    return _decorated_function


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Define the way for a user to be logged in again after leaving the web app.

       Refer to flask-login documentation https://flask-login.readthedocs.io/en/latest/#how-it-works

    Args:
        user_id (str): The string ID of a user.

    Returns:
        User: Return the logged in user of this ID or None if the ID does not match any user.
    """
    return login_with_id(user_id)


@login_manager.request_loader
def load_user_from_request(request) -> User | None:
    """Define the method for a user to get logged back in from a request after leaving the app.

       Refer to flask-login documentation https://flask-login.readthedocs.io/en/latest/#custom-login-using-request-loader

    Args:
        request (flask.request): The flask request originating

    Returns:
        User: Return the logged in user of this ID or None if the ID does not match any user.
    """
    load_result = None
    load_result = login_with_api_key_in_payload(
        request
    )  # first, try to login using the api_key passed in as payload
    if load_result["status"]:
        logger.info("User re-logged in - API key found in payload")
        return load_result["user"]

    load_result = login_with_api_key_in_url_args(
        request
    )  # next, try to login using the api_key url arg
    if load_result["status"]:
        logger.info("User re-logged in - API key found in url args")
        return load_result["user"]

    load_result = login_with_basic_auth_header(
        request
    )  # next, try to login using Basic Auth
    return load_result["user"] if load_result["status"] else None


@api_bp.route(ROUTE_WELCOME, methods=["GET"])
@api_bp.route(ROUTE_WELCOME + "/", methods=["GET"])
def default():
    """Define a test endpoint to check the webservice status."""
    logger.info(
        "Call of welcome endpoint - headers {}".format(request.headers)
    )
    logger.info("user -> {}".format(current_user))
    logger.info(
        "current user authenticated ? {}".format(current_user.is_authenticated)
    )

    return (
        jsonify(
            "Welcome to this service for scoring a password. (version {})"
            .format(API_VERSION)
        ),
        200,
        {
            "X-CSRFToken": generate_csrf(
                secret_key=current_app.config.get("SECRET_KEY")
            )
        },
    )


@csrf.exempt
@api_bp.route(ROUTE_PASSWORD_SCORING, methods=["POST"])
@token_usage_reached
def score():
    """Define the endpoint to the scoring password API.

    Returns:
        dict: The payload indicating the status and the score strength of the password.
    """
    logger.info(request)
    try:
        data = request.json
        if not is_valid_payload(PAYLOAD_TYPE_SCORING, data):
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
        return (
            jsonify(password_scoring.validate_password(data.get("password"))),
            200,
        )

    except Exception as e:
        logger.error("unknown exception here {}".format(e))
        return (
            jsonify({"message": "Something went wrong!", "error": str(e)}),
            500,
        )


def upload_file_to_s3(
    s3_bucket_name: str,
    file_path: str,
    file_name: str,
    file_data,
    file_size: int,
    s3_bucket_destination_name: str = None,
    from_memory: bool = False,
    driver: str = "minio",
    compress_data: bool = False,
):
    """Send a file to the S3 service.

    Args:
        s3_bucket_name (str): The destination bucket name for the file.
        file_path (str): In case of a file on the system: indicate the path to the file.
        file_name (str): In case of a file on the system: indicate the name of the file.
        file_data (_type_): the data to write into the file on the S3 repo.
        file_size (int): The size of the data to store (needed in case of a minio S3 provider).
        s3_bucket_destination_name (str, optional): Thje sub-repository(ies) in the destination bucket. Defaults to None.
        from_memory (bool, optional): Indicate if the file is in-memory (True), or on the file system (False). Defaults to False.
        driver (str, optional): Indicate the provider. Currently 2 possibilities aws or minio. Defaults to "minio".
        compress_data (bool, optional): Indicate if the data should be stored compressed or not. Defaults to False.
    """
    driverManager = S3DriverInterface.get_instance(driver)
    driverManager.connect(
        hostname=current_app.config.get("S3_MINIO_HOST"),
        port=current_app.config.get("S3_MINIO_API_PORT"),
        user=current_app.config.get("S3_MINIO_USER"),
        password=current_app.config.get("S3_MINIO_PASSWORD"),
    )
    driverManager.create_bucket(current_app.config.get("S3_MINIO_BUCKET_NAME"))
    if from_memory:
        driverManager.upload_file_from_memory(
            filename=file_name,
            bucket_name=s3_bucket_name,
            data=file_data,
            bucket_destination_path=s3_bucket_destination_name,
            compress=compress_data,
            length=file_size,
        )
    else:
        driverManager.upload_file_from_disk(
            path=file_path,
            filename=file_name,
            bucket_name=s3_bucket_name,
            bucket_destination_path=s3_bucket_destination_name,
            compress=compress_data,
        )


@api_bp.route(ROUTE_BULK_PASSWORD_SCORING, methods=["GET", "POST"])
def bulk_scores():
    """Define the endpoint to process and score multiple passwords passed through a file.

       The file will be stored in the filesystem of the server.

    Returns:
        response: a payload indicating that the file was processed in the case of a POST request. A redirect to the upload file form in case of a GET request.
    """
    logger.info(
        "Call bulk scores endpoint - headers {}".format(request.headers)
    )
    file_form = UploadFileForm()
    allowed_extensions = set(
        current_app.config.get("ALLOWED_FILE_EXTENSIONS").split(" ")
    )
    files_upload_directory = current_app.config["UPLOAD_FILES_FOLDER"]

    if request.method == "POST":
        if file_form.validate_on_submit():
            file = file_form.file
            file_data = file.data

            if file_data.filename == "":
                return (
                    jsonify(
                        {
                            "status": "OK",
                            "message": (
                                "Your file has been uploaded successfully."
                            ),
                        }
                    ),
                    200,
                )

            if file and expected_file(file_data.filename, allowed_extensions):
                filename = secure_filename(file_data.filename)

                if not os.path.isdir(files_upload_directory):
                    os.mkdir(files_upload_directory)

                l_passwords = file.raw_data[0].readlines()
                multiple_password_scoring.delay(
                    l_passwords
                )  # Pass the calculation of scores to the async celery task.
                file_data.save(os.path.join(files_upload_directory, filename))
                return (
                    jsonify(
                        {
                            "status": "OK",
                            "message": (
                                "Your file has been uploaded successfully."
                            ),
                        }
                    ),
                    200,
                )

    return render_template("file_upload.html", form=file_form)


@api_bp.route(ROUTE_S3_BULK_PASSWORD_SCORING, methods=["GET", "POST"])
def s3_bulk_scores():
    """Define the endpoint to process and score multiple passwords passed through a file.

       The file will be stored on a S3 minio server.

    Returns:
        response: a payload indicating that the file was processed in the case of a POST request. A redirect to the upload file form in case of a GET request.
    """
    logger.info(
        "Call S3 bulk scores endpoint - headers {}".format(request.headers)
    )
    file_form = UploadFileForm()
    allowed_extensions = set(
        current_app.config.get("ALLOWED_FILE_EXTENSIONS").split(" ")
    )

    if request.method == "POST":
        if file_form.validate_on_submit():
            file = file_form.file
            file_data = file.data
            l_passwords = file.raw_data[0].readlines()

            if file_data.filename == "":
                return (
                    jsonify(
                        {
                            "status": "OK",
                            "message": (
                                "Your file has been uploaded successfully."
                            ),
                        }
                    ),
                    200,
                )

            if file and expected_file(file_data.filename, allowed_extensions):
                filename = secure_filename(file_data.filename)
                size = os.fstat(file_data.fileno()).st_size
                upload_file_to_s3(
                    s3_bucket_name=current_app.config.get(
                        "S3_MINIO_BUCKET_NAME"
                    ),
                    file_path=None,
                    file_name=filename,
                    file_data=b"".join(l_passwords),
                    s3_bucket_destination_name=None,
                    from_memory=True,
                    driver="aws",  # "minio",
                    file_size=size,
                )

                multiple_password_scoring.delay(
                    l_passwords
                )  # Pass the calculation of scores to the async celery task.
                return (
                    jsonify(
                        {
                            "status": "OK",
                            "message": (
                                "Your file has been uploaded successfully."
                            ),
                        }
                    ),
                    200,
                )
    return render_template("file_upload.html", form=file_form)


@csrf.exempt
@api_bp.route(ROUTE_INIT_SESSION_TOKEN, methods=["POST"])
def init_session_token_of_user():
    """Define the endpoint for which a user will be able to open a session.

       The user must provide its email and an API Token key will be given back.

    Returns:
        response: a payload indicating the API token key of the user if the email was correctly input. An error otherwise.
    """
    logger.info(
        "Call init API token endpoint - headers {}".format(request.headers)
    )
    data: dict = request.json

    if not is_valid_payload(PAYLOAD_TYPE_EMAIL, data):
        return {
            "message": "The input data is invalid!",
            "error": "Bad request.",
        }, 400
    email = data.get("email")
    user = User.get_by_email(
        email
    )  # Verify that the user does not already exist
    if user:
        return (
            jsonify(
                {
                    "status": False,
                    "message": (
                        "A user with this email already exists. Try to renew"
                        " your API key."
                    ),
                }
            ),
            200,
        )
    else:
        user = User(email=email)
        user.set_token(
            secret_key=current_app.config.get("SECRET_KEY"), message=email
        )
        user.log_user_in()
        user.save()

    logged_in = login_user(user, remember=True, force=True)
    logger.info("The user {} logged in ? {}".format(user, logged_in))

    return (
        jsonify(
            {
                "status": True,
                "message": "Your API token has been created ",
                "api_key": user.token,
            }
        ),
        200,
        {"API-TOKEN": user.token},
    )


@csrf.exempt
@api_bp.route(ROUTE_RESET_SESSION_TOKEN, methods=["POST"])
def renew_token_for_user():
    """Define an endpoint for any already existing user to renew the token API key.

    Returns:
        response: a payload wit hthe renewed API Token key if the user exists. An error otherwise.
    """
    logger.info(
        "Call re-new API token endpoint - headers {}".format(request.headers)
    )
    data: dict = request.json

    token = data.get("api_key")
    if not token:
        return (
            jsonify({"status": False, "message": "The token is invalid."}),
            200,
        )
    else:
        user = User.get_by_api_token(token)
        user.reset_token(current_app.config.get("SECRET_KEY"))
        user.save()

        logged_in = login_user(user, remember=True, force=True)
        logger.info(
            "The user with id {} logged in ? {}".format(user.id, logged_in)
        )

    return (
        jsonify(
            {
                "status": True,
                "message": "Your API token has been reseted ",
                "api_key": user.token,
            }
        ),
        200,
        {"API-TOKEN": user.token},
    )


@csrf.exempt
@api_bp.route(ROUTE_TEST_USE_API, methods=["POST"])
@token_usage_reached
def test_use_api():
    """Define a sanity check endpoint for the increment and max usage of API token key.

    Returns:
        response: a payload with the API token key or an error message if the API token key reached its max usage.
    """
    logger.info(
        "Call sanity check usage for API token endpoint - headers {}".format(
            request.headers
        )
    )
    data: dict = request.json
    token = data.get("api_key")
    return (
        jsonify(
            {
                "status": True,
                "message": "The token use has been incremented",
                "api_key": token,
            }
        ),
        200,
        {"API-TOKEN": token},
    )
