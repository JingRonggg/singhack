-- Migration: Make booking_datetime and value_date nullable
-- This allows storing transactions even when date parsing fails

ALTER TABLE transactions
  ALTER COLUMN booking_datetime DROP NOT NULL,
  ALTER COLUMN value_date DROP NOT NULL;
