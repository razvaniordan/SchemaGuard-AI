"""
Materialized view refresher.

Refreshes aggregated views that dashboards depend on.
"""

import logging
from typing import Dict, Any

import psycopg

logger = logging.getLogger(__name__)


class ViewRefresher:
    """Refresh materialized views after fact loads."""

    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def _get_connection(self):
        return psycopg.connect(self.conn_string)

    def refresh_all_views(self) -> Dict[str, Any]:
        """
        Refresh all materialized views.
        Tries to refresh CONCURRENTLY, falls back to non-concurrent refresh
        if the view is not yet populated. Each refresh is in its own transaction.
        """
        result = {"status": "STARTED", "views_refreshed": 0, "total_views": 0, "error": None}

        views = [
            "analytics.mv_monthly_fee_savings",
            "analytics.mv_merchant_optimization_summary",
            "analytics.mv_category_transition_summary",
        ]
        result["total_views"] = len(views)

        for view_name in views:
            try:
                # Establish a new connection for each view to ensure transaction isolation
                with self._get_connection() as conn:
                    conn.autocommit = True  # Use autocommit for DDL-like commands
                    with conn.cursor() as cur:
                        logger.info(f"Refreshing {view_name}...")
                        try:
                            # First, try to refresh concurrently
                            cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name}")
                            logger.info(f"Successfully refreshed {view_name} (concurrently)")
                            result["views_refreshed"] += 1
                        except psycopg.errors.FeatureNotSupported:
                            # This error occurs if the view is not populated and we use CONCURRENTLY
                            logger.warning(
                                f"Could not refresh {view_name} concurrently (view may be empty), "
                                "falling back to standard refresh."
                            )
                            # Fallback to a standard refresh
                            cur.execute(f"REFRESH MATERIALIZED VIEW {view_name}")
                            logger.info(f"Successfully refreshed {view_name} (standard)")
                            result["views_refreshed"] += 1
            except Exception as e:
                # Log the error for the specific view and continue with the next ones
                logger.error(f"Failed to refresh {view_name}: {e}", exc_info=True)
                result["error"] = str(e) # Store last error

        if result["views_refreshed"] == len(views):
            result["status"] = "SUCCESS"
        elif result["views_refreshed"] > 0:
            result["status"] = "PARTIAL_SUCCESS"
        else:
            result["status"] = "FAILED"

        logger.info(f"Refreshed {result['views_refreshed']}/{len(views)} materialized views")
        return result
