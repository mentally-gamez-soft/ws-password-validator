"""Configure the swagger documentation of the api."""

import json

from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
# API_URL = 'http://127.0.0.1:5000/swagger.json'
API_URL = "/static/swagger-conf/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "ws password validator"}
)


@swaggerui_blueprint.route("/swagger.json")
def swagger():
    """Define the swagger docs url."""
    with open("swagger.json", "r") as f:
        return jsonify(json.load(f))
