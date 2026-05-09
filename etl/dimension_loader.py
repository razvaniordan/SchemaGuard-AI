"""
Dimension table loader.

Loads simple dimensions and handles SCD Type 2 dimensions (version tracking).

Simple dimensions (upsert on unique key):
- dim_date: generated from date range
- dim_region: from public.regions
- dim_client: from public.clients + public.countries (lookup)
- dim_card: from public.cards + public.card_types, card_networks, banks, countries (lookups)
- dim_acquiring_partner: from public.acquiring_partners + public.countries (lookup)
- dim_interchange_category: from public.interchange_categories

SCD Type 2 dimensions (version tracking):
- dim_country: from public.countries + public.regions (lookup)
- dim_merchant: from public.merchants + public.mcc_codes, countries, acquiring_partners (lookups)
"""

import logging
from typing import Dict, Any

from etl.db_helper import get_db_connection, make_result_dict

logger = logging.getLogger(__name__)


class DimensionLoader:
    """Load dimension tables from operational data."""

    def __init__(self, conn_string: str):
        self.conn_string = conn_string

    def load_dim_date(self, start_year: int = 2020, end_year: int = 2027) -> Dict[str, Any]:
        """
        Generate and load date dimension.
        
        Date dimension has no source table; it's generated from a date range.
        """
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Generate dates for the range and insert
                    sql = f"""
                    WITH date_range AS (
                        SELECT date_trunc('day', d)::date AS full_date
                        FROM generate_series(
                            '{start_year}-01-01'::date,
                            '{end_year}-12-31'::date,
                            '1 day'::interval
                        ) d
                    )
                    INSERT INTO analytics.dim_date (
                        date_key, full_date, day_number, month_number, month_name,
                        quarter_number, year_number, is_weekend
                    )
                    SELECT
                        TO_CHAR(full_date, 'YYYYMMDD')::INT AS date_key,
                        full_date,
                        EXTRACT(DAY FROM full_date)::INT AS day_number,
                        EXTRACT(MONTH FROM full_date)::INT AS month_number,
                        TO_CHAR(full_date, 'Month') AS month_name,
                        CEIL(EXTRACT(MONTH FROM full_date) / 3.0)::INT AS quarter_number,
                        EXTRACT(YEAR FROM full_date)::INT AS year_number,
                        CASE WHEN EXTRACT(DOW FROM full_date) IN (0, 6) THEN 'Y' ELSE 'N' END AS is_weekend
                    FROM date_range
                    ON CONFLICT (date_key) DO NOTHING
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} date dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_date: {e}", exc_info=True)

        return result

    def load_dim_region(self) -> Dict[str, Any]:
        """Load region dimension from public.regions."""
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO analytics.dim_region (source_region_code, region_name, description)
                    SELECT region_code, region_name, description
                    FROM public.regions
                    ON CONFLICT (source_region_code) DO UPDATE
                    SET region_name = EXCLUDED.region_name,
                        description = EXCLUDED.description
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} region dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_region: {e}", exc_info=True)

        return result

    def load_dim_client(self) -> Dict[str, Any]:
        """Load client dimension from public.clients."""
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO analytics.dim_client (
                        source_client_id, client_name, country_code, country_name, region_code
                    )
                    SELECT
                        c.client_id,
                        c.client_name,
                        c.country_code,
                        co.country_name,
                        co.region_code
                    FROM public.clients c
                    LEFT JOIN public.countries co ON co.country_code = c.country_code
                    ON CONFLICT (source_client_id) DO UPDATE
                    SET client_name = EXCLUDED.client_name,
                        country_code = EXCLUDED.country_code,
                        country_name = EXCLUDED.country_name,
                        region_code = EXCLUDED.region_code
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} client dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_client: {e}", exc_info=True)

        return result

    def load_dim_card(self) -> Dict[str, Any]:
        """Load card dimension from public.cards and related tables."""
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO analytics.dim_card (
                        source_card_id, card_product_type, source_card_type_id, card_type_name,
                        card_type_description, source_card_network_id, network_code, network_name,
                        source_issuer_bank_id, issuer_bank_name, issuer_country_code, 
                        issuer_country_name, issuer_region_code
                    )
                    SELECT
                        c.card_id,
                        c.card_product_type,
                        ct.card_type_id,
                        ct.card_type_name,
                        ct.description,
                        cn.card_network_id,
                        cn.network_code,
                        cn.network_name,
                        b.bank_id,
                        b.bank_name,
                        b.country_code,
                        co.country_name,
                        co.region_code
                    FROM public.cards c
                    LEFT JOIN public.card_types ct ON ct.card_type_id = c.card_type_id
                    LEFT JOIN public.card_networks cn ON cn.card_network_id = c.card_network_id
                    LEFT JOIN public.banks b ON b.bank_id = c.issuer_bank_id
                    LEFT JOIN public.countries co ON co.country_code = b.country_code
                    ON CONFLICT (source_card_id) DO UPDATE
                    SET card_product_type = EXCLUDED.card_product_type,
                        card_type_name = EXCLUDED.card_type_name,
                        network_code = EXCLUDED.network_code,
                        issuer_bank_name = EXCLUDED.issuer_bank_name
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} card dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_card: {e}", exc_info=True)

        return result

    def load_dim_acquiring_partner(self) -> Dict[str, Any]:
        """Load acquiring partner dimension."""
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO analytics.dim_acquiring_partner (
                        source_acquiring_partner_id, partner_name, partner_type,
                        country_code, country_name, region_code
                    )
                    SELECT
                        ap.acquiring_partner_id,
                        ap.partner_name,
                        ap.partner_type,
                        ap.country_code,
                        co.country_name,
                        co.region_code
                    FROM public.acquiring_partners ap
                    LEFT JOIN public.countries co ON co.country_code = ap.country_code
                    ON CONFLICT (source_acquiring_partner_id) DO UPDATE
                    SET partner_name = EXCLUDED.partner_name,
                        partner_type = EXCLUDED.partner_type,
                        country_name = EXCLUDED.country_name
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} acquiring partner dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_acquiring_partner: {e}", exc_info=True)

        return result

    def load_dim_interchange_category(self) -> Dict[str, Any]:
        """Load interchange category dimension."""
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO analytics.dim_interchange_category (
                        source_category_id, category_name, description
                    )
                    SELECT
                        category_id,
                        category_name,
                        description
                    FROM public.interchange_categories
                    ON CONFLICT (source_category_id) DO UPDATE
                    SET category_name = EXCLUDED.category_name,
                        description = EXCLUDED.description
                    RETURNING (xmax = 0)
                    """
                    cur.execute(sql)
                    inserted_count = sum(1 for row in cur.fetchall() if row[0])
                conn.commit()
                result["rows_loaded"] = inserted_count
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} interchange category dimension rows")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_interchange_category: {e}", exc_info=True)

        return result

    def load_dim_country_scd2(self) -> Dict[str, Any]:
        """
        Load country dimension with SCD Type 2 tracking.
        
        When country attributes change, close the old version and insert a new one.
        """
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Close old versions of changed rows
                    sql_close = """
                    UPDATE analytics.dim_country
                    SET is_current = 'N', effective_to = NOW()
                    WHERE is_current = 'Y'
                    AND source_country_code IN (
                        SELECT DISTINCT c.country_code
                        FROM public.countries c
                        LEFT JOIN analytics.dim_country dc 
                            ON dc.source_country_code = c.country_code 
                            AND dc.is_current = 'Y'
                        WHERE dc.country_name IS NULL
                           OR dc.country_name != c.country_name
                    )
                    """
                    cur.execute(sql_close)
                    close_count = cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0

                    # Insert new versions
                    sql_insert = """
                    INSERT INTO analytics.dim_country (
                        source_country_code, country_name, region_code, region_name,
                        effective_from, is_current, version_number
                    )
                    SELECT
                        c.country_code,
                        c.country_name,
                        c.region_code,
                        r.region_name,
                        NOW(),
                        'Y',
                        COALESCE(
                            (SELECT MAX(dc2.version_number)
                             FROM analytics.dim_country dc2
                             WHERE dc2.source_country_code = c.country_code),
                            0
                        ) + 1
                    FROM public.countries c
                    LEFT JOIN public.regions r ON r.region_code = c.region_code
                    LEFT JOIN analytics.dim_country dc 
                        ON dc.source_country_code = c.country_code
                       AND dc.is_current = 'Y'
                    WHERE dc.source_country_code IS NULL
                       OR dc.country_name != c.country_name
                       OR dc.region_code != c.region_code
                    ON CONFLICT (source_country_code, effective_from) DO NOTHING
                    """
                    cur.execute(sql_insert + "\nRETURNING 1")
                    returned = cur.fetchall()
                conn.commit()
                result["rows_loaded"] = len(returned) + (close_count if 'close_count' in locals() else 0)
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} country dimension rows (SCD2)")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_country (SCD2): {e}", exc_info=True)

        return result

    def load_dim_merchant_scd2(self) -> Dict[str, Any]:
        """
        Load merchant dimension with SCD Type 2 tracking.
        
        When merchant attributes change, close the old version and insert a new one.
        """
        result = make_result_dict("STARTED", rows_loaded=0, error=None)

        try:
            with get_db_connection(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Close old versions of changed rows
                    sql_close = """
                    UPDATE analytics.dim_merchant
                    SET is_current = 'N', effective_to = NOW()
                    WHERE is_current = 'Y'
                    AND source_merchant_id IN (
                        SELECT DISTINCT m.merchant_id
                        FROM public.merchants m
                        LEFT JOIN analytics.dim_merchant dm 
                            ON dm.source_merchant_id = m.merchant_id 
                            AND dm.is_current = 'Y'
                        WHERE dm.merchant_name IS NULL
                           OR dm.merchant_name != m.merchant_name
                           OR dm.mcc_code != m.mcc_code
                           OR dm.city != m.city
                           OR dm.address != m.address
                    )
                    """
                    cur.execute(sql_close)
                    close_count = cur.rowcount if cur.rowcount and cur.rowcount > 0 else 0

                    # Insert new versions
                    sql_insert = """
                    INSERT INTO analytics.dim_merchant (
                        source_merchant_id, merchant_name, mcc_code, mcc_description,
                        country_code, country_name, region_code, city, address,
                        source_acquiring_partner_id, acquiring_partner_name, acquiring_partner_type,
                        effective_from, is_current, version_number
                    )
                    SELECT
                        m.merchant_id,
                        m.merchant_name,
                        m.mcc_code,
                        mc.mcc_description,
                        m.country_code,
                        co.country_name,
                        co.region_code,
                        m.city,
                        m.address,
                        ap.acquiring_partner_id,
                        ap.partner_name,
                        ap.partner_type,
                        NOW(),
                        'Y',
                        COALESCE(
                            (SELECT MAX(dm2.version_number)
                             FROM analytics.dim_merchant dm2
                             WHERE dm2.source_merchant_id = m.merchant_id),
                            0
                        ) + 1
                    FROM public.merchants m
                    LEFT JOIN public.mcc_codes mc ON mc.mcc_code = m.mcc_code
                    LEFT JOIN public.countries co ON co.country_code = m.country_code
                    LEFT JOIN public.acquiring_partners ap ON ap.acquiring_partner_id = m.acquiring_partner_id
                    LEFT JOIN analytics.dim_merchant dm 
                        ON dm.source_merchant_id = m.merchant_id
                       AND dm.is_current = 'Y'
                    WHERE dm.source_merchant_id IS NULL
                       OR dm.merchant_name != m.merchant_name
                       OR dm.mcc_code != m.mcc_code
                       OR dm.city != m.city
                       OR dm.address != m.address
                       OR dm.source_acquiring_partner_id != ap.acquiring_partner_id
                    ON CONFLICT (source_merchant_id, effective_from) DO NOTHING
                    """
                    cur.execute(sql_insert + "\nRETURNING 1")
                    returned = cur.fetchall()
                conn.commit()
                result["rows_loaded"] = len(returned) + (close_count if 'close_count' in locals() else 0)
            result["status"] = "SUCCESS"
            logger.info(f"Loaded {result['rows_loaded']} merchant dimension rows (SCD2)")
        except Exception as e:
            result["status"] = "FAILED"
            result["error"] = str(e)
            logger.error(f"Failed to load dim_merchant (SCD2): {e}", exc_info=True)

        return result
