"""
test_obfuscator_mask.py
End-to-end tests for the obfuscator module.
Covers correct masking, NaN/None preservation, missing fields, and log safety.
"""

import pandas as pd
import logging
import pytest
from src.utils.obfuscator import obfuscate_fields, MASK_VALUE


# Fixtures


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


# Tests: obfuscation behaviour


def test_obfuscate_replaces_fields_with_mask(sample_df):
    """Non-null values in specified fields are replaced by the mask."""
    fields = ["email"]
    df_output = obfuscate_fields(sample_df, fields)

    # Mask applied only to 'email' column
    assert all(df_output["email"] == MASK_VALUE)
    # Other columns remain unchanged
    assert df_output["name"].tolist() == ["Alice", "Bob"]
    assert df_output["id"].tolist() == [1, 2]


def test_obfuscate_preserves_nan_and_none():
    """NaN and None values are preserved and not masked."""
    df = pd.DataFrame(
        {"email": ["user@example.com", None, float("nan")], "id": [1, 2, 3]}
    )
    df_output = obfuscate_fields(df, ["email"])

    assert df_output["email"].iloc[0] == MASK_VALUE
    assert pd.isna(df_output["email"].iloc[1])
    assert pd.isna(df_output["email"].iloc[2])


@pytest.mark.parametrize("value", ["123", 123, 12.34, True, False])
def test_mask_various_types(value):
    """Mask is applied to any non-null value regardless of type."""
    df = pd.DataFrame({"col": [value]})
    df_output = obfuscate_fields(df, ["col"])
    assert df_output["col"].iloc[0] == MASK_VALUE


def test_obfuscate_missing_field_warns_and_leaves_df_unchanged(caplog, sample_df):
    """Missing fields trigger a warning but do not modify the DataFrame."""
    caplog.clear()
    df_output = obfuscate_fields(sample_df, ["nonexistent_field"])

    assert df_output.equals(sample_df)

    # Log message should warn but not include PII
    logs = caplog.text.lower()
    assert ("not found" in logs) or ("skipping" in logs)


def test_output_columns_preserved(sample_df):
    """Column order and names are preserved after obfuscation."""
    df_output = obfuscate_fields(sample_df, ["email"])
    assert list(df_output.columns) == ["email", "name", "id"]


def test_no_pii_logged(caplog, sample_df):
    """Ensure obfuscation logs do not expose PII values."""
    caplog.set_level(logging.INFO, logger="src.utils.obfuscator")
    caplog.clear()

    _ = obfuscate_fields(sample_df, ["email"])
    logs = caplog.text.lower()

    # Original PII values must not appear in logs
    assert "user1@example.com" not in logs
    assert "user2@example.com" not in logs
    # Log can mention fields
    assert "obfuscated fields" in logs or "field" in logs
