import os
from unittest import TestCase

from botocore.client import BaseClient
from minio.api import Minio

from core.service.s3_managers.S3_boto_driver import S3BotoDriver
from core.service.s3_managers.S3_driver_interface import S3DriverInterface
from core.service.s3_managers.S3_minio_driver import S3MinioDriver


class TestS3Service(TestCase):
    def setUp(self):
        self.driver = None
        self.bucket_name = "my-bucket"
        self.s3_server = "localhost"
        self.s3_server_port = "9500"
        self.s3_user = "minio-root-user"  # nosec B105
        self.s3_password = "minio-root-password"  # nosec B105

        current_dir = os.path.dirname(__file__)
        self.fixtures_dir = os.path.join(current_dir, "fixtures")
        self.file_minio = "test-upload-minio.txt"
        self.file_aws = "test-upload-aws.txt"

    def test_connection_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

    def test_create_new_bucket_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        result = self.driver.create_bucket(bucket_name=self.bucket_name)
        self.assertTrue(
            result,
            "The creation of the bucket with driver Minio did not work!",
        )

    def test_create_already_existing_bucket_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)
        result = self.driver.create_bucket(bucket_name=self.bucket_name)
        self.assertTrue(
            result,
            "The creation of the bucket with driver Minio did not work!",
        )

    def test_upload_existing_file_with_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename=self.file_minio,
            bucket_name=self.bucket_name,
        )
        self.assertTrue(result, "The upload to the s3 Minio failed!")

    def test_upload_existing_compressed_file_with_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename=self.file_minio,
            bucket_name=self.bucket_name,
            compress=True,
        )
        self.assertTrue(result, "The upload to the s3 Minio failed!")

    def test_upload_non_existing_file_with_s3_minio(self):
        self.driver = S3DriverInterface.get_instance("minio")
        self.assertTrue(
            self.driver is not None,
            "The connection to the minio driver failed.",
        )
        self.assertIsInstance(
            self.driver,
            S3MinioDriver,
            "The connection object is not of the expected S3MinioDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            Minio,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename="non-existing-file.txt",
            bucket_name=self.bucket_name,
            compress=True,
        )
        self.assertFalse(result, "The upload to the s3 Minio failed!")

    def test_connection_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

    def test_create_new_bucket_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        result = self.driver.create_bucket(bucket_name=self.bucket_name)
        self.assertTrue(
            result, "The creation of the bucket with driver AWS did not work!"
        )

    def test_create_already_existing_bucket_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)
        result = self.driver.create_bucket(bucket_name=self.bucket_name)
        self.assertTrue(
            result, "The creation of the bucket with driver AWS did not work!"
        )

    def test_upload_existing_file_with_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename=self.file_aws,
            bucket_name=self.bucket_name,
        )
        self.assertTrue(result, "The upload to the s3 AWS failed!")

    def test_upload_existing_compressed_file_with_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename=self.file_aws,
            bucket_name=self.bucket_name,
            compress=True,
        )
        self.assertTrue(result, "The upload to the s3 AWS failed!")

    def test_upload_non_existing_file_with_s3_aws(self):
        self.driver = S3DriverInterface.get_instance("aws")
        self.assertTrue(
            self.driver is not None, "The connection to the aws driver failed."
        )
        self.assertIsInstance(
            self.driver,
            S3BotoDriver,
            "The connection object is not of the expected S3BotoDriver type"
            " -> {}".format(type(self.driver)),
        )

        self.driver.connect(
            hostname=self.s3_server,
            port=self.s3_server_port,
            user=self.s3_user,
            password=self.s3_password,
        )
        self.assertIsNotNone(
            self.driver.session, "The session object is not initialized !"
        )
        self.assertIsInstance(
            self.driver.session,
            BaseClient,
            "The session object is not of the expected type -> {}".format(
                type(self.driver.session)
            ),
        )

        self.driver.create_bucket(bucket_name=self.bucket_name)

        result = self.driver.upload_file_from_disk(
            path=self.fixtures_dir,
            filename="non-existing-file.txt",
            bucket_name=self.bucket_name,
            compress=True,
        )
        self.assertFalse(result, "The upload to the s3 AWS failed!")
