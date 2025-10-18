# Usage Guide – GDPR Obfuscator Tool

This document explains how to install, configure, and run the **GDPR Obfuscator** tool locally and in AWS S3 environments.

---

## 1. Overview

The GDPR Obfuscator processes CSV files containing personally identifiable information (PII) and replaces the specified fields with obfuscated values.

It supports:
- **Local mode** – Reads and writes files on your machine (for testing and development).
- **S3 mode** – Reads input files from AWS S3 and writes the obfuscated output to the same or another S3 location.

The main entrypoint is the function `run_pipeline()` defined in `src/main.py`.

---

## 2. Prerequisites

Before running the tool, ensure the following:

- Python **3.10+**
- An AWS account (for S3 testing)
- AWS credentials configured using:

```bash
  aws configure

  All project dependencies installed:
``` 
```bash
  pip install -r requirements.txt

```
This will install core packages such as:

- boto3 (S3 integration).
- pandas (data handling).
- pytest / pytest-cov (testing and coverage).
- flake8, black, bandit (linting and security checks).

---
### 3.Input Configuration
The tool expects a JSON string containing two keys:
| Key                 | Type        | Required | Description                                                                                                    |
| ------------------- | ----------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| `file_to_obfuscate` | `str`       | Yes      | Path to the input CSV file. Can be local or S3 (e.g. `"data/input/sample.csv"` or `"s3://my-bucket/data.csv"`) |
| `pii_field`         | `list[str]` | Yes      | List of columns to obfuscate (e.g. `["email", "phone"]`)                                                       |

#### Example JSON
```bash
{
  "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input_1Mb.csv",
  "pii_field": ["email", "phone"]
}

```

---

### 4. Local Execution
You can run the tool locally by passing a JSON string to the `run_pipeline()` function.
#### Example Local File
```bash
import json
from src.main import run_pipeline

example_json = json.dumps({
    "file_to_obfuscate": "data/input/expanded_students_data_with_mode.csv",
    "pii_field": ["email", "phone"]
})

run_pipeline(example_json)
```
The tool will:

- Load the CSV from the given path.
- Obfuscate the requested columns.
- Save the output in data/output/ with a descriptive name, for example:
```bash
    data/output/expanded_students_data_with_mode_obf_fields-email-phone_20251016T120000Z.csv
```
---

### 5. AWS S3 Execution

When the `file_to_obfuscate` path starts with `s3://`, the pipeline automatically switches to S3 mode.

#### Example (S3 file):
```bash
import json
from src.main import run_pipeline

example_json = json.dumps({
    "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input_1Mb.csv",
    "pii_field": ["email", "phone"]
})

run_pipeline(example_json)

```
The tool will:

- Download the CSV from the given S3 path.
- Obfuscate the specified fields.
- Upload the obfuscated version to the same S3 bucket, with a generated key such as:
```bash
s3://gdpr-obfuscator-pablo-caldas/sample_input_1Mb_obf_fields-email-phone_20251016T120000Z.csv
```
---
### 6. Running from Terminal

To execute the pipeline manually from the command line (useful for testing):
```bash
python3 src/main.py
```
This will trigger the example JSON defined in main.py under:
```bash
if __name__ == "__main__":
```
---
### 7. Generating Test Data
You can generate synthetic CSVs for testing using the provided data generator:
```bash
python3 src/utils/data_generator.py 
```
This will create a file in data/input/ (for example sample_input_1Mb.csv) containing fake data suitable for local obfuscation testing.

---
### 8. Output Description

Each run of the pipeline creates a new file containing:

- The same number of rows and columns as the input.
- Obfuscated values for the fields specified in the configuration.
- A timestamped, descriptive filename.

Example:
```bash
sample_input_1Mb_obf_fields-email-phone_20251017T134500Z.csv

```
If no fields are specified, the tool will still copy the input file unchanged (useful for integration testing).

---
### 9. Running Tests

Run all unit tests with:
```bash
pytest --cov=src tests/
```
This will:

- Execute all test files in tests/
- Generate a coverage report
- Skip writing any real data to S3 (tests use the moto library to mock S3 operations)

### 10. Troubleshooting
| Issue                                   | Possible Cause                       | Solution                                  |
| --------------------------------------- | ------------------------------------ | ----------------------------------------- |
| `NoCredentialsError`                    | AWS credentials not found            | Run `aws configure`                       |
| `KeyError: 'file_to_obfuscate'`         | Invalid or malformed JSON input      | Ensure JSON keys are correct              |
| `Permission denied` when writing output | No write permissions on local folder | Run as admin or change folder permissions |
| Empty DataFrame logged                  | Input file path or format invalid    | Verify the file path and delimiter        |

---
### 11. Notes

- The original file is never modified.
- Logging is enabled by default for all pipeline stages.
- No PII is ever logged.
- The pipeline returns True on success and False on any failure.