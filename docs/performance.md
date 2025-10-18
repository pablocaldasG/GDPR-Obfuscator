# Performance Report – GDPR Obfuscator

## 1. Overview

This document summarises the performance testing conducted for the **GDPR Obfuscator** MVP.  
The goal was to confirm that the tool can process CSV files of up to **1 MB** within **less than 60 seconds**, as required by the project brief.  

Testing was performed manually (end-to-end) using both local and S3 environments, without automation, since the project scope does not require continuous benchmarking.

---

## 2. Test Environment

| Parameter | Details |
|------------|----------|
| **Location** | Local Linux virtual machine |
| **Python version** | 3.11 (same as used in CI/CD) |
| **Tools used** | `boto3`, `pandas`, `pytest`, `moto` |
| **Runtime method** | `python src/main.py` (end-to-end pipeline) |
| **AWS S3** | Real bucket used for testing (`gdpr-obfuscator-pablo-caldas`) |
| **Machine specs** | Standard virtual machine (no GPU, 4 GB RAM) |

---

## 3. Dataset Details

| Metric | Description |
|--------|--------------|
| **Input file** | `sample_data.csv` |
| **Rows** | ~16 000 |
| **Columns** | 7 (`id`, `name`, `email`, `age`, `cohort`, `graduation_date`, `mode`) |
| **PII fields obfuscated** | `["email", "name"]` |
| **Input size** | ~1.2 MB |
| **Output size** | ~0.9 MB (expected reduction due to masking) |
| **Obfuscation method** | Masking with `"XXXX"` (non-reversible, visually concise) |

---

## 4. Test Procedure

A full end-to-end run was executed using the command:

```bash
python src/main.py
```
Sample JSON input:
```json
{
  "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_data.csv",
  "pii_field": ["email", "name"]
}
```
During execution, timestamps were logged before and after each major stage.
---

## 5. Execution Log (Extract)
```bash
2025-10-18 19:06:27,079 [INFO] __main__: Starting pipeline for: s3://gdpr-obfuscator-pablo-caldas/sample_data.csv
2025-10-18 19:06:27,200 [INFO] botocore.credentials: Found credentials in shared credentials file: ~/.aws/credentials
2025-10-18 19:06:28,720 [INFO] src.utils.s3_handler: Successfully loaded 'sample_data.csv' from bucket 'gdpr-obfuscator-pablo-caldas'
2025-10-18 19:06:28,723 [INFO] __main__: Obfuscating fields: ['email', 'name']
2025-10-18 19:06:28,776 [INFO] src.utils.obfuscator: Obfuscated fields: ['email', 'name'] (mask applied, values not logged)
2025-10-18 19:06:28,776 [INFO] __main__: Output will be written to: sample_data_obf_fields-email-name_20251018T190628Z.csv (bucket=gdpr-obfuscator-pablo-caldas)
2025-10-18 19:06:29,384 [INFO] src.utils.file_writer: File successfully uploaded to s3://gdpr-obfuscator-pablo-caldas/sample_data_obf_fields-email-name_20251018T190628Z.csv
2025-10-18 19:06:29,386 [INFO] __main__: Pipeline finished in 2.306 seconds (success=True)
```
---
## 6. Results Summary
```bash
| Metric                              | Result                                                   |
| ----------------------------------- | -------------------------------------------------------- |
| **Total runtime (end-to-end)**      | **2.306 seconds**                                        |
| **File size processed**             | 1.2 MB                                                   |
| **Fields obfuscated**               | 2 (`email`, `name`)                                      |
| **Output file generated**           | `sample_data_obf_fields-email-name_20251018T190628Z.csv` |
| **S3 upload success**               | ✅ Yes                                                    |
| **Average runtime across 5–6 runs** | ~2–3 seconds                                             |
```
---
##  7. Interpretation

- Performance target achieved: 2.3 s ≪ 60 s.
- Scales well for MVP size (≤1 MB).
- No data corruption or column mismatch detected.
- No PII exposure in logs (field names only).
- Network-dependent: Actual runtime on AWS Lambda may vary depending on region and cold starts.
- Larger files (>1 MB) not currently supported; future versions can adopt chunked processing if needed.

---

## 8. Verification of Obfuscation

A manual verification was performed:

- Downloaded the output CSV from S3.
- Opened both files (input.csv and _obf_*.csv) in a spreadsheet.
- Confirmed that:

    - Only specified fields (email, name) were replaced with "***".
    - All other columns and data structure remained identical.
    - No extra whitespace, line breaks, or encoding issues occurred.

This ensures data integrity and confirms successful field-level masking.
---
## 9. Observations

- The difference in file size (~300 KB smaller) is expected due to fixed-length masking.
- Pandas `DataFrame.copy()` was used to preserve the original dataset before mutation.
- Processing is fully in-memory, efficient for the tested file sizes.
- Using `pandas` vectorised operations makes obfuscation near-instantaneous for typical datasets (<20 k rows).
---
## 10. Conclusions

- The tool meets and exceeds the non-functional performance requirement.
- The current architecture (S3 → Pandas → S3) is efficient for Lambda-scale workloads.
- Obfuscation is irreversible, ensuring GDPR compliance.
- No automation was needed for performance validation — manual timing and log review are sufficient for MVP verification.
