"""Launch the web application password scoring."""

from flask import Flask
from flask_cors import CORS

# Instantiate app, set attributes
app = Flask(__name__, static_url_path="/static")
app.json.compact = False

# Instantiate CORS
CORS(app)
