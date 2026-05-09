"""
Incremental fact table loader.

Loads transaction_analysis facts from operational tables using watermark-based
incremental filtering. Joins transactions, current/optimal results, and
optimization records into the warehouse fact table.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import psycopg

from etl.watermark import WatermarkManager

logger = logging.getLogger(__name__)


class FactTransactionAnalysisLoader:
    """Load fact_transaction_analysis incrementally."""

    def __init__(self, conn_string: str):
        self.conn_string = conn_string
        self.watermark = WatermarkManager(conn_string)
        self.pipeline_name = "interchange_analysis_etl"
        self.source_table = "transactions"

    def _get_connection(self):
        return psycopg.connect(self.conn_string)

    def load_incremental(self) -> Dict[str, Any]:
        """
        Load new and updated transactions into fact table using watermark.
        
        Returns:
            Dict with rows_processed, rows_loaded, status, and any errors.
        """
        result = {
            "status": "STARTED",
            "rows_processed": 0,
            "rows_loaded": 0,
            "error": None,
        }

        try:
            # Initialize watermark if needed
            self.watermark.create_watermark(self.pipeline_name, self.source_table)

            # Get last processed watermark
            watermark = self.watermark.get_watermark(
                self.pipeline_name, self.source_table
            )

            if watermark and watermark[0] is not None and watermark[1] is not None:
                last_txn_id, last_authorization_datetime = watermark
                logger.info(
                    f"Resuming from watermark: txn_id={last_txn_id}, authorization_datetime={last_authorization_datetime}"
                )
            else:
                last_txn_id = 0
                last_authorization_datetime = datetime(2020, 1, 1)
                logger.info("No prior watermark; starting fresh from beginning")

            # Mark run as RUNNING
            self.watermark.start_run(self.pipeline_name, self.source_table)

            # Query new/updated transactions
            conn = self._get_connection()
            try:
                new_rows = self._fetch_delta_transactions(
                    conn, last_txn_id, last_authorization_datetime
                )
                result["rows_processed"] = len(new_rows)

                if len(new_rows) == 0:
                    logger.info("No new transactions to load.")
                    self.watermark.log_run(
                        self.pipeline_name,
                        "load_fact_transaction_analysis",
                        "SKIPPED",
                    )
                    result["status"] = "SUCCESS"
                    return result

                # Transform and load rows
                loaded_count = self._insert_fact_rows(conn, new_rows)
                result["rows_loaded"] = loaded_count

                # Update watermark with new high water mark
                if len(new_rows) > 0:
                    max_row = max(new_rows, key=lambda r: r["transaction_id"])
                    self.watermark.update_watermark(
                        self.pipeline_name,
                        self.source_table,
                        max_row["transaction_id"],
                        max_row["authorization_datetime"],
                        result["rows_processed"],
                        result["rows_loaded"],
                    )

                result["status"] = "SUCCESS"
                logger.info(
                    f"Fact load succeeded: processed={result['rows_processed']}, "
                    f"loaded={result['rows_loaded']}"
                )

            finally:
                conn.close()

        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            self.watermark.mark_failed(
                self.pipeline_name, self.source_table, str(e)
            )
            logger.error(f"Fact load failed: {e}", exc_info=True)

        return result

    def _fetch_delta_transactions(
        self, conn, last_txn_id: int, last_authorization_datetime: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions and their analysis data since last watermark.
        
        Joins:
        - public.transactions (source)
        - public.transaction_interchange_results (current and optimal)
        - public.transaction_optimization_results (savings data)
        - public.transaction_optimization_recommendations (top recommendation)
        """
        query = """
        SELECT
            t.transaction_id,
            t.authorization_datetime,
            t.client_id,
            t.merchant_id,
            t.card_id,
            t.acquiring_partner_id,
            t.region_code,
            
            t.transaction_amount,
            t.transaction_currency,
            t.transaction_channel,
            t.mcc_code,
            t.transaction_status,
            t.is_3ds_authenticated,
            t.authorization_datetime,
            
            EXTRACT(EPOCH FROM (t.clearing_datetime - t.authorization_datetime)) / 3600.0 
                AS clearing_hours,
            
            CASE 
                WHEN t.clearing_datetime IS NULL THEN NULL
                WHEN EXTRACT(EPOCH FROM (t.clearing_datetime - t.authorization_datetime)) / 3600.0 <= 24 
                THEN 'LTE_24H'
                ELSE 'GT_24H'
            END AS clearing_time_condition,
            
            cur_result.result_id AS current_result_id,
            cur_result.category_id AS current_category_id,
            cur_result.fee_percentage AS current_fee_percentage,
            cur_result.interchange_fee_amount AS current_interchange_fee_amount,
            
            opt_result.result_id AS optimal_result_id,
            opt_result.category_id AS optimal_category_id,
            opt_result.fee_percentage AS optimal_fee_percentage,
            opt_result.interchange_fee_amount AS optimal_interchange_fee_amount,
            
            opt.optimization_result_id,
            opt.saving_amount,
            opt.saving_percentage,
            
            COALESCE(rec.recommendation_type, 'NONE') AS top_recommendation_type,
            COALESCE(rec.recommendation_text, '') AS top_recommendation_text,
            COALESCE(rec.priority_rank, 0) AS recommendation_count
            
        FROM public.transactions t
        LEFT JOIN public.transaction_interchange_results cur_result
            ON cur_result.transaction_id = t.transaction_id
            AND cur_result.result_type = 'CURRENT'
        LEFT JOIN public.transaction_interchange_results opt_result
            ON opt_result.transaction_id = t.transaction_id
            AND opt_result.result_type = 'OPTIMAL'
        LEFT JOIN public.transaction_optimization_results opt
            ON opt.transaction_id = t.transaction_id
        LEFT JOIN public.transaction_optimization_recommendations rec
            ON rec.transaction_id = t.transaction_id
            AND rec.priority_rank = 1
        
        WHERE t.transaction_id > %s
           OR (t.transaction_id = %s AND t.authorization_datetime > %s)
        ORDER BY t.transaction_id, t.authorization_datetime
        LIMIT 10000
        """

        with conn.cursor() as cur:
            cur.execute(query, (last_txn_id, last_txn_id, last_authorization_datetime))
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        return rows

    def _insert_fact_rows(self, conn, rows: List[Dict[str, Any]]) -> int:
        """
        Insert or update fact rows using upsert (ON CONFLICT DO UPDATE).
        Uses surrogate keys from dimension tables.
        """
        inserted_count = 0

        insert_query = """
        INSERT INTO analytics.fact_transaction_analysis (
            source_transaction_id,
            source_current_result_id,
            source_optimal_result_id,
            source_optimization_result_id,
            authorization_date_key,
            client_key,
            merchant_key,
            card_key,
            acquiring_partner_key,
            region_key,
            current_category_key,
            optimal_category_key,
            transaction_amount,
            transaction_currency,
            transaction_channel,
            transaction_mcc_code,
            transaction_status,
            is_3ds_authenticated,
            clearing_hours,
            clearing_time_condition,
            current_fee_percentage,
            current_interchange_fee_amount,
            optimal_fee_percentage,
            optimal_interchange_fee_amount,
            saving_amount,
            saving_percentage,
            recommendation_count,
            top_recommendation_type,
            top_recommendation_text
        )
        SELECT
            p.source_transaction_id,
            p.source_current_result_id,
            p.source_optimal_result_id,
            p.source_optimization_result_id,
            TO_CHAR(p.authorization_datetime::date, 'YYYYMMDD')::INT,
            COALESCE(dc.client_key, -1),
            COALESCE(dm.merchant_key, -1),
            COALESCE(dcard.card_key, -1),
            COALESCE(dap.acquiring_partner_key, -1),
            COALESCE(dr.region_key, -1),
            COALESCE(dic_curr.category_key, -1),
            COALESCE(dic_opt.category_key, -1),
            p.transaction_amount,
            p.transaction_currency,
            p.transaction_channel,
            p.transaction_mcc_code,
            p.transaction_status,
            p.is_3ds_authenticated,
            p.clearing_hours,
            p.clearing_time_condition,
            p.current_fee_percentage,
            p.current_interchange_fee_amount,
            p.optimal_fee_percentage,
            p.optimal_interchange_fee_amount,
            p.saving_amount,
            p.saving_percentage,
            p.recommendation_count,
            p.top_recommendation_type,
            p.top_recommendation_text
        FROM (
            SELECT
                %s::BIGINT AS source_transaction_id,
                %s::BIGINT AS source_current_result_id,
                %s::BIGINT AS source_optimal_result_id,
                %s::BIGINT AS source_optimization_result_id,
                %s::TIMESTAMP AS authorization_datetime,
                %s::BIGINT AS client_id,
                %s::BIGINT AS merchant_id,
                %s::BIGINT AS card_id,
                %s::BIGINT AS acquiring_partner_id,
                %s::VARCHAR AS region_code,
                %s::BIGINT AS current_category_id,
                %s::BIGINT AS optimal_category_id,
                %s::NUMERIC AS transaction_amount,
                %s::CHAR(3) AS transaction_currency,
                %s::VARCHAR AS transaction_channel,
                %s::VARCHAR AS transaction_mcc_code,
                %s::VARCHAR AS transaction_status,
                %s::CHAR(1) AS is_3ds_authenticated,
                %s::NUMERIC AS clearing_hours,
                %s::VARCHAR AS clearing_time_condition,
                %s::NUMERIC AS current_fee_percentage,
                %s::NUMERIC AS current_interchange_fee_amount,
                %s::NUMERIC AS optimal_fee_percentage,
                %s::NUMERIC AS optimal_interchange_fee_amount,
                %s::NUMERIC AS saving_amount,
                %s::NUMERIC AS saving_percentage,
                %s::INT AS recommendation_count,
                %s::VARCHAR AS top_recommendation_type,
                %s::VARCHAR AS top_recommendation_text
        ) AS p
        LEFT JOIN analytics.dim_client dc ON dc.source_client_id = p.client_id
        LEFT JOIN analytics.dim_merchant dm ON dm.source_merchant_id = p.merchant_id AND dm.is_current = 'Y'
        LEFT JOIN analytics.dim_card dcard ON dcard.source_card_id = p.card_id
        LEFT JOIN analytics.dim_acquiring_partner dap ON dap.source_acquiring_partner_id = p.acquiring_partner_id
        LEFT JOIN analytics.dim_region dr ON dr.source_region_code = p.region_code
        LEFT JOIN analytics.dim_interchange_category dic_curr ON dic_curr.source_category_id = p.current_category_id
        LEFT JOIN analytics.dim_interchange_category dic_opt ON dic_opt.source_category_id = p.optimal_category_id
        
        ON CONFLICT (source_transaction_id, authorization_date_key) 
        DO UPDATE SET
            source_current_result_id = EXCLUDED.source_current_result_id,
            source_optimal_result_id = EXCLUDED.source_optimal_result_id,
            client_key = EXCLUDED.client_key,
            merchant_key = EXCLUDED.merchant_key,
            card_key = EXCLUDED.card_key,
            acquiring_partner_key = EXCLUDED.acquiring_partner_key,
            region_key = EXCLUDED.region_key,
            current_category_key = EXCLUDED.current_category_key,
            optimal_category_key = EXCLUDED.optimal_category_key,
            current_interchange_fee_amount = EXCLUDED.current_interchange_fee_amount,
            optimal_interchange_fee_amount = EXCLUDED.optimal_interchange_fee_amount,
            saving_amount = EXCLUDED.saving_amount,
            saving_percentage = EXCLUDED.saving_percentage,
            recommendation_count = EXCLUDED.recommendation_count,
            top_recommendation_type = EXCLUDED.top_recommendation_type,
            top_recommendation_text = EXCLUDED.top_recommendation_text,
            created_at = CURRENT_TIMESTAMP
        RETURNING 1
        """

        with conn.cursor() as cur:
            for row in rows:
                try:
                    cur.execute(
                        insert_query,
                        (
                            row["transaction_id"],
                            row["current_result_id"],
                            row["optimal_result_id"],
                            row["optimization_result_id"],
                            row["authorization_datetime"],
                            row["client_id"],
                            row["merchant_id"],
                            row["card_id"],
                            row["acquiring_partner_id"],
                            row["region_code"],
                            row["current_category_id"],
                            row["optimal_category_id"],
                            row["transaction_amount"],
                            row["transaction_currency"],
                            row["transaction_channel"],
                            row["mcc_code"],
                            row["transaction_status"],
                            row["is_3ds_authenticated"],
                            row["clearing_hours"],
                            row["clearing_time_condition"],
                            row["current_fee_percentage"],
                            row["current_interchange_fee_amount"],
                            row["optimal_fee_percentage"],
                            row["optimal_interchange_fee_amount"],
                            row["saving_amount"],
                            row["saving_percentage"],
                            row["recommendation_count"],
                            row["top_recommendation_type"],
                            row["top_recommendation_text"],
                        ),
                    )
                    if cur.fetchone():
                        inserted_count += 1
                except Exception as e:
                    logger.error(f"Failed to insert row for transaction {row['transaction_id']}: {e}")

        conn.commit()
        return inserted_count
