"""Update risk compliance mapping with additional units

Revision ID: update_risk_compliance_mapping
Revises: update_risk_compliance
Create Date: 2025-03-09 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'update_risk_compliance_mapping'
down_revision: str = 'update_risk_compliance'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add additional risk assessment units with fixed IDs
    op.execute("""
        INSERT INTO risk_assessment_units (id, name, description, category, created_at, updated_at)
        VALUES 
            ('unit-003', 'Enterprise Risk Management', 'Manages enterprise-wide risk assessment and mitigation', 'Governance', NOW(), NOW()),
            ('unit-004', 'Cyber Security Governance', 'Oversees cybersecurity policies and controls', 'Security', NOW(), NOW()),
            ('unit-005', 'Regulatory Change Management', 'Manages regulatory compliance changes', 'Governance', NOW(), NOW()),
            ('unit-006', 'Information Security', 'Ensures data and system security', 'Security', NOW(), NOW()),
            ('unit-007', 'Compliance Monitoring', 'Monitors ongoing compliance with regulations', 'Governance', NOW(), NOW()),
            ('unit-008', 'Risk Assessment', 'Conducts risk assessments and analysis', 'Governance', NOW(), NOW())
        ON CONFLICT (name) DO NOTHING
    """)
    
    # Map regulations to risk assessment units
    op.execute("""
        INSERT INTO regulation_unit (regulation_id, unit_id)
        SELECT r.id, u.id
        FROM regulations r
        CROSS JOIN risk_assessment_units u
        WHERE r.id = 'REG-001' 
        AND u.name IN (
            'Enterprise Risk Management',
            'Cyber Security Governance',
            'Regulatory Change Management',
            'Information Security'
        )
        ON CONFLICT DO NOTHING
    """)
    
    # Add categories for regulations
    op.execute("""
        INSERT INTO regulation_categories (id, regulation_id, category)
        VALUES 
            (gen_random_uuid(), 'REG-001', 'Risk Management'),
            (gen_random_uuid(), 'REG-001', 'Capital & Liquidity'),
            (gen_random_uuid(), 'REG-001', 'Cybersecurity')
        ON CONFLICT DO NOTHING
    """)

def downgrade() -> None:
    # Remove regulation-unit mappings for new units
    op.execute("""
        DELETE FROM regulation_unit 
        WHERE regulation_id = 'REG-001'
        AND unit_id IN (
            SELECT id FROM risk_assessment_units 
            WHERE name IN (
                'Enterprise Risk Management',
                'Cyber Security Governance',
                'Regulatory Change Management',
                'Information Security'
            )
        )
    """)
    
    # Remove new risk assessment units
    op.execute("""
        DELETE FROM risk_assessment_units 
        WHERE id IN ('unit-003', 'unit-004', 'unit-005', 'unit-006', 'unit-007', 'unit-008')
    """)
    
    # Remove added categories
    op.execute("""
        DELETE FROM regulation_categories
        WHERE regulation_id = 'REG-001'
        AND category IN ('Risk Management', 'Capital & Liquidity', 'Cybersecurity')
    """)