"""
ETL Main Entry Point.

Usage:
    python etl/run_etl.py --mode load_all             # Dimensions + facts + views
    python etl/run_etl.py --mode load_dimensions      # Dimensions only
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

from etl.config import get_database_url, validate_config, LOG_LEVEL, LOG_FILE
from etl.orchestrator import ETLOrchestrator


def setup_logging():
    """Configure logging for the ETL pipeline."""
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


def main():
    """Main ETL entry point."""
    parser = argparse.ArgumentParser(description="SchemeGuard AI ETL Pipeline")
    parser.add_argument(
        "--mode",
        choices=["load_all", "load_dimensions"],
        default="load_all",
        help="ETL mode: load_all (dimensions + facts + views), load_dimensions (dimensions only)",
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
        
        logger.info("Initializing ETL pipeline...")
        logger.info(f"Mode: {args.mode}")
        logger.info(f"Database: {conn_string.split('@')[1] if '@' in conn_string else 'unknown'}")
        
        # Create orchestrator
        orchestrator = ETLOrchestrator(conn_string)
        
        # Run based on mode
        if args.mode == "load_all":
            logger.info("Running LOAD ALL ETL (dimensions + facts + views)")
            result = orchestrator.run_full_etl()
        elif args.mode == "load_dimensions":
            logger.info("Running DIMENSION LOAD ONLY")
            result = orchestrator.run_full_etl(run_facts=False, refresh_views=False)
        
        # Log final result
        logger.info(f"\nFinal Status: {result['status']}")
        if result["status"] == "FAILED":
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        logger.info("ETL pipeline completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
