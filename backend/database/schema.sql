-- Supabase Schema for Transaction Monitoring System
-- This schema stores transactions and their rule evaluation results for dashboard display

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id TEXT UNIQUE NOT NULL,
    booking_jurisdiction TEXT NOT NULL,
    regulator TEXT NOT NULL,
    booking_datetime TIMESTAMPTZ NOT NULL,
    value_date TIMESTAMPTZ NOT NULL,
    amount DECIMAL(20, 2) NOT NULL,
    currency TEXT NOT NULL,
    channel TEXT NOT NULL,
    product_type TEXT NOT NULL,

    -- Originator information
    originator_name TEXT NOT NULL,
    originator_account TEXT NOT NULL,
    originator_country TEXT NOT NULL,

    -- Beneficiary information
    beneficiary_name TEXT NOT NULL,
    beneficiary_account TEXT NOT NULL,
    beneficiary_country TEXT NOT NULL,

    -- SWIFT information
    swift_mt TEXT NOT NULL,
    ordering_institution_bic TEXT NOT NULL,
    beneficiary_institution_bic TEXT NOT NULL,
    swift_f50_present BOOLEAN NOT NULL,
    swift_f59_present BOOLEAN NOT NULL,
    swift_f70_purpose TEXT NOT NULL,
    swift_f71_charges TEXT NOT NULL,
    travel_rule_complete BOOLEAN NOT NULL,

    -- FX information
    fx_indicator BOOLEAN NOT NULL,
    fx_base_ccy TEXT,
    fx_quote_ccy TEXT,
    fx_applied_rate DECIMAL(20, 10),
    fx_market_rate DECIMAL(20, 10),
    fx_spread_bps DECIMAL(10, 4),
    fx_counterparty TEXT,

    -- Customer information
    customer_id TEXT NOT NULL,
    customer_type TEXT NOT NULL,
    customer_risk_rating TEXT NOT NULL,
    customer_is_pep BOOLEAN NOT NULL,
    kyc_last_completed TIMESTAMPTZ,
    kyc_due_date TIMESTAMPTZ,
    edd_required BOOLEAN NOT NULL,
    edd_performed BOOLEAN NOT NULL,
    sow_documented BOOLEAN NOT NULL,

    -- Additional fields
    purpose_code TEXT NOT NULL,
    narrative TEXT NOT NULL,
    is_advised BOOLEAN NOT NULL,
    product_complex BOOLEAN NOT NULL,
    client_risk_profile TEXT NOT NULL,
    suitability_assessed BOOLEAN NOT NULL,
    suitability_result TEXT NOT NULL,
    product_has_va_exposure BOOLEAN NOT NULL,
    va_disclosure_provided BOOLEAN NOT NULL,
    cash_id_verified BOOLEAN NOT NULL,
    daily_cash_total_customer DECIMAL(20, 2) NOT NULL,
    daily_cash_txn_count INTEGER NOT NULL,
    sanctions_screening TEXT NOT NULL,
    suspicion_determined_datetime TIMESTAMPTZ,
    str_filed_datetime TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rules table
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID UNIQUE NOT NULL,
    statement TEXT NOT NULL,
    jurisdiction TEXT[] NOT NULL,
    source_url TEXT NOT NULL,
    suggested_action TEXT NOT NULL CHECK (suggested_action IN ('enhanced due diligence', 'transaction blocking', 'escalation')),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rule evaluation results table
CREATE TABLE IF NOT EXISTS rule_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    rule_id UUID NOT NULL,
    rule_statement TEXT NOT NULL,
    conditions_met BOOLEAN NOT NULL,
    confidence_score DECIMAL(3, 2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    reasoning TEXT NOT NULL,
    suggested_action TEXT NOT NULL CHECK (suggested_action IN ('enhanced due diligence', 'transaction blocking', 'escalation')),
    evaluated_at TIMESTAMPTZ NOT NULL,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Ensure unique evaluation per transaction-rule pair
    UNIQUE(transaction_id, rule_id)
);

-- Batch evaluation summary table (stores the overall evaluation result)
CREATE TABLE IF NOT EXISTS batch_evaluations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    total_rules_evaluated INTEGER NOT NULL,
    violated_rules_count INTEGER NOT NULL,
    passed_rules_count INTEGER NOT NULL,
    overall_risk_level TEXT NOT NULL CHECK (overall_risk_level IN ('low', 'medium', 'high')),
    requires_action BOOLEAN NOT NULL,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_booking_datetime ON transactions(booking_datetime DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);
CREATE INDEX IF NOT EXISTS idx_transactions_currency ON transactions(currency);
CREATE INDEX IF NOT EXISTS idx_transactions_booking_jurisdiction ON transactions(booking_jurisdiction);

CREATE INDEX IF NOT EXISTS idx_rule_evaluations_transaction_id ON rule_evaluations(transaction_id);
CREATE INDEX IF NOT EXISTS idx_rule_evaluations_rule_id ON rule_evaluations(rule_id);
CREATE INDEX IF NOT EXISTS idx_rule_evaluations_conditions_met ON rule_evaluations(conditions_met);
CREATE INDEX IF NOT EXISTS idx_rule_evaluations_evaluated_at ON rule_evaluations(evaluated_at DESC);

CREATE INDEX IF NOT EXISTS idx_batch_evaluations_transaction_id ON batch_evaluations(transaction_id);
CREATE INDEX IF NOT EXISTS idx_batch_evaluations_risk_level ON batch_evaluations(overall_risk_level);
CREATE INDEX IF NOT EXISTS idx_batch_evaluations_requires_action ON batch_evaluations(requires_action);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update updated_at
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rules_updated_at
    BEFORE UPDATE ON rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batch_evaluations_updated_at
    BEFORE UPDATE ON batch_evaluations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
