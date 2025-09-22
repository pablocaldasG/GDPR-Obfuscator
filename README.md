# GDPR Obfuscator Tool

Work in Progress – This repository contains a Python-based obfuscation tool designed to anonymise Personally Identifiable Information (PII) in datasets, ensuring compliance with GDPR requirements.

## Project Overview
The purpose of this project is to provide a lightweight, modular library that can:
- Read input data (CSV at MVP stage, later JSON/Parquet).
- Detect and obfuscate fields containing sensitive data.
- Return an anonymised copy of the dataset, ready for further processing in an AWS-based data pipeline.

This project was developed as part of a **Tech Returners freelance opportunity** and aims to demonstrate skills in:
- **Python development** (PEP-8, testing, documentation).
- **Data engineering practices** (AWS S3, boto3).
- **Software delivery** (MVP, CI/CD, version control).

---

## Features (MVP)
- Input: CSV file stored in AWS S3.
- Input config: JSON string with S3 path and fields to obfuscate.
- Output: Bytestream with the same structure as input, but with obfuscated fields.
- Compatible with `boto3` and AWS Lambda memory limits.
- Unit-tested and security-reviewed (basic checks).

---

## Possible Extensions
- Support for JSON and Parquet input/output formats.
- Configurable obfuscation methods (masking, hashing, pseudonymisation).
- CLI interface for demonstration purposes.
- Integration with AWS Step Functions / EventBridge.

---

## Repository Structure
```bash
gdpr-obfuscator/
├── src/
│   └── obfuscator/       # Main Python package
│       ├── __init__.py
│       └── core.py
├── tests/                # Unit tests
│   └── test_core.py
├── data/                 # Sample data (synthetic, non-PII)
│   └── sample.csv
├── docs/                 # Documentation
│   ├── discovery.md
│   └── design.md
├── requirements.txt      # Dependencies
├── .gitignore
└── README.md
```
---
## Getting Started
### Prerequisites

- Python 3.10+
- AWS account (for S3 testing) or local mocks
- pip for package management

---
### Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/gdpr-obfuscator.git
cd gdpr-obfuscator
pip install -r requirements.txt
```

---
### Usage (MVP Example)
```bash
from obfuscator.core import obfuscate_csv

config = {
    "s3_path": "s3://your-bucket/input.csv",
    "fields": ["name", "email"]
}

output = obfuscate_csv(config)
# 'output' now contains a bytestream with obfuscated sensitive fields

```

---
## Testing

Tests are written using pytest. To run all tests:
```bash
pytest tests/
```
## Documentation

- Discovery – problem understanding, user stories, requirements.

- Design  – technical approach, MVP design, extensions.

## CI/CD

CI/CD will be integrated later using GitHub Actions for:

Unit testing

Linting (PEP-8)

Security checks

## License

This project is released under the MIT License.

## Author

Developed by Pablo Caldas as part of the Tech Returners freelance opportunity.
