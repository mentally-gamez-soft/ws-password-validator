"""Define a set of tools to work with files."""

import gzip
import os
import shutil


def create_compressed_copy_of_file(
    path: str, filename: str, bucket_destination_name: str = None
) -> tuple:
    """Store a compressed gzip file on the system from an original file.

    Args:
        path (str): The path repos to this file.
        filename (str): The name of the file.
        bucket_destination_name (str, optional): In case of a storage to an S3 server, the symbolic name on the S3 repo is provided. Defaults to None.

    Returns:
        tuple: (The final symbolic name on the S3 repo, The full path and name to the file on the system)
    """
    with open(os.path.join(path, filename), "rb") as f_in:
        filename = "".join([filename, ".gz"])
        if bucket_destination_name:
            bucket_destination_name = "".join([bucket_destination_name, ".gz"])
        with gzip.open(os.path.join(path, filename), "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            f_out.close()
        f_in.close()

        return bucket_destination_name, os.path.join(path, filename)
