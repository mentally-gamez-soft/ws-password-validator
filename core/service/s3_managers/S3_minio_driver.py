"""Define the concrete service S3 with Minio provider."""

import io
import logging
import os

from minio import Minio

from core.common.file_tools import create_compressed_copy_of_file
from core.service.s3_managers.S3_driver_interface import S3DriverInterface

logger = logging.getLogger(__name__)


class S3MinioDriver(S3DriverInterface):
    """Declare the object for this service."""

    def __init__(self, *args, **kwargs):
        """Declare the constructor for this concrete S3 service."""
        super().__init__(*args, **kwargs)

    def connect(
        self,
        hostname: str,
        port: str,
        user: str,
        password: str,
        *args,
        **kwargs
    ) -> dict:
        """Define the connection method to the S3 service.

        Args:
            hostname (str): the server host.
            port (str): the port for host.
            user (str): username for service.
            password (str): password to service access.

        Returns:
            dict: the status of type boolean and the session object.
        """
        self.session = Minio(
            ":".join(
                [
                    hostname,
                    port,
                ]
            ),
            user,
            password,
            secure=False,
        )
        return {"status": True, "session": self.session}

    def create_bucket(self, bucket_name: str, *args, **kwargs) -> bool:
        """Implement the method to create a bucket on s3 server.

        Returns:
            bool: the resulting status for this action.
        """
        found: bool = self.session.bucket_exists(bucket_name)
        if not found:
            self.session.make_bucket(bucket_name)  # Make bucket if not exist.
        else:
            logger.info(
                "The bucket {} is already existing.".format(bucket_name)
            )
        return True

    def upload_file_from_memory(
        self,
        filename: str,
        bucket_name: str,
        data,
        length,
        bucket_destination_path: str = None,
        *args,
        **kwargs
    ) -> bool:
        """Define a method to write on the s3 repo from bytes object in-memory.

        Args:
            filename (str): How to name the file on the S3 server.
            bucket_name (str): The bucket where to store the data.
            data (_type_): The bytes data to store.
            length (_type_): Specific to minio s£ service: The full length of the data must be known beforehand.
            bucket_destination_path (str, optional): If a sub-repo from the bucket should be given. Defaults to None.

        Returns:
            bool: _description_
        """
        if bucket_destination_path:
            filename = os.path.join(bucket_destination_path, filename)

        data = io.BytesIO(data)
        self.session.put_object(bucket_name, filename, data, length)
        return True

    def upload_file_from_disk(
        self,
        path: str,
        filename: str,
        bucket_name: str,
        bucket_destination_path: str = None,
        compress: bool = False,
        *args,
        **kwargs
    ) -> bool:
        """Define a method to write on the s3 repo from a file on the system.

        Args:
            path (str): The path directory in which the file is stored on the system.
            filename (str): the name of the file.
            bucket_name (str): The bucket where to store the data on the S3 service repo.
            bucket_destination_path (str, optional): If a sub-repo from the bucket should be given. Defaults to None.
            compress (bool, optional): Indicate if a compression of the data should be applied. Defaults to False.

        Returns:
            bool: Returns the status for the upload.
        """
        bucket_destination_name = filename
        if bucket_destination_path:
            bucket_destination_name = os.path.join(
                bucket_destination_path, filename
            )

        filename_with_path = os.path.join(path, filename)
        if os.path.isfile(filename_with_path):
            if compress:
                bucket_destination_name, filename_with_path = (
                    create_compressed_copy_of_file(
                        path, filename, bucket_destination_name
                    )
                )

            self.session.fput_object(
                bucket_name=bucket_name,
                object_name=bucket_destination_name,
                file_path=filename_with_path,
            )
            return True
        else:
            logger.info(
                "The file {} does not exist.".format(filename_with_path)
            )
            return False
