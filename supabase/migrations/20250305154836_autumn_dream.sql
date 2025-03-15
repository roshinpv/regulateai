/*
  # Update database to focus on Wells Fargo

  1. Changes
    - Remove all banks except Wells Fargo
    - Update regulations to be specific to Wells Fargo
    - Update compliance alerts and regulatory updates
    - Adjust relationships and references

  2. Security
    - Maintain existing RLS policies
    - Update bank-specific policies for Wells Fargo

  3. Data Migration
    - Preserve Wells Fargo data
    - Clean up other bank data
    - Update related records
*/

-- First, save Wells Fargo data
DO $$ 
BEGIN
  -- Create temporary table for Wells Fargo data
  CREATE TEMP TABLE wells_fargo_data AS
  SELECT * FROM banks WHERE name = 'Wells Fargo';
END $$;

-- Remove all banks except Wells Fargo
DELETE FROM banks WHERE name != 'Wells Fargo';

-- Update bank_regulation table to only keep Wells Fargo relationships
DELETE FROM bank_regulation 
WHERE bank_id NOT IN (SELECT id FROM banks WHERE name = 'Wells Fargo');

-- Update regulations to focus on Wells Fargo
UPDATE regulations
SET summary = CASE id
  WHEN 'reg-001' THEN 'Basel III requirements specifically affecting Wells Fargo as a Global Systemically Important Bank (G-SIB), including capital adequacy and stress testing requirements.'
  WHEN 'reg-002' THEN 'Dodd-Frank Act compliance requirements for Wells Fargo, focusing on risk management and regulatory reporting obligations.'
  WHEN 'reg-003' THEN 'Fair lending practices and requirements specific to Wells Fargo''s retail and commercial banking operations.'
  WHEN 'reg-004' THEN 'Anti-money laundering requirements and procedures for Wells Fargo''s global banking operations.'
  WHEN 'reg-005' THEN 'Consumer protection requirements specific to Wells Fargo''s retail banking and lending services.'
  ELSE summary
END;

-- Update compliance alerts to be Wells Fargo specific
UPDATE compliance_alerts
SET description = CASE id
  WHEN 'alert-001' THEN 'Wells Fargo quarterly capital adequacy report submission to FDIC required.'
  WHEN 'alert-002' THEN 'Wells Fargo annual stress test submission deadline approaching under Dodd-Frank requirements.'
  WHEN 'alert-003' THEN 'Comprehensive review of Wells Fargo lending practices and policies needed.'
  WHEN 'alert-004' THEN 'Wells Fargo quarterly AML risk assessment and report submission required.'
  WHEN 'alert-005' THEN 'Wells Fargo staff training update needed for consumer protection requirements.'
  ELSE description
END;

-- Update regulatory updates to focus on Wells Fargo impact
UPDATE regulatory_updates
SET description = CASE id
  WHEN 'update-001' THEN 'FDIC guidance update on LCR calculations affecting Wells Fargo''s capital requirements.'
  WHEN 'update-002' THEN 'Federal Reserve releases 2024 stress test scenarios for Wells Fargo assessment.'
  WHEN 'update-003' THEN 'Updated fair lending examination procedures affecting Wells Fargo''s compliance program.'
  WHEN 'update-004' THEN 'New FinCEN guidance on digital asset monitoring affecting Wells Fargo''s AML program.'
  WHEN 'update-005' THEN 'Updated consumer protection guidelines impacting Wells Fargo''s retail operations.'
  ELSE description
END;

-- Update chat_messages to focus on Wells Fargo context
UPDATE chat_messages
SET content = CASE
  WHEN sender = 'user' AND content LIKE '%Basel III%' 
    THEN 'What are Wells Fargo''s obligations under Basel III?'
  WHEN sender = 'bot' AND content LIKE '%Basel III%'
    THEN 'As a Global Systemically Important Bank (G-SIB), Wells Fargo must maintain a minimum CET1 ratio of 4.5% under Basel III. The bank is required to implement a Liquidity Coverage Ratio (LCR) to ensure sufficient high-quality liquid assets, conduct quarterly stress tests, and report capital adequacy metrics to regulators regularly.'
  WHEN sender = 'user' AND content LIKE '%fair lending%'
    THEN 'What are our current fair lending requirements?'
  WHEN sender = 'bot' AND content LIKE '%fair lending%'
    THEN 'Wells Fargo must comply with comprehensive fair lending regulations that prohibit discrimination in lending practices. Key requirements include maintaining non-discriminatory lending policies, conducting regular audits of lending practices, providing staff training on fair lending requirements, and submitting regular reports to regulators. The bank must ensure equal access to credit regardless of protected characteristics and maintain robust documentation of lending decisions.'
  ELSE content
END;

-- Update documents to be Wells Fargo specific
UPDATE documents
SET description = CASE
  WHEN title LIKE '%Basel%' 
    THEN REPLACE(description, 'banks', 'Wells Fargo')
  WHEN title LIKE '%Dodd-Frank%'
    THEN REPLACE(description, 'financial institutions', 'Wells Fargo')
  WHEN title LIKE '%Fair Lending%'
    THEN REPLACE(description, 'lenders', 'Wells Fargo')
  WHEN title LIKE '%AML%'
    THEN REPLACE(description, 'institutions', 'Wells Fargo')
  WHEN title LIKE '%Consumer%'
    THEN REPLACE(description, 'banks', 'Wells Fargo')
  ELSE description
END;

-- Ensure RLS policies are updated for Wells Fargo focus
DO $$ 
BEGIN
  -- Update bank-specific policies
  IF EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE tablename = 'banks' AND policyname = 'Banks access policy'
  ) THEN
    DROP POLICY "Banks access policy" ON banks;
  END IF;

  CREATE POLICY "Banks access policy"
    ON banks
    FOR ALL
    TO authenticated
    USING (name = 'Wells Fargo')
    WITH CHECK (name = 'Wells Fargo');
END $$;