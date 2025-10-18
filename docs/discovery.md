# Discovery — GDPR Obfuscator

## 1. Executive Summary
The purpose of this project is to deliver a reusable Python library capable of intercepting incoming data (CSV in S3 for MVP) and anonymizing fields containing Personally Identifiable Information (PII), enabling aggregate analysis without exposing individuals — complying with GDPR requirements from Northcoders.

## 2. Context
- Project for Skills Bootcamp / Data Engineering.
- Project datasets are intended for bulk analysis; any PII must be anonymized before storing outside the ingestion system.
- The final product will be a Python module that can be integrated into pipelines (Lambda, ECS, EC2, Step Functions, Airflow).

## 3. Objectives and Success Criteria
**Main Objective (MVP):**
- Provide a function/library that, given the S3 location of a CSV and the list of PII fields, returns a bytestream or equivalent file with PII values obfuscated, maintaining the original structure.

**Acceptance criteria (examples):**
- The module processes a CSV in S3 and returns a bytestream compatible with `boto3.put_object`.
- For files ≤ 1 MB, the complete execution (read → transform → write) takes < 60 seconds in the test environment.
- No credentials are stored in code.
- Unit tests with >90–95% coverage and use of mocks (`moto`) for S3.
- Logs do not contain PII.

## 4. Assumptions and Prerequisites
1. Input data in S3 in CSV format (MVP). Extensions: JSON and Parquet.
2. PII fields are known and supplied in the invocation.
3. Each record has a primary key (not obfuscated unless specified).
4. Initial execution environment: local tests with boto3 + moto; target deployment: AWS (Lambda, ECS, EC2).
5. Tools: Python 3.10+, pandas, boto3, pytest, moto, flake8, black, bandit.

## 5. Scope
### In-Scope (MVP)
- Read CSV from S3 (and optionally local for testing).
- Irreversible obfuscation (mask `***` by default) for indicated fields.
- Generate an output file with descriptive suffix preserving the original.
- API/library usable from Python; example CLI/main for demonstration.
- Unit tests with S3 mocks; PEP-8 and basic security checks (bandit).

### Out-of-Scope (MVP)
- Initial support for JSON / Parquet (possible extension).
- Orchestration in Step Functions / EventBridge (not required).
- Reversible encryption or advanced key management.
- Web interface or visualization.

## 6. User Stories (detailed)
> Each story includes: description, acceptance criteria,technical steps, sub-tasks priority, story points and check list.

### Epic E1 — Extract (S3)

### US 1.1 — Read CSV from S3
**Description:**  
As a developer, I want to retrieve a CSV file from S3 so that I can process and obfuscate PII fields.

**Acceptance Criteria:**
- The tool accepts a JSON input with S3 URI and field names.
- The file is retrieved as a bytestream (no local disk dependency).
- Errors are handled gracefully (e.g., file not found, access denied).

**Technical Steps:**
- Use boto3 to connect to S3 and download the file stream.
- Parse CSV into memory (e.g., pandas).

**Sub-tasks:**
- Implement S3 client wrapper  
- Parse JSON input  
- Error handling and logging  

**Priority:** `High`  
**Story Points:** `3`

**Checklist:**
- [ ] Works with CSV files up to 1MB  
- [ ] Raises clear error messages  


## Epic E2 – Transform (Obfuscation)

### US 2.1 — PII Obfuscation
**Description:**  
As a user, I want all specified PII fields to be obfuscated so that data cannot be used to identify individuals.

**Acceptance Criteria:**
- Fields listed in input JSON are replaced with obfuscated strings.
- Primary key field is preserved.
- Output structure matches input structure.

**Technical Steps:**
- Implement obfuscation function (masking, UUID, or hash).
- Apply transformation column-wise.

**Sub-tasks:**
- Write obfuscation logic  
- Ensure PK is excluded from obfuscation  
- Unit test transformation logic  

**Priority:** `High`  
**Story Points:** `5`

**Checklist:**
- [ ] All sensitive fields obfuscated  
- [ ] PK column unchanged  


## Epic E3 – Load (Output)

### US 3.1 — Generate Output File
**Description:**  
As a developer, I want the tool to return a valid CSV bytestream so that it can be uploaded back to S3 or consumed downstream.

**Acceptance Criteria:**
- Output is a valid CSV string/bytes object.
- Structure is identical to input (columns, order, delimiter).

**Technical Steps:**
- Convert modified DataFrame back to CSV bytestream.
- Ensure encoding consistency (UTF-8).

**Sub-tasks:**
- Implement CSV export to bytestream  
- Validate with sample inputs  

**Priority:** `High`  
**Story Points:** `3`

**Checklist:**
- [ ] Output passes CSV validation  
- [ ] No data corruption or column mismatch  


## Epic E4 – Quality, Documentation & CI/CD

### US 4.1 — Code Style and Standards
**Description:**  
As a developer, I want the code to follow PEP-8 so that it is readable and maintainable.

**Acceptance Criteria:**
- Code passes linting (flake8, black).
- No PEP-8 violations remain.

**Technical Steps:**
- Configure linting tools.
- Run automatically in CI.

**Sub-tasks:**
- Add config files  
- Run linters pre-commit and in CI  

**Priority:** `Medium`  
**Story Points:** `2`

**Checklist:**
- [ ] CI fails if style broken  
- [ ] Code formatted consistently  

### US 4.2 — Documentation
**Description:**  
As a developer, I want the project documented so that others can understand and use it easily.

**Acceptance Criteria:**
- README includes setup, usage, and examples.
- All functions have docstrings.

**Technical Steps:**
- Write README and docstrings.

**Sub-tasks:**
- Add README  
- Add docstrings  
- Add usage examples  

**Priority:** `Medium`  
**Story Points:** `3`

**Checklist:**
- [ ] README complete  
- [ ] Functions documented  

### US 4.3 — Testing
**Description:**  
As QA, I want automated unit tests so that I can ensure the tool works correctly.

**Acceptance Criteria:**
- ≥90% test coverage.
- Tests for S3 read, obfuscation, and output.

**Technical Steps:**
- Use pytest.
- Mock S3 with moto (or localstack).

**Sub-tasks:**
- Unit tests  
- Integration tests  
- Coverage report  

**Priority:** `High`  
**Story Points:** `5`

**Checklist:**
- [ ] All tests green  
- [ ] Coverage ≥90%  

### US 4.4 — Security Checks
**Description:**  
As a security officer, I want the code scanned for vulnerabilities so that sensitive data is handled securely.

**Acceptance Criteria:**
- Static analysis with bandit.
- No secrets hardcoded in code.

**Technical Steps:**
- Run Bandit.
- Add pre-commit hooks.

**Sub-tasks:**
- Security scan  
- Remove secrets  

**Priority:** `High`  
**Story Points:** `2`

**Checklist:**
- [ ] Bandit passes  
- [ ] No credentials in repo  


## Epic E5 – Performance

### US 5.1 — Handle Files up to 1MB
**Description:**  
As a user, I want the tool to process CSV files of up to 1MB in under 1 minute so that it runs within AWS Lambda constraints.

**Acceptance Criteria:**
- Test with 1MB CSV passes in <60s.

**Technical Steps:**
- Benchmark performance.
- Optimise memory usage.

**Sub-tasks:**
- Create test dataset  
- Measure performance  
- Optimise if needed  

**Priority:** `High`  
**Story Points:** `3`

**Checklist:**
- [ ] 1MB processed in <60s  
- [ ] Memory footprint acceptable  


## Epic E6 – Integration / End-to-End

### US 6.1 — Run Full Pipeline
**Description:**  
As a developer, I want to run the entire pipeline through a single entry point so that extract–transform–load steps execute sequentially.

**Acceptance Criteria:**
- `run_pipeline(json_input)` orchestrates E1–E3 steps correctly.
- Returns True/False and logs a summary message.
- Handles invalid JSON or missing fields gracefully.

**Technical Steps:**
- Implement `run_pipeline()` wrapper.
- Integrate extract, transform, load modules.
- Error handling and logging.

**Sub-tasks:**
- Pipeline orchestration  
- Exception handling  
- Unit and integration tests  

**Priority:** `High`  
**Story Points:** `3`

**Checklist:**
- [ ] Full pipeline runs successfully  
- [ ] Errors logged and handled  


## Epic E7 – Logging / Observability

### US 7.1 — Add Logging (No PII)
**Description:**  
As an engineer, I want to log meaningful pipeline events without exposing PII so that debugging and auditability are possible.

**Acceptance Criteria:**
- Logging uses Python logging module.
- No PII values appear in logs.
- Log level configurable (INFO/DEBUG).
- Logs include timestamps and step names.

**Technical Steps:**
- Configure logging setup.
- Add log messages in main functions.
- Sanitize sensitive data.

**Sub-tasks:**
- Logging configuration  
- Add safe log statements  
- Verify PII exclusion  

**Priority:** `Medium`  
**Story Points:** `2`

**Checklist:**
- [ ] Logs generated for key steps  
- [ ] No sensitive info recorded  

## 7. Example Input / Output (synthetic / safe)
### Expected JSON input
```json
{
  "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input.csv",
  "pii_field": ["email", "phone"],
}
``` 
### Input CSV (synthetic, small example)
```bash
id,name,email,age
1,Pablo Caldas,pablo@example.com,30
2,Jane Smith,jane.smith@example.com,25
```

### Output CSV (after obfuscation)
```bash
id,name,email,age
1,Pablo Caldas,***,30
2,Jane Smith,***,25
```
Note: Reproducible samples included in data/input/sample_small.csv and data/output/sample_obfuscated_example.csv (synthetic, non-PII).

## 8. Non-functional requirements

- Language/style: Python 3.10+, PEP-8 (black/flake8).
- Tests: pytest + moto for S3 mocks; coverage ≥ 90–95%.
- Security: bandit scan; no credentials in repo; logs without PII.
- Deployment: lightweight package suitable for AWS Lambda.
- Performance: ≤ 1 MB files processed < 60s; documented.
- Configuration: environment variables / ~/.aws/credentials for dev; no hard-coded secrets.

## 9. Risks and mitigations

- PII leakage in logs/commits: mitigation: .gitignore rules, manual review, logging tests, pre-commit hooks detecting sensitive patterns.
- Excessive dependencies (Lambda size): mitigation: essential libraries only; review final size.
- Insufficient S3 permissions: mitigation: document minimal IAM permissions (GetObject, PutObject).
- S3 URI parsing errors: mitigation: validations and unit tests.
- Collision/linkage (if reversible hash used): decision: default to irreversible mask to minimize linkage; document tradeoffs in design.md.

## 10. Dependencies and environment

- requirements.txt (minimum): boto3, pandas, pytest, moto, black, flake8, bandit, faker (optional for data generator).
- Recommended local setup: create virtualenv, pip install -r requirements.txt.
- AWS: awscli for manual tasks (not required if using moto in tests).

## 11. Definition of Done (DoD)

- Complete code for CSV processing from S3 (extract), obfuscate (transform), write to destination (load).
- Unit tests covering ≥ 90% relevant lines.
- Updated README.md with instructions.
- docs/design.md and docs/performance.md documented.
- CI on GitHub Actions executing tests, linters, and bandit.
- No credentials in repo; .gitignore updated.
- Code review and merge to main branch.