# Design Document – GDPR Obfuscator

## 1. Purpose
This document defines the technical design and rationale behind the GDPR Obfuscator project.  
It builds upon the Discovery phase and explains the architecture, design choices, and implementation approach used to achieve compliance, testability, and maintainability.

---

## 2. High-Level Architecture
The GDPR Obfuscator is structured around a lightweight, modular pipeline:

1. **Input** – A CSV file located in AWS S3 or on a local path (for testing).  
2. **Process** – The system reads the file, identifies PII fields, and performs irreversible obfuscation.  
3. **Output** – A bytestream containing the anonymised data, suitable for S3 upload using `boto3`.

### Key Components
- **S3 Handler** – Manages secure download and upload of files from/to S3.
- **Obfuscator** – Performs field-level anonymisation.
- **File Writer** – Produces the output bytestream and manages naming/versioning.
- **Data Generator (Testing)** – Creates synthetic datasets for automated tests.
- **Main Script** – Entry point that orchestrates the process.

A diagram illustrating this data flow will be added to `docs/architecture_diagrams/`.

---

## 3. Design Approach

### Language & Libraries
- **Python 3.11**
- **pandas** for CSV manipulation and memory-safe DataFrame operations.
- **boto3** for AWS S3 interactions.
- **pytest**, **moto**, and **mock** for testing and mocking AWS services.

### Data Handling
- Files are processed using **DataFrame copies** to ensure the original dataset remains unaltered.  
- This approach provides auditability and allows test comparisons between raw and obfuscated data.

### Obfuscation Strategy
- **Method:** Masking PII fields with `'***'`.  
- **Rationale:**  
  - Fully irreversible (meets GDPR anonymisation standards).  
  - Readable and suitable for analytical use cases.  
  - Avoids unnecessarily long hashed strings.  
- Future versions may include hashing, pseudonymisation, or configurable field-level strategies.

### File Naming Convention
Output files follow the format:  
```bash
{prefix}/{base_name}obf_fields-{fields_part}{timestamp}.csv
```
This ensures:
- **Traceability** – timestamp and field indicators support audit logging.  
- **Safety** – prevents overwriting existing files.  
- **Compliance** – facilitates version tracking for GDPR audits.

---

## 4. Non-Functional Requirements

| Category | Requirement |
|-----------|--------------|
| **Performance** | Process ≤1 MB CSV in < 1 minute. |
| **Security** | No hardcoded credentials; use IAM roles or environment variables. |
| **Code Quality** | Compliant with PEP 8, includes docstrings and type hints. |
| **Deployment** | Package size < 250 MB to fit within AWS Lambda limits. |

---

## 5. Security Principles
- **Least privilege:** IAM roles restricted to read/write required buckets only.  
- **No credential storage:** `.gitignore` excludes `.env`, `.aws`, credentials, and cache files.  
- **No PII logs:** Obfuscated data only is logged.  
- **Code scanning:** Automated via Bandit in pre-commit hooks.

---

## 6. Testing & CI/CD

### Test-Driven Development
All modules were developed using **TDD**, ensuring that functionality is defined and verified through tests before implementation.

**Testing tools:**
- `pytest` for unit and integration tests.
- `moto` and `mock` to emulate AWS services (S3) locally.
- Synthetic CSV datasets generated for reproducibility.

### Continuous Integration (CI)
A **GitHub Actions** workflow automates validation across branches (`main`, `feature/`):

```yaml
name: CI

on:
  push:
    branches: [ main, feature, 'feature/**' ]
  pull_request:
    branches: [ main, feature, 'feature/**' ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install the dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest-cov

      - name: Ensure pre-commit is installed
        run: |
          python -m pip install pre-commit
          pre-commit --version

      - name: Run pre-commit hooks
        run: pre-commit run --all-files

      - name: Run tests with coverage
        run: |
          export PYTHONPATH=$PYTHONPATH:$(pwd)
          pytest --cov=src --cov-report=xml --cov-report=term
```
### Pre-Commit Hooks

- Black – Enforces consistent code formatting.
- Flake8 – Lints for style and syntax compliance.
- Bandit – Scans for security vulnerabilities.
---
## 7. Data Flow

- Input JSON specifies:

  - S3 location (or local path)
  - Fields to obfuscate

- The S3 handler retrieves the CSV file.
- The obfuscator processes the DataFrame, masking PII fields.
- The file writer creates a timestamped, obfuscated CSV.
- The anonymised data is returned as a bytestream.
- The orchestrator (e.g., Step Functions or Lambda) uploads the result back to S3.

## 8. Risks & Mitigations
| Risk                       | Mitigation                                                  |
| -------------------------- | ----------------------------------------------------------- |
| Large input files (> 1 MB) | Limit scope for MVP; future streaming-based implementation. |
| Reversible obfuscation     | Masking ensures irreversibility.                            |
| AWS costs                  | Use `moto` mocks and AWS free tier.                         |
| Code or style drift        | Pre-commit hooks enforce static checks.                     |

## 9. Open Decisions

- Extend support for JSON/Parquet formats in next iteration.
- Evaluate more complex anonymisation options (tokenisation, pseudonymisation).
- Refine logging and monitoring (structured JSON logs).