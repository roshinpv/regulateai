/*
  # Add Entity Analysis System

  1. New Tables
    - `entities`
      - Core entity information and risk scores
    - `entity_sources`
      - Data sources and evidence
    - `entity_transactions`
      - Transaction history and patterns
    - `entity_relationships`
      - Connections between entities
    - `entity_risk_factors`
      - Risk scoring components

  2. Security
    - Enable RLS
    - Add policies for authenticated users

  3. Features
    - Real-time risk scoring
    - Evidence tracking
    - Relationship mapping
*/

-- Create entity types enum
CREATE TYPE entity_type AS ENUM (
  'Corporation',
  'Non-Profit',
  'Shell Company',
  'Financial Intermediary',
  'Individual',
  'Other'
);

-- Create source type enum
CREATE TYPE source_type AS ENUM (
  'Transaction Data',
  'Public Records',
  'News Articles',
  'Regulatory Filings',
  'Court Records',
  'Sanctions Lists',
  'Corporate Registries',
  'Financial Statements',
  'Other'
);

-- Create verification status enum
CREATE TYPE verification_status AS ENUM (
  'Pending',
  'Verified',
  'Disputed',
  'Inconclusive'
);

-- Create entities table
CREATE TABLE IF NOT EXISTS entities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  type entity_type NOT NULL,
  registration_number text,
  jurisdiction text,
  incorporation_date date,
  risk_score integer CHECK (risk_score >= 0 AND risk_score <= 100),
  confidence_score integer CHECK (confidence_score >= 0 AND confidence_score <= 100),
  last_analyzed_at timestamptz,
  analysis_status verification_status DEFAULT 'Pending',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create entity sources table
CREATE TABLE IF NOT EXISTS entity_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
  source_type source_type NOT NULL,
  source_url text,
  source_date timestamptz,
  content text,
  reliability_score integer CHECK (reliability_score >= 0 AND reliability_score <= 100),
  verification_status verification_status DEFAULT 'Pending',
  verified_at timestamptz,
  verified_by uuid REFERENCES auth.users(id),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Create entity transactions table
CREATE TABLE IF NOT EXISTS entity_transactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
  transaction_date timestamptz NOT NULL,
  transaction_type text NOT NULL,
  amount decimal(20,2),
  currency text,
  counterparty_id uuid REFERENCES entities(id),
  risk_indicators jsonb DEFAULT '{}'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Create entity relationships table
CREATE TABLE IF NOT EXISTS entity_relationships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  from_entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
  to_entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
  relationship_type text NOT NULL,
  strength_score integer CHECK (strength_score >= 0 AND strength_score <= 100),
  evidence jsonb DEFAULT '{}'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  UNIQUE(from_entity_id, to_entity_id, relationship_type)
);

-- Create entity risk factors table
CREATE TABLE IF NOT EXISTS entity_risk_factors (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id uuid REFERENCES entities(id) ON DELETE CASCADE,
  factor_type text NOT NULL,
  factor_value text,
  risk_contribution integer CHECK (risk_contribution >= 0 AND risk_contribution <= 100),
  confidence_score integer CHECK (confidence_score >= 0 AND confidence_score <= 100),
  evidence jsonb DEFAULT '{}'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE entity_risk_factors ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read entities"
  ON entities
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage entities"
  ON entities
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read entity sources"
  ON entity_sources
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage entity sources"
  ON entity_sources
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read entity transactions"
  ON entity_transactions
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage entity transactions"
  ON entity_transactions
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read entity relationships"
  ON entity_relationships
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage entity relationships"
  ON entity_relationships
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read entity risk factors"
  ON entity_risk_factors
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage entity risk factors"
  ON entity_risk_factors
  USING (auth.jwt() ->> 'role' = 'admin');

-- Create indexes
CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_entities_type ON entities(type);
CREATE INDEX idx_entities_risk_score ON entities(risk_score);
CREATE INDEX idx_entity_sources_entity_id ON entity_sources(entity_id);
CREATE INDEX idx_entity_sources_type ON entity_sources(source_type);
CREATE INDEX idx_entity_transactions_entity_id ON entity_transactions(entity_id);
CREATE INDEX idx_entity_transactions_date ON entity_transactions(transaction_date);
CREATE INDEX idx_entity_relationships_from ON entity_relationships(from_entity_id);
CREATE INDEX idx_entity_relationships_to ON entity_relationships(to_entity_id);
CREATE INDEX idx_entity_risk_factors_entity_id ON entity_risk_factors(entity_id);

-- Create function to update entity risk score
CREATE OR REPLACE FUNCTION update_entity_risk_score(entity_id uuid)
RETURNS integer AS $$
DECLARE
  new_risk_score integer;
BEGIN
  -- Calculate weighted average of risk factors
  SELECT COALESCE(
    ROUND(
      AVG(
        risk_contribution * confidence_score / 100.0
      )
    ),
    0
  )
  INTO new_risk_score
  FROM entity_risk_factors
  WHERE entity_id = $1;

  -- Update entity risk score
  UPDATE entities
  SET 
    risk_score = new_risk_score,
    last_analyzed_at = now()
  WHERE id = $1;

  RETURN new_risk_score;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update risk score when risk factors change
CREATE OR REPLACE FUNCTION trigger_update_risk_score()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM update_entity_risk_score(
    CASE
      WHEN TG_OP = 'DELETE' THEN OLD.entity_id
      ELSE NEW.entity_id
    END
  );
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_risk_score_on_factor_change
  AFTER INSERT OR UPDATE OR DELETE ON entity_risk_factors
  FOR EACH ROW
  EXECUTE FUNCTION trigger_update_risk_score();

-- Create function to calculate relationship strength
CREATE OR REPLACE FUNCTION calculate_relationship_strength(
  transaction_count integer,
  transaction_volume numeric,
  source_overlap integer,
  risk_correlation numeric
) RETURNS integer AS $$
BEGIN
  RETURN ROUND(
    LEAST(
      100,
      GREATEST(
        0,
        -- Weight different factors
        transaction_count * 0.3 +
        LEAST(transaction_volume / 1000000 * 0.3, 30) +
        source_overlap * 0.2 +
        risk_correlation * 0.2
      )
    )
  );
END;
$$ LANGUAGE plpgsql;