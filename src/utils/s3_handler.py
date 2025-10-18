"""
s3_handler.py
Retrieves a CSV file from an S3 bucket based on JSON input.
"""

import json
import logging
import boto3
import pandas as pd
from io import StringIO
from typing import Tuple, List, Optional
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def read_csv_from_s3(
    json_input: str,
) -> Tuple[Optional[pd.DataFrame], List[str], Optional[str], Optional[str]]:
    """
    Reads a CSV file from S3 using parameters provided in a JSON string.

    Args:
        json_input (str): JSON string containing:
            {
                "file_to_obfuscate": "s3://my_ingestion_bucket/data/file1.csv",
                "pii_field": ["email", "phone"]
            }

    Returns:
        tuple:
            - pandas.DataFrame or None if failed
            - list of fields to obfuscate
    """
    try:
        # Parse the incoming JSON string to extract S3 URI and PII fields
        config = json.loads(json_input)
        s3_uri = config["file_to_obfuscate"]
        fields_to_obfuscate = config.get("pii_field", [])

        # Extract Bucket and key
        # Example: s3_uri = "s3://mybucket/data/file.csv"
        if not s3_uri.startswith("s3://"):
            raise ValueError(f"Invalid S3 URI: {s3_uri}")

        # Remove the "s3://" prefix → path = "mybucket/data/file.csv"
        _, path = s3_uri.split("s3://", 1)

        # Split path into bucket name and object key → ("mybucket", "data/file.csv")
        bucket_name, object_key = path.split("/", 1)

        # Create a boto3 S3 client and download the file contents
        s3_client = boto3.client("s3")
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        csv_content = response["Body"].read().decode("utf-8")

        # Load CSV into memory
        df = pd.read_csv(StringIO(csv_content))

        logger.info(
            "Successfully loaded '%s' from bucket '%s'",
            object_key,
            bucket_name,
        )
        return df, fields_to_obfuscate, bucket_name, object_key

    except ClientError as e:
        logger.error("AWS Client error: %s", e)
    except KeyError as e:
        logger.error("Missing key in JSON input: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)

    return None, [], None, None


if __name__ == "__main__":  # pragma: no cover
    # Example run for testing purposes
    test_json = json.dumps(
        {
            "file_to_obfuscate": "s3://gdpr-obfuscator-pablo-caldas/sample_input.csv",
            "pii_field": ["email", "phone"],
        }
    )

    df, fields = read_csv_from_s3(test_json)
    if df is not None:
        print(df.head())
