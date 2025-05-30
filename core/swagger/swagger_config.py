"""Configure the swagger documentation of the api."""

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger-conf/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "ws password validator",
        # "layout": "BaseLayout",
        # "docExpansion": "none",
    },
)


# @swaggerui_blueprint.route("/swagger")
# def swagger():
#     """Define the swagger docs url."""
#     with open("static/swagger/swagger.json", "r") as f:
#         return jsonify(json.load(f))
