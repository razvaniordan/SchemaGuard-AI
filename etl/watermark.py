"""
ETL Watermark management.

Tracks the last successfully processed row in each source table,
enabling incremental loads on the next ETL run.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple

import psycopg

logger = logging.getLogger(__name__)


class WatermarkManager:
    """Manages ETL progress tracking via watermark table."""

    def __init__(self, conn_string: str):
        """Initialize with database connection string."""
        self.conn_string = conn_string

    def _get_connection(self):
        """Get a fresh database connection."""
        return psycopg.connect(self.conn_string)

    def get_watermark(
        self, pipeline_name: str, source_table: str
    ) -> Optional[Tuple[int, datetime]]:
        """
        Fetch the last processed transaction_id and authorization_datetime timestamp.

        Returns:
            Tuple of (last_transaction_id, last_authorization_datetime) or None if no prior run.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT last_processed_transaction_id, last_processed_authorization_datetime
                    FROM analytics.etl_watermark
                    WHERE pipeline_name = %s AND source_table = %s
                    """,
                    (pipeline_name, source_table),
                )
                result = cur.fetchone()
                if result:
                    return result
                return None
        finally:
            conn.close()

    def create_watermark(
        self, pipeline_name: str, source_table: str
    ) -> None:
        """Initialize a new watermark if it doesn't exist."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analytics.etl_watermark
                    (pipeline_name, source_table, status)
                    VALUES (%s, %s, 'IDLE')
                    ON CONFLICT (pipeline_name, source_table) DO NOTHING
                    """,
                    (pipeline_name, source_table),
                )
            conn.commit()
        finally:
            conn.close()

    def start_run(self, pipeline_name: str, source_table: str) -> None:
        """Mark the pipeline as RUNNING."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE analytics.etl_watermark
                    SET status = 'RUNNING', current_run_started_at = NOW()
                    WHERE pipeline_name = %s AND source_table = %s
                    """,
                    (pipeline_name, source_table),
                )
            conn.commit()
        finally:
            conn.close()

    def update_watermark(
        self,
        pipeline_name: str,
        source_table: str,
        last_transaction_id: int,
        last_authorization_datetime: datetime,
        rows_processed: int,
        rows_loaded: int,
    ) -> None:
        """Update the watermark after a successful load.

        The second watermark value stores the latest authorization_datetime
        seen in the source transactions table.
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE analytics.etl_watermark
                    SET
                        last_processed_transaction_id = %s,
                        last_processed_authorization_datetime = %s,
                        last_successful_run_at = NOW(),
                        status = 'SUCCESS',
                        error_message = NULL,
                        rows_processed = %s,
                        rows_loaded = %s
                    WHERE pipeline_name = %s AND source_table = %s
                    """,
                    (
                        last_transaction_id,
                        last_authorization_datetime,
                        rows_processed,
                        rows_loaded,
                        pipeline_name,
                        source_table,
                    ),
                )
            conn.commit()
            logger.info(
                f"Watermark updated: {pipeline_name}/{source_table} "
                f"-> txn_id={last_transaction_id}, processed={rows_processed}, loaded={rows_loaded}"
            )
        finally:
            conn.close()

    def mark_failed(
        self, pipeline_name: str, source_table: str, error_message: str
    ) -> None:
        """Mark the pipeline as FAILED with error details."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE analytics.etl_watermark
                    SET status = 'FAILED', error_message = %s
                    WHERE pipeline_name = %s AND source_table = %s
                    """,
                    (error_message, pipeline_name, source_table),
                )
            conn.commit()
        finally:
            conn.close()

    def log_run(
        self,
        pipeline_name: str,
        job_name: str,
        status: str,
        rows_processed: int = 0,
        rows_loaded: int = 0,
        duration_seconds: float = 0.0,
        error_message: str = None,
    ) -> None:
        """Log a job run for auditing."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO analytics.etl_run_log
                    (pipeline_name, job_name, started_at, completed_at, status,
                     rows_processed, rows_loaded, duration_seconds, error_message)
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s, %s)
                    """,
                    (
                        pipeline_name,
                        job_name,
                        status,
                        rows_processed,
                        rows_loaded,
                        duration_seconds,
                        error_message,
                    ),
                )
            conn.commit()
        finally:
            conn.close()
