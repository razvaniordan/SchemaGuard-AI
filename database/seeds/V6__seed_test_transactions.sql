-- =============================================================================
-- V6: Seed 500 Test Transactions with Normal and Anomaly Patterns
-- =============================================================================
-- This migration populates the operational database with 500 test transactions
-- covering normal scenarios and anomalies for comprehensive ETL, ML, and
-- analytics testing.
--
-- Scenario Coverage:
-- - NORMAL (MCC preferred, standard debit)
-- - NO_3DS_ECOM (eCommerce without 3D Secure)
-- - DELAYED_CLEARING (clearing > 24 hours)
-- - CROSS_BORDER (transactions in cross-border region)
-- - MOTO (mail order / telephone order)
-- - COMMERCIAL (commercial/business cards)
-- - POS_BASELINE (point-of-sale transactions)
-- - HIGH_VALUE_OUTLIER (high-amount outliers for anomaly detection)
-- - DECLINED_NO_CLEARING (declined transactions without clearing)
-- - CONTACTLESS_MIX (contactless POS transactions)
--
-- Each scenario includes:
-- - 50 transactions with realistic amounts and timing
-- - Correct CURRENT and OPTIMAL interchange results
-- - Optimization savings calculations
-- - Top-priority recommendations where applicable
--
-- ETL Impact:
-- - ETL will load these into analytics.fact_transaction_analysis
-- - Dimension loaders will ensure all FK relationships are satisfied
-- - Watermark tracking enables incremental testing
-- =============================================================================

BEGIN;

-- 1) Extend MCC universe for richer testing (fallback/default and category transitions)
INSERT INTO mcc_codes (mcc_code, mcc_description) VALUES
  ('5732', 'Electronics Stores'),
  ('5999', 'Miscellaneous Retail'),
  ('7011', 'Hotels / Accommodation'),
  ('4111', 'Local and Suburban Commuter Passenger Transportation')
ON CONFLICT (mcc_code) DO NOTHING;

-- 2) Create deterministic load-test clients (idempotent by name)
WITH client_pool AS (
  SELECT
    gs,
    'LoadTest Client ' ||
    (ARRAY['Oliver','Liam','Noah','William','James','Henry','Lucas','Mason','Ethan','Alexander','Michael','Daniel','Jacob','Logan','Matthew','Owen'])[((gs-1) % array_length(ARRAY['Oliver','Liam','Noah','William','James','Henry','Lucas','Mason','Ethan','Alexander','Michael','Daniel','Jacob','Logan','Matthew','Owen'], 1)) + 1]
      || ' ' ||
    (ARRAY['Popescu','Ionescu','Georgescu','Popa','Stan','Mivovanu','Lupului','Macanache','Anghel','Lupoae','Pascan','Gorganeanu','Mutu','Stirbu','Anghelescu','Ronaldo','Badea'])[(((gs-1) / array_length(ARRAY['Popescu','Ionescu','Georgescu','Popa','Stan','Mivovanu','Lupului','Macanache','Anghel','Lupoae','Pascan','Gorganeanu','Mutu','Stirbu','Anghelescu','Ronaldo','Badea'], 1)) % array_length(ARRAY['Popescu','Ionescu','Georgescu','Popa','Stan'], 1)) + 1] AS client_name,
    (ARRAY['RO','RO','RO','NL','DE','FR','ES','IT'])[(gs % 8) + 1] AS country_code
  FROM generate_series(1, 80) AS gs
)
INSERT INTO clients (client_name, country_code)
SELECT client_name, country_code
FROM client_pool cp
WHERE NOT EXISTS (
  SELECT 1 FROM clients c WHERE c.client_name = cp.client_name
);

-- 3) Create deterministic load-test merchants (idempotent by merchant_name + address check)
--    (no unique constraint exists on merchants table, so we protect manually)
WITH merchant_pool AS (
  SELECT
    gs,
    'LoadTest Merchant ' ||
    (ARRAY[
      'Bucharest Market','Cluj Grocers','EuroFresh','CityFresh','Green Basket','DailyMart',
      'ElectroMart','TechHub','GadgetWorld','DeviceHouse','Electronica','CircuitShop',
      'Bazaar Misc','CornerShop','GeneralStore','VarietyPlus','MarketplaceX','AllGoods',
      'Hotel Grand','StayCentral','CityLodge','UrbanInn','Comfort Suites','RegalHotel',
      'MetroTransit','CityTaxi','CommuterLines','RideExpress','LocalTransit','TramWorks'
    ])[((gs - 1) % array_length(ARRAY[
      'Bucharest Market','Cluj Grocers','EuroFresh','CityFresh','Green Basket','DailyMart',
      'ElectroMart','TechHub','GadgetWorld','DeviceHouse','Electronica','CircuitShop',
      'Bazaar Misc','CornerShop','GeneralStore','VarietyPlus','MarketplaceX','AllGoods',
      'Hotel Grand','StayCentral','CityLodge','UrbanInn','Comfort Suites','RegalHotel',
      'MetroTransit','CityTaxi','CommuterLines','RideExpress','LocalTransit','TramWorks'
    ], 1)) + 1] AS merchant_name,
    (ARRAY['5411','5732','5999','7011','4111'])[((gs - 1) % array_length(ARRAY['5411','5732','5999','7011','4111'], 1)) + 1] AS mcc_code,
    (ARRAY['RO','RO','NL','DE','FR'])[((gs - 1) % array_length(ARRAY['RO','RO','NL','DE','FR'], 1)) + 1] AS country_code,
    (ARRAY['Bucharest','Cluj','Amsterdam','Berlin','Paris'])[((gs - 1) % array_length(ARRAY['Bucharest','Cluj','Amsterdam','Berlin','Paris'], 1)) + 1] AS city,
    'Seed St ' || gs AS address,
    ap.acquiring_partner_id
  FROM generate_series(1, 30) gs
  JOIN LATERAL (
    SELECT acquiring_partner_id
    FROM acquiring_partners
    ORDER BY acquiring_partner_id
    LIMIT 1 OFFSET (gs % (SELECT COUNT(*) FROM acquiring_partners))
  ) ap ON TRUE
)
INSERT INTO merchants (
  merchant_name, mcc_code, country_code, city, address, acquiring_partner_id
)
SELECT merchant_name, mcc_code, country_code, city, address, acquiring_partner_id
FROM merchant_pool mp
WHERE NOT EXISTS (
  SELECT 1 FROM merchants m WHERE m.merchant_name = mp.merchant_name AND m.address = mp.address
);

-- 4) Create one test card per load-test client (if client has no card yet)
WITH base_clients AS (
  SELECT c.client_id, ROW_NUMBER() OVER (ORDER BY c.client_id) AS rn
  FROM clients c
  WHERE c.client_name LIKE 'LoadTest Client %'
),
bank_pool AS (
  SELECT b.bank_id, ROW_NUMBER() OVER (ORDER BY b.bank_id) AS rn
  FROM banks b
),
network_pool AS (
  SELECT n.card_network_id, ROW_NUMBER() OVER (ORDER BY n.card_network_id) AS rn
  FROM card_networks n
),
type_pool AS (
  SELECT t.card_type_id, t.card_type_name, ROW_NUMBER() OVER (ORDER BY t.card_type_id) AS rn
  FROM card_types t
)
INSERT INTO cards (client_id, issuer_bank_id, card_network_id, card_type_id, card_product_type)
SELECT
  bc.client_id,
  bp.bank_id,
  np.card_network_id,
  tp.card_type_id,
  CASE
    WHEN tp.card_type_name = 'CREDIT' THEN 'CONSUMER_STANDARD'
    WHEN tp.card_type_name = 'DEBIT' THEN 'DEBIT_STANDARD'
    WHEN tp.card_type_name = 'COMMERCIAL' THEN 'BUSINESS_CORP'
    ELSE 'PREPAID_BASIC'
  END
FROM base_clients bc
JOIN bank_pool bp
  ON bp.rn = ((bc.rn - 1) % (SELECT COUNT(*) FROM bank_pool)) + 1
JOIN network_pool np
  ON np.rn = ((bc.rn - 1) % (SELECT COUNT(*) FROM network_pool)) + 1
JOIN type_pool tp
  ON tp.rn = ((bc.rn - 1) % (SELECT COUNT(*) FROM type_pool)) + 1
WHERE NOT EXISTS (
  SELECT 1 FROM cards c WHERE c.client_id = bc.client_id
);

-- 5) Build 500 scenario rows in temp table
DROP TABLE IF EXISTS tmp_scenarios;
CREATE TEMP TABLE tmp_scenarios AS
WITH
load_cards AS (
  SELECT
    ca.card_id,
    ca.client_id,
    ca.issuer_bank_id,
    ca.card_network_id,
    ct.card_type_name,
    ROW_NUMBER() OVER (ORDER BY ca.card_id) AS rn
  FROM cards ca
  JOIN clients cl ON cl.client_id = ca.client_id
  JOIN card_types ct ON ct.card_type_id = ca.card_type_id
  WHERE cl.client_name LIKE 'LoadTest Client %'
),
load_merchants AS (
  SELECT
    m.merchant_id,
    m.mcc_code,
    m.acquiring_partner_id,
    m.country_code,
    ROW_NUMBER() OVER (ORDER BY m.merchant_id) AS rn
  FROM merchants m
  WHERE m.merchant_name LIKE 'LoadTest Merchant %'
),
card_count AS (SELECT COUNT(*) AS cnt FROM load_cards),
merchant_count AS (SELECT COUNT(*) AS cnt FROM load_merchants)
SELECT
  gs AS scenario_no,
  lc.client_id,
  lc.card_id,
  lm.merchant_id,
  lm.mcc_code,
  lm.acquiring_partner_id,
  lc.issuer_bank_id,
  lc.card_network_id,
  CASE WHEN gs % 10 IN (3,7) THEN 'CROSS_BORDER' ELSE 'EU' END AS region_code,
  CASE
    WHEN gs % 10 = 4 THEN 'MOTO'
    WHEN gs % 10 = 6 THEN 'POS'
    WHEN gs % 10 = 9 THEN 'CONTACTLESS'
    ELSE 'ECOMMERCE'
  END AS transaction_channel,
  CASE
    WHEN gs % 10 = 8 THEN 'DECLINED'
    ELSE 'SETTLED'
  END AS transaction_status,
  CASE
    WHEN gs % 10 IN (1,5,8) THEN 'N'
    ELSE 'Y'
  END AS is_3ds_authenticated,
  CASE
    WHEN gs % 10 IN (1,5,8) THEN '07'
    ELSE '05'
  END AS eci_value,
  CASE
    WHEN gs % 10 = 7 THEN (15000 + gs * 3)::NUMERIC(12,2)   -- outlier amount
    WHEN gs % 10 = 5 THEN (3500 + gs * 2)::NUMERIC(12,2)    -- commercial-like high values
    ELSE (20 + (gs * 13 % 900))::NUMERIC(12,2)
  END AS transaction_amount,
  'EUR'::CHAR(3) AS transaction_currency,
  dt.base_authorization_datetime AS authorization_datetime,
  CASE
    WHEN gs % 10 = 8 THEN NULL  -- declined/no clearing
    WHEN gs % 10 IN (2,3) THEN dt.base_authorization_datetime + INTERVAL '36 hours'
    WHEN gs % 10 = 4 THEN dt.base_authorization_datetime + INTERVAL '30 hours'
    ELSE dt.base_authorization_datetime + INTERVAL '8 hours'
  END AS clearing_datetime,
  lc.card_type_name,
  CASE
    WHEN gs % 10 = 0 THEN 'NORMAL'
    WHEN gs % 10 = 1 THEN 'NO_3DS_ECOM'
    WHEN gs % 10 = 2 THEN 'DELAYED_CLEARING'
    WHEN gs % 10 = 3 THEN 'CROSS_BORDER'
    WHEN gs % 10 = 4 THEN 'MOTO'
    WHEN gs % 10 = 5 THEN 'COMMERCIAL'
    WHEN gs % 10 = 6 THEN 'POS_BASELINE'
    WHEN gs % 10 = 7 THEN 'HIGH_VALUE_OUTLIER'
    WHEN gs % 10 = 8 THEN 'DECLINED_NO_CLEARING'
    ELSE 'CONTACTLESS_MIX'
  END AS scenario_code
FROM generate_series(1, 500) gs
JOIN card_count cc ON TRUE
JOIN merchant_count mc ON TRUE
JOIN LATERAL (
  -- Deterministic pseudo-random distribution across years/months for dashboard testing.
  SELECT make_timestamp(
    2020 + ((gs * 17) % 7),   -- 2020..2026
    1 + ((gs * 29) % 12),     -- month 1..12
    1 + ((gs * 31) % 28),     -- day 1..28 (safe for all months)
    (gs * 7) % 24,
    (gs * 11) % 60,
    (gs * 13) % 60
  ) AS base_authorization_datetime
) dt ON TRUE
JOIN load_cards lc
  ON lc.rn = ((gs - 1) % cc.cnt) + 1
JOIN load_merchants lm
  ON lm.rn = ((gs * 3 - 1) % mc.cnt) + 1;

-- 6) Insert transactions and keep mapping
INSERT INTO transactions (
  client_id,
  merchant_id,
  mcc_code,
  card_id,
  acquiring_partner_id,
  issuer_bank_id,
  card_network_id,
  transaction_amount,
  transaction_currency,
  transaction_channel,
  authorization_datetime,
  clearing_datetime,
  transaction_status,
  is_3ds_authenticated,
  eci_value,
  region_code
)
SELECT
  s.client_id,
  s.merchant_id,
  s.mcc_code,
  s.card_id,
  s.acquiring_partner_id,
  s.issuer_bank_id,
  s.card_network_id,
  s.transaction_amount,
  s.transaction_currency,
  s.transaction_channel,
  s.authorization_datetime,
  s.clearing_datetime,
  s.transaction_status,
  s.is_3ds_authenticated,
  s.eci_value,
  s.region_code
FROM tmp_scenarios s;

-- 6b) Create mapping of scenarios to inserted transactions
DROP TABLE IF EXISTS tmp_txn_map;
CREATE TEMP TABLE tmp_txn_map AS
SELECT
  s.*,
  t.transaction_id
FROM tmp_scenarios s
JOIN transactions t
  ON t.client_id = s.client_id
 AND t.merchant_id = s.merchant_id
 AND t.card_id = s.card_id
 AND t.authorization_datetime = s.authorization_datetime
 AND t.transaction_amount = s.transaction_amount;

-- 7) Insert CURRENT results
INSERT INTO transaction_interchange_results (
  transaction_id,
  result_type,
  category_id,
  applied_rule_id,
  fee_percentage,
  fixed_fee_amount,
  interchange_fee_amount,
  evaluated_at
)
SELECT
  tm.transaction_id,
  'CURRENT',
  ic.category_id,
  NULL,
  x.current_fee_pct,
  0.00,
  ROUND(tm.transaction_amount * x.current_fee_pct / 100.0, 2),
  NOW()
FROM tmp_txn_map tm
JOIN LATERAL (
  SELECT
    CASE tm.scenario_code
      WHEN 'NORMAL' THEN 'MCC Preferred (Grocery)'
      WHEN 'NO_3DS_ECOM' THEN 'Ecom Non-Secure Credit'
      WHEN 'DELAYED_CLEARING' THEN 'Ecom Secure Non-Preferred Credit'
      WHEN 'CROSS_BORDER' THEN 'Cross-Border Credit'
      WHEN 'MOTO' THEN 'MOTO Credit'
      WHEN 'COMMERCIAL' THEN 'Commercial Card'
      WHEN 'POS_BASELINE' THEN 'POS Credit'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'Default Standard Category'
      WHEN 'DECLINED_NO_CLEARING' THEN 'Default Standard Category'
      ELSE 'POS Credit'
    END AS current_category_name,
    CASE tm.scenario_code
      WHEN 'NORMAL' THEN 0.1500
      WHEN 'NO_3DS_ECOM' THEN 1.8500
      WHEN 'DELAYED_CLEARING' THEN 1.5000
      WHEN 'CROSS_BORDER' THEN 2.5000
      WHEN 'MOTO' THEN 1.9000
      WHEN 'COMMERCIAL' THEN 2.2000
      WHEN 'POS_BASELINE' THEN 0.9000
      WHEN 'HIGH_VALUE_OUTLIER' THEN 1.7500
      WHEN 'DECLINED_NO_CLEARING' THEN 1.7500
      ELSE 0.9000
    END::NUMERIC(7,4) AS current_fee_pct
) x ON TRUE
JOIN interchange_categories ic
  ON ic.category_name = x.current_category_name;

-- 8) Insert OPTIMAL results
INSERT INTO transaction_interchange_results (
  transaction_id,
  result_type,
  category_id,
  applied_rule_id,
  fee_percentage,
  fixed_fee_amount,
  interchange_fee_amount,
  evaluated_at
)
SELECT
  tm.transaction_id,
  'OPTIMAL',
  ic.category_id,
  NULL,
  x.optimal_fee_pct,
  0.00,
  ROUND(tm.transaction_amount * x.optimal_fee_pct / 100.0, 2),
  NOW()
FROM tmp_txn_map tm
JOIN LATERAL (
  SELECT
    CASE tm.scenario_code
      WHEN 'NORMAL' THEN 'MCC Preferred (Grocery)'
      WHEN 'NO_3DS_ECOM' THEN 'Ecom Secure Preferred Credit'
      WHEN 'DELAYED_CLEARING' THEN 'Ecom Secure Preferred Credit'
      WHEN 'CROSS_BORDER' THEN 'Ecom Secure Preferred Credit'
      WHEN 'MOTO' THEN 'Ecom Secure Preferred Credit'
      WHEN 'COMMERCIAL' THEN 'POS Credit'
      WHEN 'POS_BASELINE' THEN 'POS Debit Regulated'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'MCC Preferred (Grocery)'
      WHEN 'DECLINED_NO_CLEARING' THEN 'Default Standard Category'
      ELSE 'POS Debit Regulated'
    END AS optimal_category_name,
    CASE tm.scenario_code
      WHEN 'NORMAL' THEN 0.1500
      WHEN 'NO_3DS_ECOM' THEN 1.2500
      WHEN 'DELAYED_CLEARING' THEN 1.2500
      WHEN 'CROSS_BORDER' THEN 1.2500
      WHEN 'MOTO' THEN 1.2500
      WHEN 'COMMERCIAL' THEN 0.9000
      WHEN 'POS_BASELINE' THEN 0.2000
      WHEN 'HIGH_VALUE_OUTLIER' THEN 0.1500
      WHEN 'DECLINED_NO_CLEARING' THEN 1.7500
      ELSE 0.2000
    END::NUMERIC(7,4) AS optimal_fee_pct
) x ON TRUE
JOIN interchange_categories ic
  ON ic.category_name = x.optimal_category_name;

-- 9) Insert optimization summary per transaction
INSERT INTO transaction_optimization_results (
  transaction_id,
  current_result_id,
  optimal_result_id,
  current_fee_amount,
  optimal_fee_amount,
  saving_amount,
  saving_percentage,
  created_at
)
SELECT
  c.transaction_id,
  c.result_id AS current_result_id,
  o.result_id AS optimal_result_id,
  c.interchange_fee_amount AS current_fee_amount,
  o.interchange_fee_amount AS optimal_fee_amount,
  GREATEST(c.interchange_fee_amount - o.interchange_fee_amount, 0) AS saving_amount,
  CASE
    WHEN c.interchange_fee_amount > 0
    THEN ROUND(
      (GREATEST(c.interchange_fee_amount - o.interchange_fee_amount, 0) / c.interchange_fee_amount) * 100.0,
      4
    )
    ELSE NULL
  END AS saving_percentage,
  NOW()
FROM transaction_interchange_results c
JOIN transaction_interchange_results o
  ON o.transaction_id = c.transaction_id
 AND o.result_type = 'OPTIMAL'
WHERE c.result_type = 'CURRENT'
ON CONFLICT (transaction_id) DO UPDATE SET
  current_result_id = EXCLUDED.current_result_id,
  optimal_result_id = EXCLUDED.optimal_result_id,
  current_fee_amount = EXCLUDED.current_fee_amount,
  optimal_fee_amount = EXCLUDED.optimal_fee_amount,
  saving_amount = EXCLUDED.saving_amount,
  saving_percentage = EXCLUDED.saving_percentage,
  created_at = NOW();

-- 10) Insert top recommendation for scenarios that should have actionable optimization
INSERT INTO transaction_optimization_recommendations (
  transaction_id,
  recommendation_type,
  recommendation_text,
  current_value,
  recommended_value,
  impact_description,
  estimated_saving_amount,
  estimated_saving_percentage,
  priority_rank,
  created_at
)
SELECT
  tm.transaction_id,
  rec.recommendation_type,
  rec.recommendation_text,
  rec.current_value,
  rec.recommended_value,
  rec.impact_description,
  tor.saving_amount,
  tor.saving_percentage,
  1,
  NOW()
FROM tmp_txn_map tm
JOIN transaction_optimization_results tor
  ON tor.transaction_id = tm.transaction_id
JOIN LATERAL (
  SELECT
    CASE tm.scenario_code
      WHEN 'NO_3DS_ECOM' THEN 'ENABLE_3DS'
      WHEN 'DELAYED_CLEARING' THEN 'FASTER_CLEARING'
      WHEN 'CROSS_BORDER' THEN 'ROUTE_TO_EU_ACQUIRER'
      WHEN 'MOTO' THEN 'SHIFT_MOTO_TO_ECOM'
      WHEN 'COMMERCIAL' THEN 'REVIEW_CARD_PRODUCT'
      WHEN 'POS_BASELINE' THEN 'DEBIT_OPTIMIZATION'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'MCC_OPTIMIZATION'
      WHEN 'CONTACTLESS_MIX' THEN 'CONTACTLESS_DEBIT_ROUTING'
      ELSE NULL
    END AS recommendation_type,
    CASE tm.scenario_code
      WHEN 'NO_3DS_ECOM' THEN 'Enable 3DS authentication for eCommerce transactions.'
      WHEN 'DELAYED_CLEARING' THEN 'Submit clearing within 24h to qualify for better fee tier.'
      WHEN 'CROSS_BORDER' THEN 'Route through regulated EU acquiring setup where possible.'
      WHEN 'MOTO' THEN 'Migrate eligible MOTO flows to authenticated eCommerce.'
      WHEN 'COMMERCIAL' THEN 'Review commercial product usage on this flow.'
      WHEN 'POS_BASELINE' THEN 'Prefer debit routing for lower regulated fee.'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'Validate MCC setup; transaction appears downgraded.'
      WHEN 'CONTACTLESS_MIX' THEN 'Tune contactless routing for debit qualification.'
      ELSE NULL
    END AS recommendation_text,
    CASE tm.scenario_code
      WHEN 'NO_3DS_ECOM' THEN 'is_3ds_authenticated=N'
      WHEN 'DELAYED_CLEARING' THEN 'clearing_time=GT_24H'
      WHEN 'CROSS_BORDER' THEN 'region=CROSS_BORDER'
      WHEN 'MOTO' THEN 'channel=MOTO'
      WHEN 'COMMERCIAL' THEN 'card_type=COMMERCIAL'
      WHEN 'POS_BASELINE' THEN 'category=POS Credit'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'category=Default Standard'
      WHEN 'CONTACTLESS_MIX' THEN 'category=POS Credit'
      ELSE NULL
    END AS current_value,
    CASE tm.scenario_code
      WHEN 'NO_3DS_ECOM' THEN 'is_3ds_authenticated=Y'
      WHEN 'DELAYED_CLEARING' THEN 'clearing_time=LTE_24H'
      WHEN 'CROSS_BORDER' THEN 'region=EU'
      WHEN 'MOTO' THEN 'channel=ECOMMERCE+3DS'
      WHEN 'COMMERCIAL' THEN 'card_type=CREDIT/DEBIT where eligible'
      WHEN 'POS_BASELINE' THEN 'category=POS Debit Regulated'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'category=MCC Preferred'
      WHEN 'CONTACTLESS_MIX' THEN 'category=POS Debit Regulated'
      ELSE NULL
    END AS recommended_value,
    CASE tm.scenario_code
      WHEN 'NO_3DS_ECOM' THEN 'Expected downgrade avoidance and better fee percentage.'
      WHEN 'DELAYED_CLEARING' THEN 'Expected qualification to preferred clearing tier.'
      WHEN 'CROSS_BORDER' THEN 'Expected lower regional fee profile.'
      WHEN 'MOTO' THEN 'Expected lower secure eCommerce fee profile.'
      WHEN 'COMMERCIAL' THEN 'Expected reduced fee profile on eligible traffic.'
      WHEN 'POS_BASELINE' THEN 'Expected debit regulated fee qualification.'
      WHEN 'HIGH_VALUE_OUTLIER' THEN 'Expected major reduction from fallback category.'
      WHEN 'CONTACTLESS_MIX' THEN 'Expected lower POS debit fee.'
      ELSE NULL
    END AS impact_description
) rec ON TRUE
WHERE rec.recommendation_type IS NOT NULL
  AND tor.saving_amount > 0
ON CONFLICT (transaction_id, recommendation_type) DO UPDATE SET
  recommendation_text = EXCLUDED.recommendation_text,
  current_value = EXCLUDED.current_value,
  recommended_value = EXCLUDED.recommended_value,
  impact_description = EXCLUDED.impact_description,
  estimated_saving_amount = EXCLUDED.estimated_saving_amount,
  estimated_saving_percentage = EXCLUDED.estimated_saving_percentage,
  priority_rank = EXCLUDED.priority_rank,
  created_at = NOW();

COMMIT;
