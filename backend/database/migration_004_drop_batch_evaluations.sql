-- Migration 004: Drop batch_evaluations table
-- This table is no longer needed as all evaluation data is available through rule_evaluations

-- Drop the batch_evaluations table and its constraints
DROP TABLE IF EXISTS batch_evaluations CASCADE;

-- Drop any related indexes
DROP INDEX IF EXISTS idx_batch_evaluations_transaction_id;
DROP INDEX IF EXISTS idx_batch_evaluations_risk_level;
DROP INDEX IF EXISTS idx_batch_evaluations_requires_action;

-- Note: The rule_evaluations table contains all the data needed to reconstruct
-- batch evaluation summaries through aggregation queries
