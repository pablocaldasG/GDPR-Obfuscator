"""
test_s3_handler.py

End-to-end tests for the S3 handler module using moto (AWS mock). Covers
successful reads, invalid input, and error handling for ClientError and
unexpected exceptions.
"""

import json
import boto3
import pandas as pd
from unittest.mock import patch
from botocore.exceptions import ClientError
from moto import mock_aws
from src.utils.s3_handler import read_csv_from_s3


# Tests: successful reads


@mock_aws
def test_read_csv_from_s3_returns_dataframe_bucket_name_object_key_and_fields():
    """S3 CSV is read successfully, returning DataFrame, bucket, key, and fields."""
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    csv_content = "email,phone,name\nuser@example.com,123456,Bob\n"
    s3.put_object(
        Bucket="test-bucket",
        Key="data/sample_input.csv",
        Body=csv_content.encode("utf-8"),
    )

    json_input = json.dumps(
        {
            "file_to_obfuscate": "s3://test-bucket/data/sample_input.csv",
            "pii_field": ["email", "phone"],
        }
    )

    df, fields, bucket_name, object_key = read_csv_from_s3(json_input)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["email", "phone", "name"]
    assert bucket_name == "test-bucket"
    assert object_key == "data/sample_input.csv"
    assert fields == ["email", "phone"]
    assert df.loc[0, "email"] == "user@example.com"


# Tests: invalid input


def test_invalid_json_returns_none_and_logs_error(caplog):
    """Invalid JSON input should return None and log an error."""
    invalid_json = '{"file_to_obfuscate": "s3://test-bucket/key.csv" '
    caplog.clear()

    df, fields, bucket_name, object_key = read_csv_from_s3(invalid_json)

    assert df is None
    assert fields == []
    assert bucket_name is None
    assert object_key is None
    assert "JSON decode" in caplog.text or "error" in caplog.text.lower()


def test_missing_file_to_obfuscate_key_returns_none_and_logs(caplog):
    """JSON missing 'file_to_obfuscate' should return None and log warning."""
    json_input = json.dumps({"pii_field": ["email", "phone"]})
    caplog.clear()

    df, fields, bucket_name, object_key = read_csv_from_s3(json_input)

    assert df is None
    assert fields == []
    assert bucket_name is None
    assert object_key is None
    assert "Missing key" in caplog.text


def test_invalid_s3_uri_returns_none_and_logs(caplog):
    """Non-S3 URI should return None and log invalid URI."""
    json_input = json.dumps(
        {
            "file_to_obfuscate": "local/file.csv",
            "pii_field": ["email", "phone"],
        }
    )
    caplog.clear()

    df, fields, bucket_name, object_key = read_csv_from_s3(json_input)

    assert df is None
    assert fields == []
    assert bucket_name is None
    assert object_key is None
    assert "Invalid S3 URI" in caplog.text


# Tests: error handling


def test_client_error_returns_none_and_logs(caplog):
    """S3 ClientError should return None and log AWS Client error."""
    json_input = json.dumps(
        {
            "file_to_obfuscate": "s3://bucket/key.csv",
            "pii_field": ["email", "phone"],
        }
    )
    caplog.clear()

    with patch("boto3.client") as mock_client:
        instance = mock_client.return_value
        instance.get_object.side_effect = ClientError(
            {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist.",
                }
            },
            "GetObject",
        )
        df, fields, bucket_name, object_key = read_csv_from_s3(json_input)

    assert df is None
    assert fields == []
    assert bucket_name is None
    assert object_key is None
    assert "AWS Client error" in caplog.text


@mock_aws
def test_unexpected_exception_returns_none_and_logs(caplog):
    """Unexpected exceptions should return None and log error."""
    s3 = boto3.client("s3", region_name="eu-west-2")
    s3.create_bucket(
        Bucket="test-bucket",
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )
    csv_content = "email,phone,name\nuser@example.com,123456,Bob\n"
    s3.put_object(
        Bucket="test-bucket",
        Key="data/sample.csv",
        Body=csv_content.encode("utf-8"),
    )

    json_input = json.dumps(
        {
            "file_to_obfuscate": "s3://test-bucket/data/sample.csv",
            "pii_field": ["email", "phone"],
        }
    )
    caplog.clear()

    with patch("pandas.read_csv", side_effect=Exception("Unexpected failure")):
        df, fields, bucket_name, object_key = read_csv_from_s3(json_input)

    assert df is None
    assert fields == []
    assert bucket_name is None
    assert object_key is None
    assert "unexpected error" in caplog.text.lower()
