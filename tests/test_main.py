"""
test_main.py
End-to-end tests for the GDPR Obfuscator pipeline.
Covers S3 and local scenarios, including success, failure, and edge cases.
"""

import json
import pandas as pd
import pytest
import logging
from unittest.mock import patch
from src.main import run_pipeline, build_output_key


# Fixtures


@pytest.fixture
def sample_json_s3():
    """Mock JSON input simulating an S3-based CSV file."""
    return json.dumps(
        {
            "file_to_obfuscate": "s3://test-bucket/sample_input.csv",
            "pii_field": ["email"],
        }
    )


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame used across tests to ensure consistent structure."""
    return pd.DataFrame(
        {
            "email": ["user1@example.com", "user2@example.com"],
            "name": ["Alice", "Bob"],
            "id": [1, 2],
        }
    )


@pytest.fixture
def sample_json_local(tmp_path, sample_dataframe):
    """Mock JSON input simulating a local CSV file."""
    csv_path = tmp_path / "input.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return json.dumps({"file_to_obfuscate": str(csv_path), "pii_field": ["email"]})


# Tests: main pipeline behaviour


def test_run_pipeline_s3_success(sample_json_s3, sample_dataframe):
    """Pipeline runs successfully when reading and writing from S3."""
    mock_bucket = "test-bucket"
    mock_key = "sample_input.csv"

    with patch(
        "src.main.read_csv_from_s3",
        return_value=(sample_dataframe, ["email"], mock_bucket, mock_key),
    ), patch("src.main.obfuscate_fields", return_value=sample_dataframe), patch(
        "src.main.write_csv_to_destination", return_value=True
    ) as mock_write:
        result = run_pipeline(sample_json_s3)
        assert result is True

        # Ensure the correct bucket and output key were used
        args, kwargs = mock_write.call_args
        assert kwargs["bucket_name"] == mock_bucket
        assert mock_key.split(".csv")[0] in args[1]


def test_run_pipeline_local_success(sample_json_local, sample_dataframe):
    """Pipeline runs successfully using a local CSV file."""

    with patch("src.main.pd.read_csv", return_value=sample_dataframe), patch(
        "src.main.obfuscate_fields", return_value=sample_dataframe
    ), patch("src.main.write_csv_to_destination", return_value=True) as mock_write:
        result = run_pipeline(sample_json_local)
        assert result is True

        args, kwargs = mock_write.call_args
        # Local runs don't use an S3 bucket
        assert kwargs["bucket_name"] is None


def test_run_pipeline_empty_dataframe(sample_json_s3):
    """Pipeline stops gracefully if DataFrame is empty."""
    empty_df = pd.DataFrame()
    mock_bucket = "test-bucket"
    mock_key = "sample_input.csv"

    with patch(
        "src.main.read_csv_from_s3",
        return_value=(empty_df, ["email"], mock_bucket, mock_key),
    ), patch("src.main.write_csv_to_destination", return_value=True) as mock_write:
        result = run_pipeline(sample_json_s3)
        assert result is False
        mock_write.assert_not_called()


def test_run_pipeline_none_dataframe(sample_json_s3):
    """Pipeline returns False if extractor returns None instead of a DataFrame."""
    mock_bucket = "test-bucket"
    mock_key = "sample_input.csv"

    with patch(
        "src.main.read_csv_from_s3",
        return_value=(None, ["email"], mock_bucket, mock_key),
    ), patch("src.main.write_csv_to_destination", return_value=True):
        result = run_pipeline(sample_json_s3)
        assert result is False


def test_run_pipeline_exception_in_read(sample_json_s3):
    """Pipeline handles unexpected exceptions from the extractor."""
    with patch(
        "src.main.read_csv_from_s3",
        side_effect=Exception("Unexpected exception"),
    ):
        result = run_pipeline(sample_json_s3)
        assert result is False


def test_run_pipeline_missing_key():
    """Pipeline returns False if input JSON lacks the required key."""
    invalid_json = json.dumps({"pii_field": ["email"]})
    result = run_pipeline(invalid_json)
    assert result is False


def test_run_pipeline_invalid_json():
    """Pipeline returns False when receiving malformed JSON input."""
    invalid_json = '{"file_to_obfuscate": "s3://bucket/key.csv"'
    result = run_pipeline(invalid_json)
    assert result is False


def test_run_pipeline_no_fields_provided(sample_json_s3, sample_dataframe):
    """Pipeline writes an unmodified copy when no PII fields are provided."""

    mock_bucket = "test-bucket"
    mock_key = "sample_input.csv"
    json_input = sample_json_s3

    with patch(
        "src.main.read_csv_from_s3",
        return_value=(sample_dataframe, [], mock_bucket, mock_key),
    ), patch(
        "src.main.obfuscate_fields", return_value=sample_dataframe
    ) as mock_obf, patch(
        "src.main.write_csv_to_destination", return_value=True
    ) as mock_write:
        result = run_pipeline(json_input)
        assert result is True
        mock_obf.assert_called_once()
        args, kwargs = mock_write.call_args
        assert kwargs["bucket_name"] == mock_bucket


def test_run_pipeline_exception_local(tmp_path, sample_json_s3):
    """Pipeline returns False if reading a local CSV raises an exception."""
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("email,phone,name\nuser@example.com,123456,Bob\n")
    json_input = sample_json_s3

    with patch("src.main.pd.read_csv", side_effect=Exception("fail")):
        result = run_pipeline(json_input)
        assert result is False


# Tests: build_output_key helper


def test_build_output_key_with_prefix():
    """Ensures build_output_key preserves folder prefixes and field names."""
    key = "data/input/file.csv"
    fields = ["email", "name"]
    output_key = build_output_key(key, fields)
    assert "_obf_fields-email-name" in output_key
    assert output_key.endswith(".csv")
    assert output_key.startswith("data/input/")


def test_build_output_key_simple_file():
    """Ensures build_output_key works correctly for simple filenames."""
    key = "file.csv"
    fields = ["phone"]
    output_key = build_output_key(key, fields)
    assert "_obf_fields-phone" in output_key
    assert output_key.endswith(".csv")
    assert "/" not in output_key


def test_run_pipeline_no_fields_provided_triggers_warning(caplog, sample_dataframe):
    """When no PII fields are provided (neither in JSON nor from S3),
    the pipeline logs a warning and still writes a copy."""
    mock_bucket = "test-bucket"
    mock_key = "sample_input.csv"

    # JSON without pii_field key
    json_input_no_fields = json.dumps(
        {"file_to_obfuscate": "s3://test-bucket/sample_input.csv"}
    )

    with patch(
        "src.main.read_csv_from_s3",
        return_value=(sample_dataframe, [], mock_bucket, mock_key),
    ), patch(
        "src.main.obfuscate_fields", return_value=sample_dataframe
    ) as mock_obf, patch(
        "src.main.write_csv_to_destination", return_value=True
    ) as mock_write:
        caplog.set_level(logging.WARNING)
        result = run_pipeline(json_input_no_fields)

        # Pipeline should succeed (writes a copy) even if no fields
        assert result is True

        # obfuscate_fields should still be called (the function handles empty fields)
        mock_obf.assert_called_once_with(sample_dataframe, [])

        # write should have been called
        mock_write.assert_called_once()

        # The warning about no PII fields should be present in logs
        warnings = [r.message for r in caplog.records if r.levelno == logging.WARNING]
        assert any(
            "No PII fields provided; nothing to obfuscate. Still writing copy."
            in str(w)
            for w in warnings
        )
