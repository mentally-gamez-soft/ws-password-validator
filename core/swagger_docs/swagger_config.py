"""Configure the swagger documentation of the api."""

import json

from flask import jsonify
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
# API_URL = 'http://192.168.0.20:6019/static/swagger.json'
API_URL = "http://localhost:5000/swagger"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    # f'http://127.0.0.1:5000/swagger',
    config={
        "app_name": "ws password validator",
        "layout": "BaseLayout",
        "docExpansion": "none",
    },
)


@swaggerui_blueprint.route("/swagger")
def swagger():
    """Define the swagger docs url."""
    with open("static/swagger/swagger.json", "r") as f:
        return jsonify(json.load(f))
