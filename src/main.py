"""
Main pipeline entrypoint for GDPR Obfuscator.

Behavior:
- Accepts a JSON input (string) containing "file_to_obfuscate" (s3://...)
 and "pii_field" (list).
- Reads the CSV (S3 or local), obfuscates the requested fields, and writes a new object
  to the same S3 bucket (or local path) with a descriptive suffix:
    <original_basename>_obf_fields-<fields>_<YYYYmmddTHHMMSSZ>.csv
- The original file is NOT modified.
- Returns True on success, False on failure.
"""

import json
import logging
import time
import pandas as pd
from datetime import datetime, timezone
from typing import List, Optional
from src.utils.s3_handler import read_csv_from_s3
from src.utils.obfuscator import obfuscate_fields
from src.utils.file_writer import write_csv_to_destination

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def build_output_key(
    input_key: str, fields: List[str], ts: Optional[datetime] = None
) -> str:
    """
    Build descriptive output key from input key and list of fields.
    Example:
      input_key = "data/in/file.csv"
      fields = ["email","name"]
      -> "data/in/file_obf_fields-email-name_20251016T120000Z.csv"
    """
    ts = datetime.now(timezone.utc)
    # Preserve path prefix if present
    if "/" in input_key:
        prefix, base = input_key.rsplit("/", 1)
        base_name = base.rsplit(".csv", 1)[0]
        fields_part = "-".join(sorted(fields)) if fields else "all"
        timestamp = ts.strftime("%Y%m%dT%H%M%SZ")
        return f"{prefix}/{base_name}_obf_fields-{fields_part}_{timestamp}.csv"
    else:
        base_name = input_key.rsplit(".csv", 1)[0]
        fields_part = "-".join(sorted(fields)) if fields else "all"
        timestamp = ts.strftime("%Y%m%dT%H%M%SZ")
        return f"{base_name}_obf_fields-{fields_part}_{timestamp}.csv"


def run_pipeline(json_input: str) -> bool:
    """
    Main pipeline runner.

    Args:
      json_input: JSON string containing at least "file_to_obfuscate" key
      and optional "pii_field".

    Returns:
      bool: True if the pipeline completed successfully, False otherwise.
      Logs all errors without exposing sensitive data.
    """
    try:
        json_data = json.loads(json_input)
        file_to_obfuscate = json_data["file_to_obfuscate"]
        # If the JSON contains pii_field it's used
        json_fields = json_data.get("pii_field", None)

        logger.info("Starting pipeline for: %s", file_to_obfuscate)
        start = time.perf_counter()

        # If s3 URI we use s3 handler to obtain df, fields, bucket and key
        if isinstance(file_to_obfuscate, str) and file_to_obfuscate.startswith("s3://"):
            df, fields_from_s3, bucket, key = read_csv_from_s3(json_input)

            fields = json_fields if json_fields is not None else fields_from_s3
        else:
            # Local file path
            df = pd.read_csv(file_to_obfuscate)
            bucket = None
            key = file_to_obfuscate
            fields = json_fields or []

        if df is None:
            logger.error(
                "No DataFrame returned from source handler; aborting pipeline."
            )
            return False

        if not fields:
            logger.warning(
                "No PII fields provided; nothing to obfuscate. Still writing copy."
            )
        else:
            logger.info("Obfuscating fields: %s", fields)

        if df.empty:
            logger.warning("DataFrame is empty, pipeline stopped.")
            return False

        # Transform
        df_obf = obfuscate_fields(df, fields)

        # Build output key/path
        output_key = build_output_key(key, fields)
        logger.info(
            "Output will be written to: %s (bucket=%s)",
            output_key,
            bucket or "local",
        )

        # Load
        success = write_csv_to_destination(df_obf, output_key, bucket_name=bucket)

        end = time.perf_counter()
        logger.info(
            "Pipeline finished in %.3f seconds (success=%s)",
            end - start,
            bool(success),
        )

        return bool(success)

    except KeyError as e:
        logger.error("Missing key in JSON input: %s", e)
    except Exception:
        logger.exception("Pipeline failed unexpectedly (PII not logged).")
    return False


if __name__ == "__main__":  # pragma: no cover
    # Example run for testing purposes
    example_json = json.dumps(
        {
            "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_data.csv",
            "pii_field": ["email", "name"],
        }
    )
    run_pipeline(example_json)
