-- Migration: Add UNIQUE constraint to batch_evaluations.transaction_id
-- This allows upsert operations on the batch_evaluations table

-- Add UNIQUE constraint to transaction_id column
ALTER TABLE batch_evaluations
  ADD CONSTRAINT batch_evaluations_transaction_id_key UNIQUE (transaction_id);
