"""Configure the swagger documentation of the api."""

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger-docs/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "ws password validator",
        "layout": "BaseLayout",
        # "docExpansion": "none",
    },
)
