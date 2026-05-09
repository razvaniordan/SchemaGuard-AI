"""
Database helper utilities for ETL modules.

Consolidates common patterns: connection management, result dicts, error handling.
"""

from contextlib import contextmanager
from typing import Any, Dict, Callable
import logging

import psycopg

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection(conn_string: str):
    """
    Context manager for database connections.
    
    Handles opening and closing the connection. Commit/rollback is caller's responsibility.
    
    Usage:
        with get_db_connection(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
    """
    conn = psycopg.connect(conn_string)
    try:
        yield conn
    finally:
        conn.close()


def make_result_dict(status: str = "STARTED", **kwargs) -> Dict[str, Any]:
    """
    Create a standard result dict for ETL jobs.
    
    Args:
        status: Job status (STARTED, SUCCESS, FAILED, SKIPPED).
        **kwargs: Additional fields like rows_loaded, error, etc.
    
    Returns:
        Dict with status and any additional fields.
    """
    result = {"status": status}
    result.update(kwargs)
    return result


def execute_with_error_handling(
    job_name: str,
    job_func: Callable,
    conn_string: str = None,
) -> Dict[str, Any]:
    """
    Execute a job function with standard error handling and logging.
    
    Args:
        job_name: Human-readable job name for logging.
        job_func: Callable that takes conn_string and returns a result dict.
        conn_string: Database connection string (if needed by job_func).
    
    Returns:
        Result dict with status and details.
    """
    logger.info(f"Starting: {job_name}...")
    try:
        result = job_func(conn_string) if conn_string else job_func()
        status = result.get("status", "UNKNOWN")
        count = result.get("rows_loaded", 0) or result.get("views_refreshed", 0)
        logger.info(f"{job_name}: {status} ({count} items)")
        return result
    except Exception as e:
        logger.error(f"{job_name} FAILED: {e}", exc_info=True)
        return make_result_dict("FAILED", error=str(e))
