"""
file_writer.py
Writes a pandas DataFrame to a CSV file, either locally or in S3.
Handles both destinations safely, logging all outcomes.
"""

import logging
from io import StringIO
from typing import Optional
import boto3
import pandas as pd
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def write_csv_to_destination(
    df: pd.DataFrame, output_path: str, bucket_name: Optional[str] = None
) -> bool:
    """
    Writes the DataFrame to a destination (local or S3).

    Args:
        df (pd.DataFrame): DataFrame to save.
        output_path (str): File path or S3 key.
        bucket_name (Optional[str]): If provided, writes to S3.

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        if bucket_name:
            s3_client = boto3.client("s3")
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            # Upload CSV content stored in memory to S3
            s3_client.put_object(
                Bucket=bucket_name, Key=output_path, Body=csv_buffer.getvalue()
            )
            logger.info(
                "File successfully uploaded to s3://%s/%s",
                bucket_name,
                output_path,
            )
        else:
            df.to_csv(output_path, index=False)
            logger.info("File successfully saved locally at %s", output_path)
        return True
    except ClientError as e:
        logger.error("AWS Client error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    return False
