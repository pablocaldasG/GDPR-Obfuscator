"""
obfuscator.py
Transforms sensitive fields in a DataFrame using a mask.
"""

import pandas as pd
import logging
from typing import List

logger = logging.getLogger(__name__)

MASK_VALUE = "***"


def obfuscate_fields(df: pd.DataFrame, fields_to_obfuscate: List[str]) -> pd.DataFrame:
    """
    Obfuscate the given fields in a DataFrame by replacing their values with a mask.

    Args:
        df (pd.DataFrame): Input DataFrame to process.
        fields_to_obfuscate (List[str]): List of field names to mask.

    Returns:
        pd.DataFrame: A copy of the DataFrame with masked fields.
    """
    df_copy = df.copy()

    for field in fields_to_obfuscate:
        if field not in df_copy.columns:
            logger.warning("Field '%s' not found in DataFrame; skipping.", field)
            continue

        # Replace non-null value with mask; preserve NaN
        # Use vectorized .where to avoid Python loops
        series = df_copy[field]
        df_copy[field] = series.where(series.isna(), MASK_VALUE)

    logger.info(
        "Obfuscated fields: %s (mask applied, values not logged)",
        fields_to_obfuscate,
    )
    return df_copy
