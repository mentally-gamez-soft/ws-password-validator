"""Declare the base test classfor the tests suit."""

import unittest

from faker import Faker

from core import create_app, db
from core.models import User
from core.service.password_scoring import DEFAULT_MINIMUM_SCORE


class BaseTestClass(unittest.TestCase):
    """Define the base test class."""

    def setUp(self):
        """Define the data set to create before each test."""
        self.app = create_app(BaseTestClass._setup_test_env())
        self.client = self.app.test_client()
        self.fake = Faker()

        self.has_digits: bool = True
        self.has_lowercase: bool = True
        self.has_uppercase: bool = True
        self.has_spaces: bool = False
        self.has_symbols: bool = True
        self.max_length: int = 40
        self.min_length: int = 10
        self.min_accepted_score: int = DEFAULT_MINIMUM_SCORE

        self.characteristics = {
            "characteristics": {
                "has_digits": self.has_digits,
                "has_lowercase": self.has_lowercase,
                "has_spaces": self.has_spaces,
                "has_symbols": self.has_symbols,
                "has_uppercase": self.has_uppercase,
                "max_length": self.max_length,
                "min_length": self.min_length,
            },
            "min_accepted_score": self.min_accepted_score,
        }
        with self.app.app_context():
            # Create the tables for the database
            db.create_all()
            # Create a fake user
            BaseTestClass.create_user(
                self.fake.email(), self.app.config["SECRET_KEY"]
            )

    def set_symbols(self, symbols: bool = True):
        """Define a utility function for testing the scoring of password.

        Set the presence or not of at least one special character in the password.

        Args:
            symbols (bool, optional): Declare the presence or not of at least one special character. Defaults to True.
        """
        self.has_symbols = symbols

    def set_spaces(self, spaces: bool = True):
        """Define a utility function for testing the scoring of password.

           Set the presence or not of at least one space character in the password.

        Args:
            spaces (bool, optional): Declare the presence or not of at least one space character. Defaults to True.
        """
        self.has_spaces = spaces

    def set_digits(self, digits: bool = True):
        """Define a utility function for testing the scoring of password.

           Set the presence or not of at least one digit character in the password.

        Args:
            digits (bool, optional): Declare the presence or not of at least one digit character. Defaults to True.
        """
        self.has_digits = digits

    def set_lowercase(self, lowercase: bool = True):
        """Define a utility function for testing the scoring of password.

           Set the presence or not of at least one lowercased character in the password.

        Args:
            lowercase (bool, optional): Declare the presence or not of at least one lowercased character. Defaults to True.
        """
        self.has_lowercase = lowercase

    def set_uppercase(self, uppercase: bool = True):
        """Define a utility function for testing the scoring of password.

           Set the presence or not of at least one uppercased character in the password.

        Args:
            uppercase (bool, optional): Declare the presence or not of at least one uppercased character. Defaults to True.
        """
        self.has_uppercase = uppercase

    def set_max_length(self, max_length: int = 8):
        """Define a utility function for testing the scoring of password.

           Set the maximum allowed length of the password.

        Args:
            max_length (int, optional): Set the maximum length of a password. Defaults to 8.
        """
        self.max_length = max_length

    def set_min_length(self, min_length: int = 8):
        """Define a utility function for testing the scoring of password.

           Set the minimum allowed length of the password.

        Args:
            min_length (int, optional): Set the minimum length of a password. Defaults to 8.
        """
        self.min_length = min_length

    def set_min_accepted_score(self, min_accepted_score: int = 80):
        """Define a utility function for testing the scoring of password.

           Set the minimum allowed calculated scoring for a password.

        Args:
            min_accepted_score (int, optional): Set the minimum allowed scoring of a password. Defaults to 8.
        """
        self.min_accepted_score = min_accepted_score

    def tearDown(self):
        """Destroy the data set after each test."""
        with self.app.app_context():
            # Delete the test database
            db.session.remove()
            db.drop_all()

    @staticmethod
    def create_user(email, secret):
        """Define an utility method to initiate the dataset.

        Args:
            email (str): the email of a user

        Returns:
            User: Returns an instance of a user
        """
        user = User(email)
        user.set_token(secret, email)
        user.save()
        return user

    @staticmethod
    def get_user() -> "User":
        """Define an utility method to get a user in the test database.

        Returns:
            User: Returns an instance of a user
        """
        return User.get_all()[0]

    @staticmethod
    def _setup_test_env() -> dict:
        configuration = dict()
        configuration["APP_ENV"] = "testing"
        configuration["DEBUG"] = True
        configuration["APP_ENV_LOCAL"] = "envir-local"
        configuration["APP_ENV_TESTING"] = "testing"
        configuration["APP_ENV_DEVELOPMENT"] = "envir-development"
        configuration["APP_ENV_PRODUCTION"] = "envir-production"
        configuration["APP_ENV_STAGING"] = "envir-preprod"
        configuration["HOSTNAME"] = "localhost"  # nosec B104
        configuration["APP_INCOMING_CONNECTIONS"] = "0.0.0.0"  # nosec B104
        configuration["APP_NAME"] = "My-API-TEST-SCORE-PASSWD"  # nosec B104
        import secrets

        configuration["SECRET_KEY"] = secrets.token_hex(16)
        configuration["APP_VERSION"] = "0.2.1j"
        configuration["TESTING"] = True
        configuration["WTF_CSRF_ENABLED"] = False
        configuration["CORS_ORIGINS_ROUTE_WELCOME"] = "*"
        configuration["CORS_ORIGINS_ROUTE_SCORING"] = (
            "http://server-test1.net http://server-test2.net"
        )
        configuration["LOG_PATH"] = "logs"
        configuration["LOG_FILENAME"] = "ws-password-scoring.log"

        configuration["S3_MINIO_BUCKET_NAME"] = "password-scoring-app-buckets"
        configuration["S3_MINIO_HOST"] = "localhost"
        configuration["S3_MINIO_USER"] = "s3-minio-user"  # nosec B105
        configuration["S3_MINIO_PASSWORD"] = "s3-minio-pass"  # nosec B105
        configuration["S3_MINIO_WEB_PORT"] = 9501  # nosec B105
        configuration["S3_MINIO_API_PORT"] = 9500

        configuration["ALLOWED_FILE_EXTENSIONS"] = "txt md pdf"
        configuration["MAX_FILE_SIZE"] = 30
        configuration["UPLOAD_FILES_FOLDER"] = "Uploads"

        configuration["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///api-password-scoring-testing.db"
        )
        configuration["API_MAX_USAGE_LIMIT"] = "20"

        return configuration
