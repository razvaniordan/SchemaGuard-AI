"""
ETL Scheduler.

Schedule the ETL pipeline to run at regular intervals using APScheduler.

Usage:
  python etl/scheduler.py --interval 15    # Run every 15 minutes
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv


# Load .env into environment before reading config
load_dotenv()

ETL_DIR = Path(__file__).resolve().parent
ROOT_DIR = ETL_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from etl.config import get_database_url, validate_config, LOG_LEVEL, LOG_FILE
from etl.orchestrator import ETLOrchestrator


def setup_logging():
    """Configure logging for the scheduler."""
    log_format = "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if LOG_FILE:
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(LOG_FILE))
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=log_format,
        handlers=handlers,
    )


def run_etl_job(orchestrator: ETLOrchestrator, logger):
    """Execute the load-all ETL job with dimensions refreshed first."""
    logger.info("=" * 80)
    logger.info(f"ETL Job started at {datetime.now()}")
    logger.info("=" * 80)
    
    try:
        result = orchestrator.run_full_etl()
        logger.info(f"ETL Job completed with status: {result['status']}")
    except Exception as e:
        logger.error(f"ETL Job failed: {e}", exc_info=True)


def main():
    """Start the ETL scheduler."""
    parser = argparse.ArgumentParser(description="SchemeGuard AI ETL Scheduler")
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Interval in minutes between ETL runs (default: 15)",
    )
    parser.add_argument(
        "--conn-string",
        help="Database connection string (overrides DATABASE_URL env var)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate config
        validate_config()
        
        # Get database connection string
        conn_string = args.conn_string or get_database_url()
        
        logger.info("Initializing ETL Scheduler...")
        logger.info(f"Interval: {args.interval} minutes")
        logger.info(f"Database: {conn_string.split('@')[1] if '@' in conn_string else 'unknown'}")
        
        # Create orchestrator
        orchestrator = ETLOrchestrator(conn_string)
        
        # Create scheduler
        scheduler = BackgroundScheduler()
        
        # Add job
        scheduler.add_job(
            run_etl_job,
            trigger=IntervalTrigger(minutes=args.interval),
            args=[orchestrator, logger],
            id="etl_job",
            name="Load All ETL Pipeline",
            replace_existing=True,
        )
        
        logger.info("Starting scheduler...")
        scheduler.start()
        
        # Run initial job immediately
        logger.info("Running initial ETL job...")
        run_etl_job(orchestrator, logger)
        
        # Keep scheduler running
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
