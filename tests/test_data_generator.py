"""
test_data_generator.py
Tests for the data generator module.
Covers random row creation, ID sequencing, and CSV generation.
"""

import os
import pandas as pd
from src.utils.data_generator import generate_random_row, generate_full_dataset


def test_generate_random_row_basic():
    """Verifies that the correct number of random rows are generated with
    expected fields."""
    rows = generate_random_row(1, 5)
    assert len(rows) == 5
    first = rows[0]
    assert len(first) == 7
    assert isinstance(first[0], int)
    assert "@" in first[2]


def test_generate_random_row_increments_ids():
    """Ensures that row IDs increment sequentially starting from the given ID."""
    rows = generate_random_row(10, 3)
    ids = [r[0] for r in rows]
    assert ids == [10, 11, 12]


def test_generate_full_dataset_creates_file(tmp_path):
    """Checks that a CSV file is successfully created with the correct structure."""
    output_path = tmp_path / "data_output.csv"
    path, count = generate_full_dataset(str(output_path), extra_rows=5)
    assert os.path.exists(path)
    df_read = pd.read_csv(path)
    assert len(df_read) == count

    expected_cols = {
        "id",
        "name",
        "email",
        "age",
        "cohort",
        "graduation_date",
        "mode",
    }
    assert set(df_read.columns) == expected_cols


def test_generate_full_dataset_row_content(tmp_path):
    """Validates the content of the generated rows (id, email, age range)."""
    output_path = tmp_path / "data_output.csv"
    path, count = generate_full_dataset(str(output_path), extra_rows=3)
    df_read = pd.read_csv(path)
    assert df_read["id"].iloc[0] == 1
    assert "@" in df_read["email"].iloc[0]
    assert df_read["age"].between(22, 45).all()
