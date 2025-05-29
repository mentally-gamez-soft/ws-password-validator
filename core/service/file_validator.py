"""Define the module for file extension validation."""

ALLOWED_EXTENSIONS = set(
    [
        "txt",
    ]
)


def expected_file(filename: str, allowed_extensions: list) -> bool:
    """Check that a file presents the expected extension.

    Args:
        filename (str): The name of the file.
        allowed_extensions (list): the list of extensions expected.

    Returns:
        bool: Returns true if the filename is correct. False otherwise.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )
