START TRANSACTION;

-- fee_percentage stores the human percentage value, e.g. 1.2500 means 1.25%.
INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  1, NULL, NULL, ct.card_type_id, 'ECOMMERCE', 'EU', 'Y', 'LTE_24H', ic.category_id,
  1.2500, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Ecom Secure Preferred Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 1);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  2, NULL, NULL, ct.card_type_id, 'ECOMMERCE', 'EU', 'Y', 'GT_24H', ic.category_id,
  1.5000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Ecom Secure Non-Preferred Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 2);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  3, NULL, NULL, ct.card_type_id, 'ECOMMERCE', 'EU', 'N', NULL, ic.category_id,
  1.8500, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Ecom Non-Secure Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 3);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  4, NULL, NULL, ct.card_type_id, 'ECOMMERCE', 'EU', 'Y', NULL, ic.category_id,
  0.2000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Ecom Secure Debit'
WHERE ct.card_type_name = 'DEBIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 4);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  5, NULL, NULL, ct.card_type_id, 'ECOMMERCE', 'EU', 'N', NULL, ic.category_id,
  0.3000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Ecom Non-Secure Debit'
WHERE ct.card_type_name = 'DEBIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 5);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  6, NULL, NULL, ct.card_type_id, 'POS', 'EU', NULL, 'LTE_24H', ic.category_id,
  0.2000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'POS Debit Regulated'
WHERE ct.card_type_name = 'DEBIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 6);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  7, NULL, NULL, ct.card_type_id, 'POS', 'EU', NULL, 'LTE_24H', ic.category_id,
  0.9000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'POS Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 7);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  8, NULL, NULL, ct.card_type_id, 'MOTO', NULL, NULL, NULL, ic.category_id,
  1.9000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'MOTO Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 8);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  9, NULL, NULL, ct.card_type_id, 'MOTO', NULL, NULL, NULL, ic.category_id,
  0.3500, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'MOTO Debit'
WHERE ct.card_type_name = 'DEBIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 9);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  10, NULL, NULL, ct.card_type_id, NULL, 'CROSS_BORDER', NULL, NULL, ic.category_id,
  2.5000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Cross-Border Credit'
WHERE ct.card_type_name = 'CREDIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 10);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  11, NULL, NULL, ct.card_type_id, NULL, 'CROSS_BORDER', NULL, NULL, ic.category_id,
  1.0000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Cross-Border Debit'
WHERE ct.card_type_name = 'DEBIT'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 11);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  12, NULL, NULL, ct.card_type_id, NULL, NULL, NULL, NULL, ic.category_id,
  2.2000, 0.00, 'EUR'
FROM card_types ct
JOIN interchange_categories ic ON ic.category_name = 'Commercial Card'
WHERE ct.card_type_name = 'COMMERCIAL'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 12);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  13, NULL, '5411', NULL, NULL, 'EU', NULL, NULL, ic.category_id,
  0.1500, 0.00, 'EUR'
FROM interchange_categories ic
WHERE ic.category_name = 'MCC Preferred (Grocery)'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 13);

INSERT INTO interchange_rules (
  rule_priority, card_network_id, mcc_code, card_type_id, transaction_channel,
  region_code, is_3ds_required, clearing_time_condition, category_id,
  fee_percentage, fixed_fee_amount, currency_code
)
SELECT
  14, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ic.category_id,
  1.7500, 0.00, 'EUR'
FROM interchange_categories ic
WHERE ic.category_name = 'Default Standard Category'
  AND NOT EXISTS (SELECT 1 FROM interchange_rules WHERE rule_priority = 14);

COMMIT;