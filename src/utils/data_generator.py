"""
data_generator.py
Generates synthetic student data with random attributes and saves it as a CSV file.
Used for testing and demonstration purposes.
"""

import pandas as pd
import random
from faker import Faker

fake = Faker()


def generate_random_row(id_start: int, num_rows: int):
    """
    Generates a list of random student records with fake data.

    Args:
        id_start (int): Starting ID for generated records.
        num_rows (int): Number of records to generate.

    Returns:
        list[list]: A list of rows, each containing:
            [id, name, email, age, cohort, graduation_date, mode].
    """
    rows = []
    cohorts = [
        "Data Engineering",
        "Web development",
        "Software Engineering",
        "Data Science",
        "Machine Learning",
    ]
    modes = ["Online", "In-person"]

    for i in range(id_start, id_start + num_rows):
        name = fake.name()
        email = fake.unique.email()
        age = random.randint(22, 45)
        cohort = random.choice(cohorts)
        graduation_date = fake.date_between(start_date="-3y", end_date="+2y").strftime(
            "%Y-%m-%d"
        )
        mode = random.choice(modes)
        rows.append([i, name, email, age, cohort, graduation_date, mode])
    return rows


def generate_full_dataset(
    output_path: str = "data/input/expanded_students_data_with_mode.csv",
    extra_rows: int = 16000,
):
    """
    Generates a complete dataset (base + random rows) and writes it to CSV.

    Args:
        output_path (str): Destination path for the generated CSV file.
        extra_rows (int): Number of additional randomly generated records.

    Returns:
        tuple[str, int]: Output path and total number of rows written.
    """
    base_data = [
        [
            1,
            "Pablo Caldas",
            "pablo@example.com",
            30,
            "Data Engineering",
            "2024-03-31",
            "Online",
        ],
        [
            2,
            "Jane Smith",
            "jane.smith@example.com",
            25,
            "Web development",
            "2024-03-31",
            "Online",
        ],
        [
            3,
            "Peter Aston",
            "peter@example.com",
            40,
            "Data Engineering",
            "2024-03-31",
            "Online",
        ],
    ]

    new_rows = generate_random_row(len(base_data) + 1, extra_rows)
    all_data = base_data + new_rows
    df = pd.DataFrame(
        all_data,
        columns=[
            "id",
            "name",
            "email",
            "age",
            "cohort",
            "graduation_date",
            "mode",
        ],
    )
    df.to_csv(output_path, index=False)
    return output_path, len(df)


if __name__ == "__main__":  # pragma: no cover
    path, n = generate_full_dataset()
    print(f"CSV file '{path}' generated successfully with {n} rows.")
