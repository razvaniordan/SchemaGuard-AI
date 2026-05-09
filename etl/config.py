"""
ETL Configuration and utilities.
"""

import os
from typing import Optional

# Database connection
DATABASE_URL: str = os.getenv("DATABASE_URL")

# ETL Pipeline configuration
PIPELINE_NAME: str = "interchange_analysis_etl"

# Load batching and performance
BATCH_SIZE: int = int(os.getenv("ETL_BATCH_SIZE", "1000"))
INCREMENTAL_LOAD_HOURS: int = int(os.getenv("ETL_INCREMENTAL_HOURS", "24"))

# Logging
LOG_LEVEL: str = os.getenv("ETL_LOG_LEVEL", "INFO")
LOG_FILE: Optional[str] = os.getenv("ETL_LOG_FILE", None)


def get_database_url() -> str:
    """Get the database connection URL from environment or config."""
    return DATABASE_URL


def validate_config() -> bool:
    """Validate that all required configuration is available."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    return True
