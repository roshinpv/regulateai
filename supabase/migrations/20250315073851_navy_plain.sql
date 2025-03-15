/*
  # Add Regulatory Change Alert System

  1. New Tables
    - `regulatory_alerts`
      - `id` (uuid, primary key)
      - `title` (text)
      - `content` (text)
      - `agency_id` (text)
      - `update_type` (enum)
      - `priority` (enum)
      - `status` (enum)
      - `published_date` (timestamptz)
      - `url` (text)
      - `metadata` (jsonb)
      - `created_at` (timestamptz)
      - `updated_at` (timestamptz)
      - `processed_at` (timestamptz)
      - `notified_at` (timestamptz)

  2. Security
    - Enable RLS
    - Add policies for authenticated users

  3. Changes
    - Add alert generation functionality
    - Add notification tracking
*/

-- Create update type enum
CREATE TYPE regulatory_update_type AS ENUM (
  'Rule Change',
  'Guidance',
  'Advisory',
  'Enforcement Action',
  'Press Release',
  'Bulletin',
  'Notice',
  'Other'
);

-- Create alert priority enum
CREATE TYPE alert_priority AS ENUM (
  'High',
  'Medium',
  'Low'
);

-- Create alert status enum
CREATE TYPE alert_status AS ENUM (
  'New',
  'Processing',
  'Analyzed',
  'Notified',
  'Archived'
);

-- Create regulatory alerts table
CREATE TABLE IF NOT EXISTS regulatory_alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL,
  content text NOT NULL,
  agency_id text NOT NULL,
  update_type regulatory_update_type NOT NULL,
  priority alert_priority NOT NULL DEFAULT 'Medium',
  status alert_status NOT NULL DEFAULT 'New',
  published_date timestamptz NOT NULL,
  url text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  processed_at timestamptz,
  notified_at timestamptz
);

-- Enable RLS
ALTER TABLE regulatory_alerts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read regulatory alerts"
  ON regulatory_alerts
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage regulatory alerts"
  ON regulatory_alerts
  USING (auth.jwt() ->> 'role' = 'admin');

-- Create indexes
CREATE INDEX idx_regulatory_alerts_agency ON regulatory_alerts(agency_id);
CREATE INDEX idx_regulatory_alerts_type ON regulatory_alerts(update_type);
CREATE INDEX idx_regulatory_alerts_priority ON regulatory_alerts(priority);
CREATE INDEX idx_regulatory_alerts_status ON regulatory_alerts(status);
CREATE INDEX idx_regulatory_alerts_published_date ON regulatory_alerts(published_date);
CREATE INDEX idx_regulatory_alerts_created_at ON regulatory_alerts(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_regulatory_alerts_updated_at
  BEFORE UPDATE ON regulatory_alerts
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create function to analyze alert priority
CREATE OR REPLACE FUNCTION analyze_alert_priority(
  update_type regulatory_update_type,
  content text,
  metadata jsonb
) RETURNS alert_priority AS $$
DECLARE
  priority alert_priority;
  content_lower text;
BEGIN
  -- Convert content to lowercase for case-insensitive matching
  content_lower := lower(content);
  
  -- Set initial priority based on update type
  CASE update_type
    WHEN 'Rule Change' THEN priority := 'High'
    WHEN 'Enforcement Action' THEN priority := 'High'
    WHEN 'Guidance' THEN priority := 'Medium'
    WHEN 'Advisory' THEN priority := 'Medium'
    ELSE priority := 'Low'
  END;
  
  -- Check content for high-priority keywords
  IF content_lower LIKE ANY (ARRAY[
    '%compliance requirement%',
    '%mandatory%',
    '%deadline%',
    '%violation%',
    '%penalty%',
    '%fine%',
    '%immediate effect%',
    '%critical%',
    '%urgent%'
  ]) THEN
    priority := 'High';
  END IF;
  
  -- Check metadata for priority indicators
  IF metadata ? 'priority' THEN
    CASE lower(metadata->>'priority')
      WHEN 'high' THEN priority := 'High'
      WHEN 'medium' THEN priority := 'Medium'
      WHEN 'low' THEN priority := 'Low'
    END;
  END IF;
  
  RETURN priority;
END;
$$ LANGUAGE plpgsql;

-- Create function to generate alert from regulatory update
CREATE OR REPLACE FUNCTION generate_regulatory_alert(
  p_title text,
  p_content text,
  p_agency_id text,
  p_update_type regulatory_update_type,
  p_published_date timestamptz,
  p_url text DEFAULT NULL,
  p_metadata jsonb DEFAULT '{}'::jsonb
) RETURNS uuid AS $$
DECLARE
  alert_id uuid;
  alert_priority alert_priority;
BEGIN
  -- Analyze priority
  alert_priority := analyze_alert_priority(p_update_type, p_content, p_metadata);
  
  -- Insert alert
  INSERT INTO regulatory_alerts (
    title,
    content,
    agency_id,
    update_type,
    priority,
    published_date,
    url,
    metadata
  ) VALUES (
    p_title,
    p_content,
    p_agency_id,
    p_update_type,
    alert_priority,
    p_published_date,
    p_url,
    p_metadata
  ) RETURNING id INTO alert_id;
  
  RETURN alert_id;
END;
$$ LANGUAGE plpgsql;