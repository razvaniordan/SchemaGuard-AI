# SchemeGuard AI - ETL Pipeline

Extract, Transform, Load for the analytics warehouse. This ETL pipeline populates the star schema from operational data.

## Architecture

The ETL pipeline follows a modular design:

```
├── etl/
│   ├── __init__.py                  # Package exports
│   ├── config.py                    # Configuration and environment
│   ├── watermark.py                 # Progress tracking (incremental loads)
│   ├── dimension_loader.py          # Load dimensions (simple + SCD Type 2)
│   ├── fact_loader.py               # Load facts incrementally
│   ├── view_refresher.py            # Refresh materialized views
│   ├── orchestrator.py              # Coordinates all jobs
│   ├── run_etl.py                   # CLI entry point
│   └── scheduler.py                 # APScheduler for recurring runs
```

## Setup

### 1. Install Dependencies

From the project root:

```bash
pip install -r etl/requirements.txt
```

Or from inside the `etl` folder:

```bash
cd etl
pip install -r requirements.txt
```

### 2. Configure Database

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/schemeguard
ETL_LOG_LEVEL=INFO
```

### 3. Create Migration Tables

Run the Flyway migration to create control tables:

```sql
-- database/migrations/V5__create_etl_control_table.sql
```

The migration creates:
- `analytics.etl_watermark` — Tracks progress for incremental loads
- `analytics.etl_run_log` — Audit log of all ETL runs

## Usage

### Run Load-All ETL

```bash
python etl/run_etl.py --mode load_all
```

Runs the complete ETL pipeline: loads/refreshes all dimensions (simple + SCD Type 2), then loads facts incrementally using the watermark, and finally refreshes the materialized views.

### Run Dimensions Only

```bash
python etl/run_etl.py --mode load_dimensions
```

This refreshes only the dimension tables and skips facts and materialized views.

### Run Scheduler (Continuous)

```bash
python etl/scheduler.py --interval 15
```

Runs load-all ETL every 15 minutes. Press Ctrl+C to stop.

## How It Works

### 1. Watermark-Based Incremental Loading

The ETL uses a watermark table to track progress:

```python
# First run
# watermark = None
# → Load all data

# Second run (30 min later)
# watermark = (transaction_id: 10000, authorization_datetime: 2026-05-08 14:30:00)
# → Load only transactions where transaction_id > 10000 or authorization_datetime > 2026-05-08 14:30:00
# → Update watermark to new high-water mark
```

This makes incremental runs fast and idempotent.

### 2. Dimension Loading

Each dimension is loaded from one primary source table and, for some dimensions, additional lookup/enrichment tables.

**Simple dimensions** (upsert on unique key):
- `dim_date` — Generated from a date range, not from a source table
- `dim_region` — Primary source: `public.regions`
- `dim_client` — Primary source: `public.clients`; lookup table: `public.countries`
- `dim_card` — Primary source: `public.cards`; lookup tables: `public.card_types`, `public.card_networks`, `public.banks`, `public.countries`
- `dim_acquiring_partner` — Primary source: `public.acquiring_partners`; lookup table: `public.countries`
- `dim_interchange_category` — Primary source: `public.interchange_categories`

**SCD Type 2 dimensions** (version tracking):
- `dim_country` — Primary source: `public.countries`; lookup table: `public.regions`
- `dim_merchant` — Primary source: `public.merchants`; lookup tables: `public.mcc_codes`, `public.countries`, `public.acquiring_partners`

When source data changes, old versions are closed (`is_current = 'N'`, `effective_to = NOW()`) and new versions are inserted.

### 3. Fact Loading

`fact_transaction_analysis` combines:
- Transaction details from `public.transactions`
- Current interchange results from `transaction_interchange_results` (result_type = 'CURRENT')
- Optimal interchange results from `transaction_interchange_results` (result_type = 'OPTIMAL')
- Optimization savings from `transaction_optimization_results`
- Top recommendation from `transaction_optimization_recommendations`

Derived fields computed during load:
- `authorization_date_key` — Date key for partitioning
- `clearing_hours` — Hours between authorization and clearing
- `clearing_time_condition` — 'LTE_24H' or 'GT_24H'
- Surrogate keys for all dimensions (lookup from `dim_*` tables)

### 4. Materialized View Refresh

After facts are loaded, materialized views are refreshed:
- `mv_monthly_fee_savings` — Monthly totals by savings
- `mv_merchant_optimization_summary` — Merchant-level rollup
- `mv_category_transition_summary` — Category migration patterns

## Configuration

Environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/db

# ETL Tuning
ETL_BATCH_SIZE=1000                  # Rows per batch insert
ETL_INCREMENTAL_HOURS=24              # Lookback window for delta detection

# Logging
ETL_LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
ETL_LOG_FILE=logs/etl.log            # Optional; leave empty for console only
```

## Monitoring

### Check Watermark Status

```sql
SELECT pipeline_name, source_table, status, last_processed_transaction_id, last_successful_run_at
FROM analytics.etl_watermark;
```

### View ETL Run History

```sql
SELECT pipeline_name, job_name, status, rows_processed, rows_loaded, duration_seconds, started_at
FROM analytics.etl_run_log
ORDER BY started_at DESC
LIMIT 20;
```

## Troubleshooting

### ETL Stuck in RUNNING State

If a previous run crashed, the watermark may still be marked RUNNING:

```sql
UPDATE analytics.etl_watermark
SET status = 'IDLE'
WHERE pipeline_name = 'interchange_analysis_etl' AND status = 'RUNNING';
```

### Reset Watermark (Start Fresh)

```sql
DELETE FROM analytics.etl_watermark
WHERE pipeline_name = 'interchange_analysis_etl';
```

### View Recent Errors

```sql
SELECT pipeline_name, job_name, status, error_message, started_at
FROM analytics.etl_run_log
WHERE status = 'FAILED'
ORDER BY started_at DESC
LIMIT 10;
```
