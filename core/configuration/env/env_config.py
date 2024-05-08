"""Configuration file for the application."""

import os
from io import StringIO
from os import environ as env
from pathlib import Path
from typing import Union, get_type_hints

import dotenv_vault.main as vault
from dotenv import load_dotenv as std_load_dotenv
from dotenv_vault import load_dotenv


class ConfigurationNotFoundException(Exception):
    """Raised when the configuration files of the application is not available."""

    pass


class EnvLoader:
    """Load the environment variables."""

    def __init__(self, env_path: str = ".") -> None:
        """Init the env variables.

        Args:
            env_path (str, optional): the path to the application .env file. Defaults to '.'.
        """
        self.app_env_path = env_path
        self.vault = vault
        self.env = env
        self.env["SIMULATION"] = "0"

    def __check_available_env(self) -> bool:
        if self.env["APP_ENV"] == "cicd_runner":
            return True

        if self.env["APP_ENV"] == "local.dev" and not os.path.exists(
            ".env.keys"
        ):
            raise ConfigurationNotFoundException(
                "The .env.keys file does not exists in local dev environment."
            )
        elif self.env["APP_ENV"] == "dev" and "DOTENV_KEY_DEV" not in self.env:
            raise ConfigurationNotFoundException(
                "The .env.keys file does not exists in environment."
            )
        elif (
            self.env["APP_ENV"] == "integ"
            and "DOTENV_KEY_STAGING" not in self.env
        ):
            raise ConfigurationNotFoundException(
                "The .env.keys file does not exists in environment."
            )
        elif (
            self.env["APP_ENV"] == "prod" and "DOTENV_KEY_PROD" not in self.env
        ):
            raise ConfigurationNotFoundException(
                "The .env.keys file does not exists in environment."
            )

    def __load_env(self) -> bool:
        """Load all the environment variables and the keys pass.

        Returns:
            bool: True if the environment variables are loaded, False otherwise
        """
        std_load_dotenv(os.path.join(self.app_env_path, ".env"))
        try:
            self.__check_available_env()
        except ConfigurationNotFoundException:
            return False

        if env["APP_ENV"] == "local.dev":
            return std_load_dotenv(".env.keys")
        else:
            return True

    def __load_env_key(self) -> str:
        """Load all the encrypted environment variables.

        Returns:
            str: The encrypted env variable
        """
        if self.env["APP_ENV"] in ("local.dev"):
            self.env["DOTENV_KEY"] = self.env.get("DOTENV_KEY_DEV")
            self.env["SIMULATION"] = "1"
        elif self.env["APP_ENV"] in ("dev"):
            self.env["DOTENV_KEY"] = self.env.get("DOTENV_KEY_DEV")
        elif self.env["APP_ENV"] == "integ":
            self.env["DOTENV_KEY"] = self.env.get("DOTENV_KEY_STAGING")
        elif self.env["APP_ENV"] == "prod":
            self.env["DOTENV_KEY"] = self.env.get("DOTENV_KEY_PROD")

        return self.env["DOTENV_KEY"]

    def __load_decyphered_env(self):
        if not std_load_dotenv(os.path.join(self.app_env_path, ".env.vault")):
            raise ConfigurationNotFoundException(
                "The .env.vault file does not exists"
            )

        try:
            dot_env_vault = None
            if self.env["APP_ENV"] in ("dev", "local.dev"):
                dot_env_vault = self.env["DOTENV_VAULT_DEV"]
            elif self.env["APP_ENV"] == "integ":
                dot_env_vault = self.env["DOTENV_VAULT_STAGING"]
            elif self.env["APP_ENV"] == "prod":
                dot_env_vault = self.env["DOTENV_VAULT_PROD"]

            if dot_env_vault is None:
                raise ConfigurationNotFoundException(
                    "The .env.vault file does not exists"
                )

            stream = self.vault.parse_vault(StringIO(dot_env_vault))
            load_dotenv(stream=stream, override=False)
        finally:
            os.unsetenv("DOTENV_KEY")

    def get_env_config(self, simulate_env: str = None):
        """Load the environment variables of the application."""
        if self.__load_env():
            if self.env["APP_ENV"] != "cicd_runner":
                self.__load_env_key()
                self.__load_decyphered_env()
        else:
            raise ConfigurationNotFoundException(
                "The .env.keys file does not exists"
            )

        if simulate_env:
            self.env["APP_ENV"] = simulate_env
            self.env["SIMULATION"] = "1"
            self.get_env_config()


class AppConfigError(Exception):
    """Raise an error of this type if the expected env variables are missing."""

    pass


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if type(val) is bool else val.lower() in ["true", "yes", "1"]


# AppConfig class with required fields, default values, type checking, and typecasting for int and bool values
class AppConfig:
    """Control that the environment variables are correctly configured for the application."""

    HOSTNAME: str
    APP_INCOMING_CONNECTIONS: str = "127.0.0.1"
    DOCKER_REGISTRY: str
    DEBUG: bool = False
    APP_ENV: str = "dev"

    def __init__(self, env):
        """
        Map environment variables to class fields according to these rules.

        - Field won't be parsed unless it has a type annotation
        - Field will be skipped if not in all caps
        - Class field and environment variable name are the same
        """
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise AppConfigError("The {} field is required".format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise AppConfigError(
                    'Unable to cast value of "{}" to type "{}" for "{}" field'
                    .format(env[field], var_type, field)
                )

    def __repr__(self):
        """Give the list of environment variables key with their values.

        Returns:
            dict: The key-value pair of environment variables for the application.
        """
        return str(self.__dict__)

    def get_application_env(self) -> dict:
        """Give the list of environment variables key with their values.

        Returns:
            dict: The key-value pair of environment variables for the application.
        """
        return self.__dict__
