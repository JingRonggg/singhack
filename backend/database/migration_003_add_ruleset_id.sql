-- Migration 003: Add ruleset_id to rules table for tracking crawls
-- This allows us to keep old rules and query only the latest crawl

-- Add ruleset_id column to rules table
ALTER TABLE rules
ADD COLUMN IF NOT EXISTS ruleset_id UUID;

-- Create index for efficient querying by ruleset_id
CREATE INDEX IF NOT EXISTS idx_rules_ruleset_id ON rules(ruleset_id);

-- Create index for finding latest ruleset efficiently
CREATE INDEX IF NOT EXISTS idx_rules_created_at ON rules(created_at DESC);

-- Add comment to document the column
COMMENT ON COLUMN rules.ruleset_id IS 'UUID linking rules to a specific web crawl/extraction batch. Rules from the same crawl share the same ruleset_id.';
