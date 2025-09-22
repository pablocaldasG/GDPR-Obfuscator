# Discovery Document – GDPR Obfuscator

## 1. Context
- Based on Tech Returners freelance brief.
- Goal: anonymise PII in datasets stored in AWS (CSV for MVP).
- Ensure GDPR compliance while allowing safe bulk data analysis.

## 2. Goals / Success Criteria
- Provide a reusable Python library to obfuscate sensitive fields.
- Work with AWS S3 files (CSV first).
- Produce anonymised output in < 1 min for files ≤ 1MB.
- Code must be unit tested, PEP-8 compliant, and documented.

## 3. Assumptions
- Input files stored in S3.
- Fields to obfuscate are known and provided in advance.
- Primary key exists in the dataset.
- Only CSV supported for MVP (JSON/Parquet for extensions).

## 4. Out of Scope
- Real deployment to production systems.
- Building full orchestration (Step Functions/EventBridge).
- Handling of datasets >1MB.

## 5. User Stories (high-level)
### Epic: Obfuscation Tool
- **US1**: As a developer, I want to provide an S3 path and fields so that I can obfuscate sensitive data in a CSV file.  
- **US2**: As a developer, I want to receive an anonymised bytestream so that I can save it elsewhere in S3.  
- **US3**: As a developer, I want the tool to handle missing/invalid fields gracefully so that it does not crash the pipeline.  

### Possible Extensions
- **US4**: As a data engineer, I want to process JSON/Parquet so that I can anonymise multiple formats.  
- **US5**: As a data engineer, I want configurable obfuscation (masking, hashing) so that I can adapt to business needs.  

## 6. Open Questions
- What specific obfuscation method should be used (masking, hashing, pseudonymisation)?  
- Should output file names include suffix/prefix (`_obfuscated`)?  
- Is there a preferred error handling/logging approach?  
- Should unit tests use real S3 (mocked with `moto`) or local files only?  

## 7. Risks
- Risk of leaking PII if .gitignore not properly configured.
- AWS costs if not careful with S3 usage (can be avoided with free tier + mocks).
- Time constraint (~40h for full project incl. docs + demo).

---
