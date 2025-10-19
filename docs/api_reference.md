# GDPR Obfuscator — API Reference

Description:  
Quick reference of the main functions in the GDPR Obfuscator project.  
Intended for developers who want to integrate or test the module without opening the source code.  
Includes signatures, parameters, return values, common errors, and usage examples (local and S3).

---

## Functions

### run_pipeline
Signature: 
`run_pipeline(json_input: str) -> bool`

Description:  
Orchestrates the full ETL pipeline (Extract → Transform → Load).  
Accepts a serialized JSON string describing the input file and the fields to obfuscate.  
Works with local file paths or s3:// URIs.

Parameters:
- json_input (str, required) — JSON string containing:
  - `file_to_obfuscate` (str): local path or `s3://bucket/key.csv`  
  - `pii_field` (list[str], optional): list of columns to obfuscate

Returns: 
- (bool) — `True` on success, `False` on any failure.

Errors & Behaviour:
- Missing `file_to_obfuscate` key → logs KeyError and returns `False`.  
- If read handler returns `None` or empty DataFrame → logs error and returns `False`.  
- Exceptions are logged with no PII and pipeline returns `False`.

Examples:

S3 Example:
```python
import json
from src.main import run_pipeline

cfg = json.dumps({
    "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input.csv",
    "pii_field": ["email", "phone"]
})

run_pipeline(cfg)
```

Local Example:
```python
import json
from src.main import run_pipeline

cfg = json.dumps({
    "file_to_obfuscate": "data/input/sample_small.csv",
    "pii_field": ["email", "name"]
})
run_pipeline(cfg)
```

---

### build_output_key
Signature:  
`build_output_key(input_key: str, fields: List[str], ts: Optional[datetime] = None) -> str`

Description:  
Builds a descriptive output filename / S3 key including the obfuscated fields and a UTC timestamp.  
Preserves the path prefix if present.

Parameters:
- input_key (str, required) — Original filename or S3 object key (e.g. `data/in/file.csv`).  
- fields (List[str], required) — List of fields used to build the field part of the filename.  
- ts (datetime | None, optional) — Optional timestamp; if omitted, current UTC is used.

Returns:  
- (str) — Constructed filename/key, e.g.  
  `data/in/file_obf_fields-email-name_20251016T120000Z.csv`.

---

### read_csv_from_s3
Signature:
`read_csv_from_s3(json_input: str) -> Tuple[Optional[pd.DataFrame], List[str], Optional[str], Optional[str]]`

Description:  
Parses a JSON config, validates the `s3://` URI, downloads the object, and returns a pandas DataFrame.  
Also returns the list of fields to obfuscate (from JSON), the bucket name, and the object key.

Parameters:
- json_input (str, required) — JSON string with `file_to_obfuscate` (must start with `s3://`) and optional `pii_field` list.

Returns:
- df (pandas.DataFrame | None) — Loaded DataFrame or `None` if failed.  
- fields_to_obfuscate (List[str]) — Parsed list of fields (or []).  
- bucket_name (str | None)
- object_key (str | None)

Errors & Behaviour:
- Validates `s3://` prefix; raises/logs ValueError if invalid.  
- Catches botocore.ClientError and other exceptions; returns `(None, [], None, None)`.

Example:
```python
import json
from src.utils.s3_handler import read_csv_from_s3

cfg = json.dumps({
    "file_to_obfuscate": "s3://test-bucket/path/data.csv",
    "pii_field": ["email"]
})
df, fields, bucket, key = read_csv_from_s3(cfg)
```

---

### obfuscate_fields
Signature:
`obfuscate_fields(df: pd.DataFrame, fields_to_obfuscate: List[str]) -> pd.DataFrame`

Description: 
Replaces values of specified PII columns with a constant mask (`'***'`).  
Preserves NaN values and operates on a copy of the DataFrame (original is not mutated).

Parameters:
- df (pd.DataFrame, required) — Input DataFrame.  
- fields_to_obfuscate (List[str], required) — Columns to obfuscate.

Returns:  
- (pd.DataFrame) — New DataFrame with masked values in the specified columns.

Errors & Behaviour:
- If a column is missing, logs a warning and skips it.  
- Values are never logged to avoid PII leakage.

Example:
```python
from src.utils.obfuscator import obfuscate_fields
import pandas as pd

df = pd.DataFrame({"id":[1,2],"email":["user1@example.com", None], "name":["Alice","Bob"]})
df_obf = obfuscate_fields(df, ["email", "name"])
# df_obf["email"] -> ['***', NaN]
```

---

### write_csv_to_destination
Signature:  
`write_csv_to_destination(df: pd.DataFrame, output_path: str, bucket_name: Optional[str] = None) -> bool`

Description:  
Writes a DataFrame to disk or uploads to S3.  
If `bucket_name` is provided, the function uploads the CSV to that bucket using `output_path` as the key.

Parameters:
- df (pd.DataFrame, required) — DataFrame to write.  
- output_path (str, required) — Local path or S3 key for the output CSV.  
- bucket_name (str | None, optional) — If provided, upload to this S3 bucket.

Returns: 
- (bool) — `True` on success, `False` on failure.

Errors & Behaviour:
- Catches botocore.ClientError and general exceptions; logs the error and returns `False`.

Examples:

S3 Example:
```python
from src.utils.file_writer import write_csv_to_destination
success = write_csv_to_destination(df_obf, "outputs/obf.csv", bucket_name="my-bucket")
```

Local Example:
```python
write_csv_to_destination(df_obf, "data/output/sample_obf.csv")
```

---

### generate_full_dataset
Signature:  
`generate_full_dataset(output_path: str = 'data/input/sample_data.csv', extra_rows: int = 16000) -> Tuple[str, int]`

Description:  
Utility function that generates a synthetic CSV dataset for testing and demonstrations using Faker.

Parameters:
- output_path (str, optional) — Destination path for the generated CSV.  
- extra_rows (int, optional) — Number of random rows to append to base data.

Returns:
- output_path (str)
- total_rows (int)

Example:
```bash
python src/utils/data_generator.py
# creates data/input/sample_data.csv
```

---

## Testing

Description:  
Unit tests are implemented with pytest.  
S3 interactions are mocked using moto, so running the test suite does **not require real AWS resources**.

Commands:
```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html  # optional HTML report
```

CI:  
GitHub Actions workflow `.github/workflows/ci.yml` runs:
- Linters  
- Pre-commit hooks  
- Pytest on push/PR  

---

## Notes
- Do not include real PII in `data/input/`. Use synthetic examples only.  
- For pipelines/integrations (EventBridge, Step Functions, Lambda), use the same JSON format as `run_pipeline`.  
- If you change obfuscation logic, update tests in `tests/test_obfuscator.py` accordingly.  
- This is a code-level API reference (functions), not an HTTP API.

