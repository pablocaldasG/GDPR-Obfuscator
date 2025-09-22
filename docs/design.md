# Design Document – GDPR Obfuscator

## 1. Purpose
This document describes the technical design and approach for implementing the GDPR Obfuscator project.  
It builds upon the Discovery phase and outlines architecture, components, and technical choices.

---

## 2. High-Level Architecture
- **Input**: CSV file stored in S3.  
- **Process**: Python library reads file → identifies specified PII fields → obfuscates them → produces anonymised bytestream.  
- **Output**: Byte stream compatible with `boto3` S3 PutObject, ready to be saved back to S3.  

### Diagram (to add later)

---

## 3. Approach
- **Language**: Python 3.x  
- **Library**: `boto3` for S3 interactions.  
- **Obfuscation strategy**:  
  - MVP: Replace sensitive fields with masked strings (`XXXX`, hashed values, or UUIDs).  
  - Extension: Configurable obfuscation methods (masking, hashing, pseudonymisation).  

- **Error handling**:  
  - Log and skip invalid fields (do not crash pipeline).  
  - Ensure bytestream always returned, even if partial.  

- **Testing**:  
  - Unit tests with `pytest`.  
  - Mock AWS S3 using `moto`.  
  - Local test datasets with dummy data.  

---

## 4. Non-Functional Requirements
- **Performance**: ≤1MB files processed in <1 min.  
- **Security**:  
  - No credentials in code (use AWS IAM roles/env vars).  
  - `.gitignore` excludes `.env`, `.aws`, credentials, cache.  
- **Compliance**: PEP-8 style, type hints, docstrings.  
- **Deployment**: Must fit Lambda size limits (<250MB incl. deps).  

---

## 5. Data Flow (Detailed)
1. Receive JSON input with:  
   - S3 file location  
   - Fields to obfuscate  

2. Fetch file from S3 using `boto3`.  

3. Process CSV in memory with `pandas` or Python `csv` module.  

4. Obfuscate sensitive fields.  

5. Return anonymised file as bytestream.  

6. Calling service (Step Functions/Airflow/etc.) handles saving to destination.  

---

## 6. User Stories → Tasks Mapping
### US1 – Provide S3 path + fields → obfuscate CSV
- Task: Implement JSON input parser.  
- Task: Fetch CSV from S3.  
- Task: Obfuscate specified fields.  

### US2 – Return anonymised bytestream
- Task: Implement CSV → byte conversion.  
- Task: Validate output compatible with `boto3 PutObject`.  

### US3 – Handle invalid/missing fields gracefully
- Task: Add error handling & logging.  
- Task: Unit tests for edge cases.  

---

## 7. Risks & Mitigations
- **Large files** (>1MB): out of scope for MVP.  
- **Obfuscation reversibility**: ensure chosen method is non-reversible.  
- **AWS costs**: use mocks + free tier.  

---

## 8. Open Decisions
- Obfuscation method: Masking (`XXXX`) vs Hashing vs UUID.  
- File naming convention for outputs (`_obfuscated` suffix?).  
- Logging format/level.  

---

## 9. Next Steps
- Finalise obfuscation method with stakeholders.  
- Define directory structure in repo.  
- Start implementation branch `feature/obfuscator-core`.  

