"""Define the concrete service S3 with amazon AWS provider."""

import gzip
import io
import logging
import os

import boto3

from core.common.file_tools import create_compressed_copy_of_file
from core.service.s3_managers.S3_driver_interface import S3DriverInterface

logger = logging.getLogger(__name__)


class S3BotoDriver(S3DriverInterface):
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
        self.session = boto3.client(
            "s3",
            endpoint_url="".join(["http://", hostname, ":", port]),
            aws_access_key_id=user,
            aws_secret_access_key=password,
            aws_session_token=None,
            config=boto3.session.Config(signature_version="s3v4"),
        )
        return {"status": True, "session": self.session}

    def create_bucket(self, bucket_name: str, *args, **kwargs) -> bool:
        """Implement the method to create a bucket on s3 server.

        Returns:
            bool: the resulting status for this action.
        """
        try:
            self.session.create_bucket(Bucket=bucket_name)
        except:
            logger.info(
                "The bucket {} is already existing.".format(bucket_name)
            )
        return True

    def upload_file_from_memory(
        self,
        filename: str,
        bucket_name: str,
        data,
        bucket_destination_path: str = None,
        compress: bool = False,
        *args,
        **kwargs
    ) -> bool:
        """Define a method to write on the s3 repo from bytes object in-memory.

        Args:
            filename (str): How to name the file on the S3 server.
            bucket_name (str): The bucket where to store the data.
            data (_type_): The bytes data to store.
            bucket_destination_path (str, optional): If a sub-repo from the bucket should be given. Defaults to None.
            compress (bool, optional): indicate if a compression of the data should be applied. Defaults to False.

        Returns:
            bool: Returns the status of the action.
        """
        if bucket_destination_path:
            filename = os.path.join(bucket_destination_path, filename)

        data = io.BytesIO(data)
        if compress:
            data = gzip.GzipFile(fileobj=data, mode="rb")
            filename = "".join([filename, ".gz"])
        self.session.upload_fileobj(data, bucket_name, filename)
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
            bucket_name (str):  The bucket where to store the data on the S3 service repo.
            bucket_destination_path (str, optional): If a sub-repo from the bucket should be given. Defaults to None.
            compress (bool, optional): Indicate if a compression of the data should be applied. Defaults to False.

        Returns:
            bool: Returns the status for the upload.
        """
        filename_with_path = os.path.join(path, filename)
        if os.path.isfile(filename_with_path):
            bucket_destination_name = filename
            if bucket_destination_path:
                bucket_destination_name = os.path.join(
                    bucket_destination_path, filename
                )

            if compress:
                bucket_destination_name, filename_with_path = (
                    create_compressed_copy_of_file(
                        path, filename, bucket_destination_name
                    )
                )

            self.session.upload_file(
                Filename=filename_with_path,
                Bucket=bucket_name,
                Key=bucket_destination_name,
            )
            return True
        else:
            logger.info(
                "The file {} does not exist.".format(filename_with_path)
            )
            return False
