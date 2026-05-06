CREATE TABLE regions (
    region_code VARCHAR(30),
    region_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),

    CONSTRAINT pk_regions PRIMARY KEY (region_code),
    CONSTRAINT uq_regions_name UNIQUE (region_name)
);
-- -----------------------------------------------------------------------------
CREATE TABLE countries (
    country_code CHAR(2),
    country_name VARCHAR(100) NOT NULL,
    region_code VARCHAR(30) NOT NULL,

    CONSTRAINT pk_countries PRIMARY KEY (country_code),
    
    CONSTRAINT fk_countries_region FOREIGN KEY (region_code) REFERENCES regions (region_code),
        
    CONSTRAINT uq_countries_name UNIQUE (country_name),
    CONSTRAINT ck_countries_code CHECK (country_code REGEXP '^[A-Z]{2}$')
);
-- -----------------------------------------------------------------------------
CREATE TABLE card_types (
    card_type_id BIGINT AUTO_INCREMENT,
    card_type_name VARCHAR(30) NOT NULL,
    description VARCHAR(255),

    CONSTRAINT pk_card_types PRIMARY KEY (card_type_id),
    CONSTRAINT uq_card_types_name UNIQUE (card_type_name)
);
-- -----------------------------------------------------------------------------
CREATE TABLE mcc_codes (
    mcc_code VARCHAR(4),
    mcc_description VARCHAR(255) NOT NULL,

    CONSTRAINT pk_mcc_codes PRIMARY KEY (mcc_code),
    CONSTRAINT ck_mcc_codes_code CHECK (mcc_code REGEXP '^[0-9]{4}$')
);
-- -----------------------------------------------------------------------------
CREATE TABLE clients (
    client_id BIGINT AUTO_INCREMENT,
    client_name VARCHAR(100) NOT NULL,
    country_code CHAR(2) NOT NULL,

    CONSTRAINT pk_clients PRIMARY KEY (client_id),
    CONSTRAINT fk_clients_country FOREIGN KEY (country_code) REFERENCES countries (country_code)
);
-- -----------------------------------------------------------------------------
CREATE TABLE banks (
    bank_id BIGINT AUTO_INCREMENT,
    bank_name VARCHAR(100) NOT NULL,
    country_code CHAR(2) NOT NULL,

    CONSTRAINT pk_banks PRIMARY KEY (bank_id),

    CONSTRAINT fk_banks_country FOREIGN KEY (country_code) REFERENCES countries (country_code),
    CONSTRAINT uq_banks_name_country UNIQUE (bank_name, country_code)
);
-- -----------------------------------------------------------------------------
CREATE TABLE acquiring_partners (
    acquiring_partner_id BIGINT AUTO_INCREMENT,
    partner_name VARCHAR(100) NOT NULL,
    partner_type VARCHAR(30) NOT NULL,
    country_code CHAR(2) NOT NULL,

    CONSTRAINT pk_acquiring_partners PRIMARY KEY (acquiring_partner_id),

    CONSTRAINT fk_acquiring_partners_country FOREIGN KEY (country_code) REFERENCES countries (country_code),

    CONSTRAINT ck_acquiring_partner_type CHECK (partner_type IN ('BANK', 'PSP')),
    CONSTRAINT uq_acquiring_partner_name_country UNIQUE (partner_name, country_code)
);
-- -----------------------------------------------------------------------------
CREATE TABLE card_networks (
    card_network_id BIGINT AUTO_INCREMENT,
    network_code VARCHAR(30) NOT NULL,
    network_name VARCHAR(100) NOT NULL,

    CONSTRAINT pk_card_networks PRIMARY KEY (card_network_id),

    CONSTRAINT uq_card_networks_code UNIQUE (network_code),
    CONSTRAINT uq_card_networks_name UNIQUE (network_name)
);
-- -----------------------------------------------------------------------------
CREATE TABLE merchants (
    merchant_id BIGINT AUTO_INCREMENT,
    merchant_name VARCHAR(150) NOT NULL,
    mcc_code VARCHAR(4) NOT NULL,
    country_code CHAR(2) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    acquiring_partner_id BIGINT NOT NULL,

    CONSTRAINT pk_merchants PRIMARY KEY (merchant_id),

    CONSTRAINT fk_merchants_mcc FOREIGN KEY (mcc_code) REFERENCES mcc_codes (mcc_code),
    CONSTRAINT fk_merchants_country FOREIGN KEY (country_code) REFERENCES countries (country_code),
    CONSTRAINT fk_merchants_acquiring_partner FOREIGN KEY (acquiring_partner_id) REFERENCES acquiring_partners (acquiring_partner_id)
);
-- -----------------------------------------------------------------------------
CREATE TABLE cards (
    card_id BIGINT AUTO_INCREMENT,
    client_id BIGINT NOT NULL,
    issuer_bank_id BIGINT NOT NULL,
    card_network_id BIGINT NOT NULL,
    card_type_id BIGINT NOT NULL,
    card_product_type VARCHAR(30),

    CONSTRAINT pk_cards PRIMARY KEY (card_id),

    CONSTRAINT fk_cards_client FOREIGN KEY (client_id) REFERENCES clients (client_id),
    CONSTRAINT fk_cards_issuer_bank FOREIGN KEY (issuer_bank_id) REFERENCES banks (bank_id),
    CONSTRAINT fk_cards_network FOREIGN KEY (card_network_id) REFERENCES card_networks (card_network_id),
    CONSTRAINT fk_cards_card_type FOREIGN KEY (card_type_id) REFERENCES card_types (card_type_id)
);
-- -----------------------------------------------------------------------------
CREATE TABLE transactions (
    transaction_id BIGINT AUTO_INCREMENT,
    client_id BIGINT NOT NULL,
    merchant_id BIGINT NOT NULL,
    card_id BIGINT NOT NULL,
    acquiring_partner_id BIGINT NOT NULL,
    issuer_bank_id BIGINT NOT NULL,
    card_network_id BIGINT NOT NULL,

    transaction_amount DECIMAL(12, 2) NOT NULL,
    transaction_currency CHAR(3) NOT NULL,
    transaction_channel VARCHAR(30) NOT NULL,

    authorization_datetime TIMESTAMP NOT NULL,
    clearing_datetime TIMESTAMP,

    transaction_status VARCHAR(30) NOT NULL,
    
    is_3ds_authenticated CHAR(1) DEFAULT 'N' NOT NULL,
    eci_value VARCHAR(2),
    region_code VARCHAR(30) NOT NULL,

    CONSTRAINT pk_transactions PRIMARY KEY (transaction_id),

    CONSTRAINT fk_transactions_client FOREIGN KEY (client_id) REFERENCES clients (client_id),
    CONSTRAINT fk_transactions_merchant FOREIGN KEY (merchant_id) REFERENCES merchants (merchant_id),
    CONSTRAINT fk_transactions_card FOREIGN KEY (card_id) REFERENCES cards (card_id),
    CONSTRAINT fk_transactions_acquiring_partner FOREIGN KEY (acquiring_partner_id) REFERENCES acquiring_partners (acquiring_partner_id),
    CONSTRAINT fk_transactions_issuer_bank FOREIGN KEY (issuer_bank_id) REFERENCES banks (bank_id),
    CONSTRAINT fk_transactions_card_network FOREIGN KEY (card_network_id) REFERENCES card_networks (card_network_id),
    CONSTRAINT fk_transactions_region FOREIGN KEY (region_code) REFERENCES regions (region_code),

    CONSTRAINT ck_transactions_amount CHECK (transaction_amount > 0),
    CONSTRAINT ck_transactions_channel CHECK (transaction_channel IN ('ECOMMERCE', 'POS', 'MOTO', 'CONTACTLESS')),
    CONSTRAINT ck_transactions_status CHECK (transaction_status IN ('APPROVED', 'DECLINED', 'SETTLED')),
    CONSTRAINT ck_transactions_3ds CHECK (is_3ds_authenticated IN ('Y', 'N'))
);
-- Important note: Some fields are technically derivable from card_id or merchant_id, such as issuer_id, card_network_id, psp_id, and acquirer_id.
--
-- However, I would still store them in transactions because a transaction should preserve the exact situation at the time it happened. If a merchant changes acquirer later, old transactions should not change meaning.
-- -----------------------------------------------------------------------------
CREATE TABLE interchange_categories (
    category_id BIGINT AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),

    CONSTRAINT pk_interchange_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_interchange_categories_name UNIQUE (category_name)
);
-- -----------------------------------------------------------------------------
CREATE TABLE interchange_rules (
    rule_id BIGINT AUTO_INCREMENT,
    
    rule_priority BIGINT NOT NULL,
    
    card_network_id BIGINT,
    mcc_code VARCHAR(4),
    card_type_id BIGINT,
    transaction_channel VARCHAR(30),
    region_code VARCHAR(30),
    is_3ds_required CHAR(1),
    clearing_time_condition VARCHAR(30),
    
    category_id BIGINT NOT NULL,

    fee_percentage DECIMAL(7, 4) NOT NULL,
    fixed_fee_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL,
    currency_code CHAR(3) DEFAULT 'EUR' NOT NULL,

    CONSTRAINT pk_interchange_rules PRIMARY KEY (rule_id),

    CONSTRAINT fk_interchange_rules_network FOREIGN KEY (card_network_id) REFERENCES card_networks (card_network_id),
    CONSTRAINT fk_interchange_rules_mcc FOREIGN KEY (mcc_code) REFERENCES mcc_codes (mcc_code),
    CONSTRAINT fk_interchange_rules_card_type FOREIGN KEY (card_type_id) REFERENCES card_types (card_type_id),
    CONSTRAINT fk_interchange_rules_category FOREIGN KEY (category_id) REFERENCES interchange_categories (category_id),
    CONSTRAINT fk_interchange_rules_region FOREIGN KEY (region_code) REFERENCES regions (region_code),

    CONSTRAINT uq_interchange_rules_priority UNIQUE (rule_priority),
    CONSTRAINT ck_interchange_rules_priority CHECK (rule_priority > 0),
    CONSTRAINT ck_interchange_rules_channel CHECK (transaction_channel IS NULL OR transaction_channel IN ('ECOMMERCE', 'POS', 'MOTO', 'CONTACTLESS')),
    CONSTRAINT ck_interchange_rules_3ds_required CHECK (is_3ds_required IS NULL OR is_3ds_required IN ('Y', 'N')),
    CONSTRAINT ck_interchange_rules_clearing_condition CHECK (clearing_time_condition IS NULL OR clearing_time_condition IN ('LTE_24H', 'GT_24H')), 
                                                                                                            -- LTE_24H = lower than or equal to 24, GT_24H = greater than 24
    CONSTRAINT ck_interchange_rules_fee_percentage CHECK (fee_percentage >= 0),
    CONSTRAINT ck_interchange_rules_fixed_fee CHECK (fixed_fee_amount >= 0)
);

CREATE UNIQUE INDEX uq_interchange_rules_scope
ON interchange_rules (
    (COALESCE(card_network_id, -1)),
    (COALESCE(mcc_code, 'ANY')),
    (COALESCE(card_type_id, -1)),
    (COALESCE(transaction_channel, 'ANY')),
    (COALESCE(region_code, 'ANY')),
    (COALESCE(is_3ds_required, 'ANY')),
    (COALESCE(clearing_time_condition, 'ANY'))
);
-- -----------------------------------------------------------------------------
CREATE TABLE transaction_interchange_results (
    result_id BIGINT AUTO_INCREMENT,
    transaction_id BIGINT NOT NULL,

    result_type VARCHAR(30) NOT NULL,
    category_id BIGINT NOT NULL,
    applied_rule_id BIGINT,

    fee_percentage DECIMAL(7, 4) NOT NULL,
    fixed_fee_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL,
    interchange_fee_amount DECIMAL(12, 2) NOT NULL,

    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_transaction_interchange_results PRIMARY KEY (result_id),

    CONSTRAINT fk_txn_interchange_result_transaction FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
    CONSTRAINT fk_txn_interchange_result_category FOREIGN KEY (category_id) REFERENCES interchange_categories (category_id),
    CONSTRAINT fk_txn_interchange_result_rule FOREIGN KEY (applied_rule_id) REFERENCES interchange_rules (rule_id),

    CONSTRAINT ck_txn_interchange_result_type CHECK (result_type IN ('CURRENT', 'OPTIMAL')),
    CONSTRAINT ck_txn_interchange_fee CHECK (interchange_fee_amount >= 0)
);

CREATE UNIQUE INDEX uq_txn_interchange_result_type ON transaction_interchange_results (transaction_id, result_type);
-- -----------------------------------------------------------------------------
CREATE TABLE transaction_simulations (
    simulation_id BIGINT AUTO_INCREMENT,
    transaction_id BIGINT NOT NULL,

    simulated_is_3ds_authenticated CHAR(1),
    simulated_eci_value VARCHAR(2),
    simulated_clearing_datetime TIMESTAMP,
    simulated_region_code VARCHAR(30),
    simulation_reason VARCHAR(500),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_transaction_simulations PRIMARY KEY (simulation_id),

    CONSTRAINT fk_transaction_simulations_transaction FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
    CONSTRAINT fk_simulations_region FOREIGN KEY (simulated_region_code) REFERENCES regions (region_code),

    CONSTRAINT ck_simulations_3ds CHECK (simulated_is_3ds_authenticated IS NULL OR simulated_is_3ds_authenticated IN ('Y', 'N'))
);
-- -----------------------------------------------------------------------------
CREATE TABLE transaction_optimization_recommendations (
    recommendation_id BIGINT AUTO_INCREMENT,
    transaction_id BIGINT NOT NULL,

    recommendation_type VARCHAR(50) NOT NULL,
    recommendation_text VARCHAR(500) NOT NULL,

    current_value VARCHAR(100),
    recommended_value VARCHAR(100),

    impact_description VARCHAR(500),
    estimated_saving_amount DECIMAL(12, 2),
    estimated_saving_percentage DECIMAL(7, 4),
    priority_rank BIGINT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_txn_optimization_recommendations PRIMARY KEY (recommendation_id),

    CONSTRAINT fk_txn_recommendation_transaction FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),

    CONSTRAINT ck_txn_recommendation_saving_amount CHECK (estimated_saving_amount IS NULL OR estimated_saving_amount >= 0),
    CONSTRAINT ck_txn_recommendation_saving_pct CHECK (estimated_saving_percentage IS NULL OR estimated_saving_percentage >= 0),
    CONSTRAINT ck_txn_recommendation_priority CHECK (priority_rank IS NULL OR priority_rank > 0)
);

CREATE INDEX idx_txn_recommendations_transaction ON transaction_optimization_recommendations (transaction_id);
CREATE UNIQUE INDEX uq_txn_recommendation_type ON transaction_optimization_recommendations (transaction_id, recommendation_type);
CREATE UNIQUE INDEX uq_txn_recommendation_rank ON transaction_optimization_recommendations (transaction_id, priority_rank);
-- -----------------------------------------------------------------------------
CREATE TABLE transaction_optimization_results (
    optimization_result_id BIGINT AUTO_INCREMENT,
    transaction_id BIGINT NOT NULL,

    current_result_id BIGINT NOT NULL,
    optimal_result_id BIGINT NOT NULL,

    current_fee_amount DECIMAL(12, 2) NOT NULL,
    optimal_fee_amount DECIMAL(12, 2) NOT NULL,
    saving_amount DECIMAL(12, 2) NOT NULL,
    saving_percentage DECIMAL(7, 4),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    CONSTRAINT pk_transaction_optimization_results PRIMARY KEY (optimization_result_id),

    CONSTRAINT fk_optimization_transaction FOREIGN KEY (transaction_id) REFERENCES transactions (transaction_id),
    CONSTRAINT fk_optimization_current_result FOREIGN KEY (current_result_id) REFERENCES transaction_interchange_results (result_id),
    CONSTRAINT fk_optimization_optimal_result FOREIGN KEY (optimal_result_id) REFERENCES transaction_interchange_results (result_id),
    
    CONSTRAINT uq_optimization_transaction UNIQUE (transaction_id),
    CONSTRAINT ck_optimization_amounts CHECK (current_fee_amount >= 0 AND optimal_fee_amount >= 0 AND saving_amount >= 0),
    CONSTRAINT ck_optimization_saving_pct CHECK (saving_percentage IS NULL OR saving_percentage >= 0)
);

CREATE INDEX idx_optimization_current_result ON transaction_optimization_results (current_result_id);
CREATE INDEX idx_optimization_optimal_result ON transaction_optimization_results (optimal_result_id);