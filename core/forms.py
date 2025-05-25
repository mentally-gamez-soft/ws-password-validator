"""Define the forms for the app."""

from flask_wtf import FlaskForm
from wtforms import FileField


class UploadFileForm(FlaskForm):
    """Define the class for a form to upload a file."""

    file = FileField(name="file")
