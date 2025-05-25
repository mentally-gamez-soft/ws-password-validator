"""Define the module to hamdle the API Token creation."""

import binascii
import hashlib
import hmac


def create_sha256_signature(key: str, message: str) -> hmac.HMAC:
    """Genertae a SH256 from a secret key and specified message.

    Args:
        key (str): The secret key.
        message (str): The message to encode.

    Returns:
        hmac.HMAC: The Token API Key of the user.
    """
    byte_key = binascii.unhexlify(key)
    message = message.encode("UTF-8")
    return hmac.new(byte_key, message, hashlib.sha512).hexdigest().upper()
