"""Update risk compliance mapping

Revision ID: update_risk_compliance
Revises: add_wells_fargo
Create Date: 2025-03-09 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'update_risk_compliance'
down_revision: str = 'add_wells_fargo'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add risk assessment units with fixed IDs
    op.execute("""
        INSERT INTO risk_assessment_units (id, name, description, category, created_at, updated_at)
        VALUES 
            ('unit-001', 'Enterprise Risk Management', 'Manages enterprise-wide risk assessment and mitigation', 'Governance', NOW(), NOW()),
            ('unit-002', 'Cyber Security Governance', 'Oversees cybersecurity policies and controls', 'Security', NOW(), NOW())
        ON CONFLICT (name) DO NOTHING
    """)
    
    # Map regulations to risk assessment units
    op.execute("""
        INSERT INTO regulation_unit (regulation_id, unit_id)
        VALUES 
            ('REG-001', 'unit-001'),  -- Map Basel III to Enterprise Risk Management
            ('REG-001', 'unit-002')   -- Map Basel III to Cyber Security Governance
        ON CONFLICT DO NOTHING
    """)

def downgrade() -> None:
    # Remove regulation-unit mappings
    op.execute("""
        DELETE FROM regulation_unit 
        WHERE (regulation_id = 'REG-001' AND unit_id = 'unit-001')
           OR (regulation_id = 'REG-001' AND unit_id = 'unit-002')
    """)
    
    # Remove risk assessment units
    op.execute("""
        DELETE FROM risk_assessment_units 
        WHERE id IN ('unit-001', 'unit-002')
    """)