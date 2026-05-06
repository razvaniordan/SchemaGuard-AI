USE schemaguard_ai;

START TRANSACTION;

INSERT IGNORE INTO regions (region_code, region_name, description) VALUES
  ('EU', 'EU / EEA Region', 'Regulated European region used for interchange classification.'),
  ('CROSS_BORDER', 'Cross-Border', 'Transactions where issuer and acquirer are in different regions or outside the EU/EEA region.');

-- Countries for EU region
-- Includes EU member states plus EEA countries Iceland, Liechtenstein, and Norway,
-- because the project documentation defines the EU region as EEA-style regulated coverage.
INSERT IGNORE INTO countries (country_code, country_name, region_code) VALUES
  ('AT', 'Austria', 'EU'),
  ('BE', 'Belgium', 'EU'),
  ('BG', 'Bulgaria', 'EU'),
  ('HR', 'Croatia', 'EU'),
  ('CY', 'Cyprus', 'EU'),
  ('CZ', 'Czechia', 'EU'),
  ('DK', 'Denmark', 'EU'),
  ('EE', 'Estonia', 'EU'),
  ('FI', 'Finland', 'EU'),
  ('FR', 'France', 'EU'),
  ('DE', 'Germany', 'EU'),
  ('GR', 'Greece', 'EU'),
  ('HU', 'Hungary', 'EU'),
  ('IE', 'Ireland', 'EU'),
  ('IT', 'Italy', 'EU'),
  ('LV', 'Latvia', 'EU'),
  ('LT', 'Lithuania', 'EU'),
  ('LU', 'Luxembourg', 'EU'),
  ('MT', 'Malta', 'EU'),
  ('NL', 'Netherlands', 'EU'),
  ('PL', 'Poland', 'EU'),
  ('PT', 'Portugal', 'EU'),
  ('RO', 'Romania', 'EU'),
  ('SK', 'Slovakia', 'EU'),
  ('SI', 'Slovenia', 'EU'),
  ('ES', 'Spain', 'EU'),
  ('SE', 'Sweden', 'EU'),
  ('IS', 'Iceland', 'EU'),
  ('LI', 'Liechtenstein', 'EU'),
  ('NO', 'Norway', 'EU');


INSERT IGNORE INTO card_types (card_type_name, description) VALUES
  ('CREDIT', 'Consumer credit card.'),
  ('DEBIT', 'Consumer debit card.'),
  ('PREPAID', 'Prepaid card.'),
  ('COMMERCIAL', 'Business, corporate or commercial card.');


INSERT IGNORE INTO mcc_codes (mcc_code, mcc_description) VALUES
  ('5411', 'Grocery Stores / Supermarkets');


-- Issuing banks from Romania only for now
INSERT IGNORE INTO banks (bank_name, country_code) VALUES
  ('Banca Transilvania', 'RO'),
  ('BRD', 'RO'),
  ('BCR', 'RO'),
  ('Raiffeisen', 'RO'),
  ('CEC Bank', 'RO');


INSERT IGNORE INTO acquiring_partners (partner_name, partner_type, country_code) VALUES
  ('Banca Transilvania', 'BANK', 'RO'),
  ('BRD', 'BANK', 'RO'),
  ('BCR', 'BANK', 'RO'),
  ('Raiffeisen', 'BANK', 'RO'),
  ('UniCredit', 'BANK', 'RO'),
  ('CEC Bank', 'BANK', 'RO'),
  ('Netopia', 'PSP', 'RO'),
  ('EuPlatesc', 'PSP', 'RO'),
  ('PayU Romania', 'PSP', 'RO'),
  ('Adyen', 'PSP', 'NL');


INSERT IGNORE INTO card_networks (network_code, network_name) VALUES
  ('VISA', 'Visa'),
  ('MASTERCARD', 'Mastercard');


INSERT IGNORE INTO interchange_categories (category_name, description) VALUES
  ('Ecom Secure Preferred Credit', 'eCommerce credit transaction with 3DS and clearing within 24 hours.'),
  ('Ecom Secure Non-Preferred Credit', 'eCommerce credit transaction with 3DS but clearing after 24 hours.'),
  ('Ecom Non-Secure Credit', 'eCommerce credit transaction without 3DS authentication.'),
  ('Ecom Secure Debit', 'eCommerce debit transaction with 3DS authentication.'),
  ('Ecom Non-Secure Debit', 'eCommerce debit transaction without 3DS authentication.'),
  ('POS Debit Regulated', 'Card-present POS debit transaction in the regulated EU/EEA region.'),
  ('POS Credit', 'Card-present POS credit transaction in the regulated EU/EEA region.'),
  ('MOTO Credit', 'Mail order / telephone order credit transaction.'),
  ('MOTO Debit', 'Mail order / telephone order debit transaction.'),
  ('Cross-Border Credit', 'Cross-border credit transaction.'),
  ('Cross-Border Debit', 'Cross-border debit transaction.'),
  ('Commercial Card', 'Commercial, business, or corporate card transaction.'),
  ('MCC Preferred (Grocery)', 'Preferred grocery MCC 5411 category.'),
  ('Default Standard Category', 'Fallback category when no specific rule applies.');

COMMIT;