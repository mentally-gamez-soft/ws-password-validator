"""Defines the models for the users module."""

import datetime

from core import db
from core.service.API_key_generator import create_sha256_signature


class User(db.Model):
    """Define the user model class."""

    __tablename__ = "app_user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=True)
    number_of_uses_for_token = db.Column(db.Integer, default=0, nullable=False)
    number_of_token_renewal = db.Column(db.Integer, default=0, nullable=False)
    last_date_token_renewed = db.Column(db.DateTime, nullable=True)

    is_authenticated: bool = False
    is_active: bool = False
    is_anonymous: bool = True

    def log_user_out(self):
        """Define the logout process for a user.

        Refer to flask-login https://flask-login.readthedocs.io/en/latest/#flask_login.logout_user
        """
        self.is_authenticated = False
        self.is_active = False
        self.is_anonymous = True

    def log_user_in(self):
        """Define the login process for a user.

        Refer to flask-login https://flask-login.readthedocs.io/en/latest/#your-user-class
        """
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self) -> str:
        """Define the method to log a user back in.

           Refer to flask-login https://flask-login.readthedocs.io/en/latest/#alternative-tokens

        Returns:
            str: The ID string that defines the user.
        """
        return self.token

    def __init__(self, email):
        """Declare constructor for User.

        Args:
            email (str): the email of a user
        """
        self.email = email

    def _make_timestamp_message(self, message: str):
        return "".join(
            [
                message,
                datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
            ]
        )

    def set_token(self, secret_key: str, message: str):
        """Set the token for a user.

        Args:
            secret_key (str): the APP secret key
            message (str): the message to encode
        """
        self.token = create_sha256_signature(
            secret_key, self._make_timestamp_message(message)
        )

    def reset_token(self, secret_key: str):
        """Reset the token for a user.

        Args:
            secret_key (str): the APP secret key
            message (str): the message to encode
        """
        self.token = self.set_token(secret_key, self.email)
        self.number_of_uses_for_token = 0
        self.number_of_token_renewal += 1
        self.last_date_token_renewed = datetime.datetime.utcnow()

    def check_token(self, api_key):
        """Control that a given password is correct.

        Args:
            token (str): the token to check.

        Returns:
            bool: True if the given password is the same as the stored one, False otherwise.
        """
        return self.token == api_key

    def save(self):
        """Save an instance of a user in the database."""
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """Set the representation of an instance of a user.

        Returns:
            str: An instance of a user.
        """
        return (
            f"<User {self.email}, is_login: {self.is_authenticated},"
            f" is_anonymous: {self.is_anonymous}, is_active: {self.is_active}>"
        )

    @staticmethod
    def get_by_id(id) -> "User":
        """Retrieve a user according to its ID.

        Args:
            id (int): the ID of a user.

        Returns:
            User: An instance of a user.
        """
        return User.query.get(id)

    @staticmethod
    def get_number_of_token_uses_by_id(id) -> int:
        """Retrieve the number of time a user identified by its ID has used his token API.

        Args:
            id (int): the ID of a user.

        Returns:
             int: The number of times the token API has been used.
        """
        return User.query.get(id).number_of_uses_for_token

    @staticmethod
    def get_by_email(email) -> "User":
        """Retrieve a user according to its email.

        Args:
            email (str): the email of a user.

        Returns:
            User: An instance of a user.
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_api_token(api_token) -> "User":
        """Retrieve a user according to its email.

        Args:
            api_token (str): the api_token of a user.

        Returns:
            User: An instance of a user.
        """
        return User.query.filter_by(token=api_token).first()

    @staticmethod
    def get_number_of_token_uses_by_email(email) -> int:
        """Retrieve the number of time a user identified by its email has used his token API.

        Args:
            email (str): the email of a user.

        Returns:
            int: The number of times the token API has been used.
        """
        return (
            User.query.filter_by(email=email).first().number_of_uses_for_token
        )

    @staticmethod
    def increment_number_of_use_for_token(token: str):
        """Increment the number of time a token API is used.

        Args:
            token (str): the token api of a user.
        """
        user = User.query.filter_by(token=token).first()
        user.number_of_uses_for_token += 1
        user.save()

    def increment_number_of_use_for_token(self: "User"):
        """Increment the number of time a token API is used.

        Args:
            self (User): The user for whom to update the token API key usage counter.
        """
        self.number_of_uses_for_token += 1
        self.save()

    @staticmethod
    def has_reached_usage_limit(token, max_usage_limit) -> bool:
        """Verify if a token API key can still be in use.

        Args:
            token (str): the API token key of a user.
            max_usage_limit (int): the maximum authorized usage of an API key token.

        Returns:
            bool: _description_
        """
        user: User = User.query.filter_by(token=token).first()
        if user:
            current_nb_of_use = user.number_of_uses_for_token
            user.increment_number_of_use_for_token()
            return current_nb_of_use >= max_usage_limit
        else:
            return True

    def delete(self):
        """Delete an instance of a user."""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def get_all():
        """Retrieve the list of all the users."""
        return User.query.all()
