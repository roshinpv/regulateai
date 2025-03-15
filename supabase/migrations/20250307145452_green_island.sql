/*
  # Add Risk Assessment Units and Related Tables

  1. New Tables
    - `risk_assessment_units`
      - `id` (uuid, primary key)
      - `name` (text, unique)
      - `description` (text)
      - `category` (enum)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)
    
    - `regulation_unit` (junction table)
      - `regulation_id` (uuid, foreign key)
      - `unit_id` (uuid, foreign key)

  2. Changes
    - Add risk compliance mapping functionality
    - Add related regulations support

  3. Security
    - Enable RLS on new tables
    - Add policies for authenticated users
*/

-- Create risk assessment unit category enum
CREATE TYPE unit_category AS ENUM (
  'Application',
  'Infrastructure',
  'Security',
  'Governance',
  'Operations'
);

-- Create risk assessment units table
CREATE TABLE IF NOT EXISTS risk_assessment_units (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text UNIQUE NOT NULL,
  description text,
  category unit_category NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create junction table for regulations and units
CREATE TABLE IF NOT EXISTS regulation_unit (
  regulation_id uuid REFERENCES regulations(id) ON DELETE CASCADE,
  unit_id uuid REFERENCES risk_assessment_units(id) ON DELETE CASCADE,
  PRIMARY KEY (regulation_id, unit_id)
);

-- Create table for risk compliance mapping
CREATE TABLE IF NOT EXISTS risk_compliance_mapping (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  regulation_id uuid REFERENCES regulations(id) ON DELETE CASCADE,
  compliance_area text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create table for related regulations
CREATE TABLE IF NOT EXISTS related_regulations (
  regulation_id uuid REFERENCES regulations(id) ON DELETE CASCADE,
  related_regulation_id uuid REFERENCES regulations(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  PRIMARY KEY (regulation_id, related_regulation_id)
);

-- Enable RLS
ALTER TABLE risk_assessment_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulation_unit ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_compliance_mapping ENABLE ROW LEVEL SECURITY;
ALTER TABLE related_regulations ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read risk assessment units"
  ON risk_assessment_units
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage risk assessment units"
  ON risk_assessment_units
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read regulation unit mappings"
  ON regulation_unit
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage regulation unit mappings"
  ON regulation_unit
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read risk compliance mappings"
  ON risk_compliance_mapping
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage risk compliance mappings"
  ON risk_compliance_mapping
  USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can read related regulations"
  ON related_regulations
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage related regulations"
  ON related_regulations
  USING (auth.jwt() ->> 'role' = 'admin');

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_risk_assessment_units_category ON risk_assessment_units(category);
CREATE INDEX IF NOT EXISTS idx_risk_compliance_mapping_area ON risk_compliance_mapping(compliance_area);
CREATE INDEX IF NOT EXISTS idx_regulation_unit_regulation ON regulation_unit(regulation_id);
CREATE INDEX IF NOT EXISTS idx_regulation_unit_unit ON regulation_unit(unit_id);