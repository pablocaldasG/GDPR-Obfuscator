# GDPR Obfuscator Tool

![Python](https://img.shields.io/badge/python-3.10-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)

A Python-based ETL tool designed to anonymise Personally Identifiable Information (PII) in datasets stored on AWS S3 or locally, ensuring compliance with GDPR requirements.

This project was developed as part of the Tech Returners Skills Bootcamp in Data Engineering by Pablo Caldas.

## Project Overview
The GDPR Obfuscator acts as a modular data processing pipeline:

- Extract – Reads CSV data from AWS S3 or local storage.
- Transform – Obfuscates sensitive fields (email, phone, etc.) using configurable rules.
- Load – Writes the anonymised file back to S3 or to a local destination.

The tool is lightweight, modular, and suitable for deployment on AWS Lambda or other cloud-based environments.

---

## Features (MVP)
- Processes CSV files up to 1MB in less than one minute.
- Accepts JSON configuration specifying file location and PII fields.
- Reads/writes data from AWS S3 or local directories.
- Designed for AWS Lambda compatibility.
- Fully unit-tested, PEP8 compliant, and security-audited using flake8, black, and bandit.
- Integrated CI/CD pipeline for automated testing and code quality validation.

---

## Repository Structure
```bash
gdpr-obfuscator/
├── data/
│   ├── input/                     # Example input files
│   └── output/                    # Obfuscated output files
├── docs/
│   ├── api_reference/             # Functions parameters and usage examples
│   ├── architecture_diagrams/     # Visual architecture and data flow
│   ├── design.md                  # Technical design and implementation details
│   ├── discovery.md               # Problem definition and project context
│   ├── performance.md             # Performance metrics and benchmarks
│   ├── usage.md                   # Installation, setup, and usage guide
├── src/
│   ├── main.py                    # Main pipeline entry point
│   └── utils/
│       ├── data_generator.py      # Generates synthetic CSVs for testing
│       ├── file_writer.py         # Handles output writing to local or S3
│       ├── obfuscator.py          # Obfuscation logic
│       ├── s3_handler.py          # AWS S3 interaction (read/write)
│       └── __init__.py
├── tests/
│   ├── test_main.py
│   ├── test_obfuscator.py
│   ├── test_file_writer.py
│   ├── test_data_generator.py
│   ├── test_s3_handler.py
│   └── test_sample.py
├── requirements.txt
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
├── .gitignore
├── README.md
└── LICENSE
```
---
## Installation
### Prerequisites

- Python 3.10+
- AWS credentials configured locally via aws configure
- pip for package management

---
### Setup

Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/gdpr-obfuscator.git
cd gdpr-obfuscator
pip install -r requirements.txt

```

---
## Usage 
Example invocation of the main pipeline:
```bash
import json
from src.main import run_pipeline

example_json = json.dumps({
    "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input_1Mb.csv",
    "pii_field": ["email", "phone"]
})

run_pipeline(example_json)

```
The pipeline performs the following steps:

- Reads the file from AWS S3 or local storage.
- Obfuscates all specified PII fields.
- Writes the anonymised file to S3 or data/output/.

For local testing, you can execute the main script directly:
```bash
python src/main.py
```

---
## Testing

Unit tests are implemented using pytest.

Run tests with coverage:
```bash
pytest --cov=src --cov-report=term-missing

```
Generate an HTML report:
```bash
pytest --cov=src --cov-report=html
```

## CI/CD Pipelone

A GitHub Actions workflow is configured in .github/workflows/ci.yml.
It runs automatically on every push or pull request to the repository.

The pipeline performs the following steps:

- Install dependencies.
- Run Black for code formatting.
- Run Flake8 for PEP8 compliance.
- Run Bandit for security scanning.
- Execute Pytest for unit tests and coverage.

## Pre-commit Hooks

Pre-commit hooks ensure that code quality checks run before each commit.
Configured in .pre-commit-config.yaml to run:

- black – automatic code formatting
- flake8 – style and syntax validation
- bandit – security audit

Install and activate locally with:
```bash
pre-commit install
```
Run manually across all files with:
```bash
pre-commit run --all-files

```

## Documentation
Full documentation is included in the docs/ directory:
| Document                 | Description                                      |
| ------------------------ | ------------------------------------------------ |
| `discovery.md`           | Problem statement, assumptions, and objectives.  |
| `design.md`              | Technical architecture, modules, and data flow.  |
| `usage.md`               | Installation, configuration, and usage examples. |
| `performance.md`         | Runtime performance and file size testing.       |
| `architecture_diagrams/` | System architecture and data flow diagrams.      |
| `api_reference/`         | Functions parameters and usage examples.         |




## Future Extensions

- Add support for JSON and Parquet file formats.
- Implement configurable obfuscation strategies (masking, hashing, pseudonymisation).
- Develop a CLI interface for command-line invocation.
- Integrate with AWS Step Functions, EventBridge, or Airflow.
- Add parallelised obfuscation for larger datasets.


## Author
Developed by Pablo Caldas
Tech Returners – Skills Bootcamp in Data Engineering
2025

## License

This project is licensed under the MIT License (2025) – free for use, modification, and distribution with attribution.