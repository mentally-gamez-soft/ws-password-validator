"""Declare the interface and the factory for any service using S3 repos."""

class S3DriverInterface:
    """Define the interface."""

    def __init__(self, *args, **kwargs):
        """Declare the base constructor for any object of this type."""
        self.session = None

    def connect(self, *args, **kwargs) -> dict:
        """Define the connection method that must implement any specific s3 service.

        Returns:
            dict: the status of type boolean and if the session object.
        """
        return {"status": True, "session": self.session}

    def create_bucket(self, *args, **kwargs) -> bool:
        """Implement the method to create a bucket on s3 server.

        Returns:
            bool: the resulting status for this action.
        """
        return True

    def upload_file_from_disk(self, *args, **kwargs) -> bool:
        """Define a method to write on the s3 repo from a file on the system.

        Returns:
            bool: the resulting status for this action.
        """
        return True

    def upload_file_from_memory(self, *args, **kwargs) -> bool:
        """Define a method to write on the s3 repo from bytes object in-memory.

        # https://stackoverflow.com/questions/52336902/what-is-the-difference-between-s3-client-upload-file-and-s3-client-upload-file

        Returns:
            bool: the resulting status for this action.
        """
        return True

    @classmethod
    def get_instance(cls, type_s3_manager: str):
        """Declare a factory method to create a concrete object of type service S3.

        Currently 2 concrete representation are existing: Minio S3 and AWS S3.

        Args:
            type_s3_manager (str): aws or minio

        Returns:
            S3MinioDriver | S3BotoDriver: An instance of the concrete object implementing this interface.
        """
        from core.service.s3_managers.S3_boto_driver import S3BotoDriver

        from .S3_minio_driver import S3MinioDriver

        if "minio" in type_s3_manager.lower():
            return S3MinioDriver()

        if "aws" in type_s3_manager.lower():
            return S3BotoDriver()
