"""Process the main algorithms for scoring a password."""

import enum
import logging

import enpass as ep
from password_validator import PasswordValidator

logger = logging.getLogger(__name__)

DEFAULT_MINIMUM_SCORE = 62


class ColorScore(enum.Enum):
    """Declare the enumaration for correspondance between a score and a color."""

    black = (0, DEFAULT_MINIMUM_SCORE)
    crimson = (DEFAULT_MINIMUM_SCORE, 85)
    coral = (85, 95)
    yellow = (95, 105)
    yellowgreen = (105, 115)
    lightgreen = (115, 155)
    lime = (155, 1000)

    @staticmethod
    def get_color_from_score(score: float) -> str:
        """Retrieve the color that binds to this scoring value.

        Args:
            score (float): The scoring value of a password.

        Returns:
            str: The color that represents this score.
        """
        l = [c.name for c in ColorScore if int(score) in range(*c.value)]
        return l[0]


class Singleton(type):
    """Define the signleton pattern.

    Args:
        type (_type_): Any kind of object that is inheriting from the metaclass Singleton

    Returns:
        _type_: a single instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Instanciate a singleton object.

        Returns:
            _type_: an instance of an object.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


class PasswordConfigSingleton(metaclass=Singleton):
    """Define a password validator object following the singleton pattern.

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    def __init__(self) -> None:
        """Instanciate a singleton object with default settings."""
        self.__schema = PasswordValidator()

        # Add properties to schema
        self.__schema.min(10).max(
            25
        ).has().uppercase().has().lowercase().has().digits().has().symbols().has().no().spaces()
        self.__min_entropy = 70

    def validate_password(self, password) -> dict:
        """Indicate if a password is well formatted and has a good strength scoring.

        Args:
            password (str): The password to know the strength.

        Returns:
            dict: The information relative to the password.
        """
        message_for_schema = ""
        message_for_entropy = ""
        status = True

        if not self.__schema.validate(password):
            message_for_schema = (
                "The password is not meeting the length and/or characters"
                " requirements !"
            )
            status = False

        if not ep.validate(ep.calc_entropy(password), self.__min_entropy):
            message_for_entropy = "The strength of the password is too low !"
            status = False

        return {
            "status": status,
            "status_for_schema": message_for_schema,
            "status_for_entropy": message_for_entropy,
        }

    @classmethod
    def get_instance(cls):
        """Return the unique instance of an object PasswordConfigSingleton.

        Returns:
            PasswordConfigSingleton: a unique instance of this object.
        """
        return PasswordConfigSingleton()


class PasswordConfig:
    """Define the validator for a password."""

    def __init__(
        self,
        min_characters: int = 10,
        max_characters: int = 40,
        has_uppercase: bool = True,
        has_lowercase: bool = True,
        has_digits: bool = True,
        has_symbols: bool = True,
        has_spaces: bool = False,
        min_score: int = DEFAULT_MINIMUM_SCORE,
    ) -> None:
        """Instanciate an object of type PasswordConfig.

        Args:
            min_characters (int, optional): The minimum characters length of the password. Defaults to 10.
            max_characters (int, optional): The maximum characters length of the password. Defaults to 40.
            has_uppercase (bool, optional): Indicates if a uppercased character is needed for this password. Defaults to True.
            has_lowercase (bool, optional): Indicates if a lowercased character is needed for this password. Defaults to True.
            has_digits (bool, optional): Indicates if a digit character is needed for this password. Defaults to True.
            has_symbols (bool, optional): Indicates if a symbol character is needed for this password. Defaults to True.
            has_spaces (bool, optional): Indicates if a space character is needed for this password. Defaults to False.
            min_score (int, optional): Determines if the calculated final score strength is sufficient or not. Defaults to 65.
        """
        self.__schema = PasswordValidator()
        self.__min_entropy = min_score

        if min_characters:
            self.__set_min_characters(min_characters)

        if max_characters:
            self.__set_max_characters(max_characters)

        self.__set_uppercase(has_uppercase)
        self.__set_lowercase(has_lowercase)
        self.__set_digits(has_digits)
        self.__set_symbols(has_symbols)
        self.__set_spaces(has_spaces)

    def __set_min_characters(self, min_characters: int):
        self.__schema.min(min_characters)

    def __set_max_characters(self, max_characters: int):
        self.__schema.max(max_characters)

    def __set_uppercase(self, has_uppercase: bool):
        if has_uppercase:
            self.__schema.has().uppercase()
        else:
            self.__schema.has().no().uppercase()

    def __set_lowercase(self, has_lowercase: bool):
        if has_lowercase:
            self.__schema.has().lowercase()
        else:
            self.__schema.has().no().lowercase()

    def __set_digits(self, has_digits: bool):
        if has_digits:
            self.__schema.has().digits()
        else:
            self.__schema.has().no().digits()

    def __set_symbols(self, has_symbols: bool):
        if has_symbols:
            self.__schema.has().symbols()
        else:
            self.__schema.has().no().symbols()

    def __set_spaces(self, has_spaces: bool):
        if has_spaces:
            self.__schema.has().spaces()
        else:
            self.__schema.has().no().spaces()

    def validate_password(self, password) -> dict:
        """Validate the password in length, format and strength.

        Args:
            password (str): The password to score.

        Returns:
            dict: The payload with the information for this password.
        """
        message_for_schema = "Your password is valid."
        message_for_entropy = "Your password is strong enough."
        status = True
        score = ep.calc_entropy(password)

        if not self.__schema.validate(password):
            message_for_schema = (
                "The password is not meeting the length and/or characters"
                " requirements!"
            )
            status = False

        if not ep.validate(score, self.__min_entropy):
            message_for_entropy = "The strength of the password is too low!"
            status = False
        logger.info("Score: {}".format(score))
        return {
            "status": status,
            "score": score,
            "color": ColorScore.get_color_from_score(score),
            "message_password": message_for_schema,
            "message_score": message_for_entropy,
        }
