"""
ETL Orchestrator.

Coordinates all ETL jobs in the correct order:
1. Load dimensions (simple first, SCD2 second)
2. Load facts incrementally
3. Refresh materialized views
"""

import logging
import time
from typing import Dict, Any

from etl.watermark import WatermarkManager
from etl.dimension_loader import DimensionLoader
from etl.fact_loader import FactTransactionAnalysisLoader
from etl.view_refresher import ViewRefresher
from etl.config import PIPELINE_NAME

logger = logging.getLogger(__name__)


class ETLOrchestrator:
    """Orchestrates the full ETL pipeline."""

    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.watermark = WatermarkManager(conn_string)
        self.dimension_loader = DimensionLoader(conn_string)
        self.fact_loader = FactTransactionAnalysisLoader(conn_string)
        self.view_refresher = ViewRefresher(conn_string)

    def run_full_etl(
        self,
        run_facts: bool = True,
        refresh_views: bool = True,
    ) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline.
        
        Args:
            run_facts: If True, load fact rows after refreshing dimensions.
            refresh_views: If True, refresh materialized views after facts.
        
        Returns:
            Summary of all jobs executed.
        """
        summary = {
            "pipeline": PIPELINE_NAME,
            "status": "STARTED",
            "started_at": time.time(),
            "jobs": {},
            "total_rows_processed": 0,
            "total_rows_loaded": 0,
            "error": None,
        }

        try:
            logger.info("=" * 80)
            logger.info("STARTING ETL PIPELINE")
            logger.info("=" * 80)

            # Step 1: Load/Refresh Dimensions
            logger.info("\n--- STEP 1: Loading Dimensions ---")
            summary["jobs"]["dim_date"] = self._run_job(
                "Load Date Dimension",
                self.dimension_loader.load_dim_date,
            )
            summary["jobs"]["dim_region"] = self._run_job(
                "Load Region Dimension",
                self.dimension_loader.load_dim_region,
            )
            summary["jobs"]["dim_client"] = self._run_job(
                "Load Client Dimension",
                self.dimension_loader.load_dim_client,
            )
            summary["jobs"]["dim_card"] = self._run_job(
                "Load Card Dimension",
                self.dimension_loader.load_dim_card,
            )
            summary["jobs"]["dim_acquiring_partner"] = self._run_job(
                "Load Acquiring Partner Dimension",
                self.dimension_loader.load_dim_acquiring_partner,
            )
            summary["jobs"]["dim_interchange_category"] = self._run_job(
                "Load Interchange Category Dimension",
                self.dimension_loader.load_dim_interchange_category,
            )

            # SCD2 Dimensions
            summary["jobs"]["dim_country_scd2"] = self._run_job(
                "Load Country Dimension (SCD Type 2)",
                self.dimension_loader.load_dim_country_scd2,
            )
            summary["jobs"]["dim_merchant_scd2"] = self._run_job(
                "Load Merchant Dimension (SCD Type 2)",
                self.dimension_loader.load_dim_merchant_scd2,
            )

            # Step 2: Load Facts Incrementally
            if run_facts:
                logger.info("\n--- STEP 2: Loading Facts (Incremental) ---")
                summary["jobs"]["fact_transaction_analysis"] = self._run_job(
                    "Load Fact Transaction Analysis",
                    self.fact_loader.load_incremental,
                )
            else:
                logger.info("\n--- STEP 2: Skipping Facts ---")

            # Step 3: Refresh Materialized Views
            if refresh_views:
                logger.info("\n--- STEP 3: Refreshing Materialized Views ---")
                summary["jobs"]["refresh_views"] = self._run_job(
                    "Refresh Materialized Views",
                    self.view_refresher.refresh_all_views,
                )
            else:
                logger.info("\n--- STEP 3: Skipping Materialized Views ---")

            # Calculate totals and final status
            summary["total_rows_processed"] = sum(
                job.get("rows_processed", 0)
                for job in summary["jobs"].values()
                if isinstance(job, dict)
            )
            summary["total_rows_loaded"] = sum(
                job.get("rows_loaded", 0)
                for job in summary["jobs"].values()
                if isinstance(job, dict)
            )
            summary["status"] = "SUCCESS"

            logger.info("\n" + "=" * 80)
            logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"Total rows processed: {summary['total_rows_processed']}")
            logger.info(f"Total rows loaded: {summary['total_rows_loaded']}")
            logger.info("=" * 80 + "\n")

        except Exception as e:
            summary["status"] = "FAILED"
            summary["error"] = str(e)
            logger.error(f"\nETL PIPELINE FAILED: {e}", exc_info=True)

        finally:
            summary["completed_at"] = time.time()
            summary["duration_seconds"] = summary["completed_at"] - summary["started_at"]

        return summary

    def run_incremental_facts_only(self) -> Dict[str, Any]:
        """Run only the incremental fact load (fast refresh)."""
        logger.info("Running incremental fact load only...")
        return self.fact_loader.load_incremental()

    @staticmethod
    def _run_job(job_name: str, job_func) -> Dict[str, Any]:
        """
        Execute a single job and log results.
        
        Args:
            job_name: Human-readable job name.
            job_func: Callable that returns a result dict with 'status', 'rows_loaded', etc.
        
        Returns:
            Result dictionary from the job.
        """
        logger.info(f"  Starting: {job_name}...")
        try:
            result = job_func()
            status = result.get("status", "UNKNOWN")
            rows = result.get("rows_loaded", 0) or result.get("views_refreshed", 0)
            logger.info(f"{job_name}: {status} ({rows} items)")
            return result
        except Exception as e:
            logger.error(f"{job_name} FAILED: {e}")
            return {"status": "FAILED", "error": str(e)}
