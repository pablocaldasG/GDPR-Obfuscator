"""
test_file_writer.py

End-to-end tests for the file_writer module. Covers saving DataFrames locally
and to S3, plus error handling for ClientError and unexpected exceptions.
"""


import pytest
import pandas as pd
from io import StringIO
from moto import mock_aws
from unittest.mock import patch
from botocore.exceptions import ClientError
import boto3
from src.utils.file_writer import write_csv_to_destination


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def sample_df():
    """Sample DataFrame used across tests to ensure consistent structure."""
    return pd.DataFrame(
        {
            "email": ["user1@example.com", "user2@example.com"],
            "name": ["Alice", "Bob"],
            "id": [1, 2],
        }
    )


@pytest.fixture
def s3_bucket():
    """Temporary S3 bucket using moto for testing."""
    with mock_aws():
        s3 = boto3.client("s3", region_name="eu-west-2")
        bucket_name = "test-bucket"
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        yield s3, bucket_name


# Tests: local file saves


def test_write_csv_local(tmp_path, sample_df):
    """Write DataFrame to local CSV and verify content."""
    file_path = tmp_path / "output.csv"
    success = write_csv_to_destination(sample_df, str(file_path))
    assert success
    df_read = pd.read_csv(file_path)
    assert df_read.equals(sample_df)


# Tests: S3 file saves


def test_write_csv_s3(s3_bucket, sample_df):
    """Write DataFrame to S3 and verify content."""
    s3, bucket_name = s3_bucket
    key = "folder/output.csv"

    success = write_csv_to_destination(sample_df, key, bucket_name=bucket_name)
    assert success

    # Verify object exists and content matches
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    df_read = pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))
    assert df_read.equals(sample_df)


# Tests: error handling


def test_write_csv_unexpected_exception_logs_and_returns_false(caplog, sample_df):
    """Unexpected exceptions should log error and return False."""
    with patch("boto3.client", side_effect=Exception("Unexpected failure")):
        caplog.clear()
        success = write_csv_to_destination(
            sample_df, "folder/output.csv", bucket_name="fake-bucket"
        )

    assert not success
    assert "Unexpected error:" in caplog.text


def test_write_csv_s3_client_error_logs_and_returns_false(caplog, sample_df):
    """S3 ClientError should log error and return False."""
    with patch("boto3.client") as mock_client:
        instance = mock_client.return_value
        instance.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "PutObject",
        )

        caplog.clear()
        success = write_csv_to_destination(
            sample_df, "folder/output.csv", bucket_name="fake-bucket"
        )

    assert not success
    assert "AWS Client error:" in caplog.text
