"""Define th module to validate an email."""

from email_validator import EmailNotValidError, validate_email


class EmailValidator:
    """Declare the email validator class."""

    @staticmethod
    def is_valid_email(email: str) -> dict:
        """Indicate if an email is valid.

        Args:
            email (str): the email to verify.

        Returns:
            dict: a dictionary indicating the status [True/False], a message and the standardized email to use.
        """
        if email is None:
            return {"status": False, "message": "", "email": ""}

        try:
            emailinfo = validate_email(email, check_deliverability=True)
            return {
                "status": True,
                "message": "",
                "email": emailinfo.normalized,
            }

        except EmailNotValidError as e:
            return {"status": False, "message": str(e), "email": ""}
