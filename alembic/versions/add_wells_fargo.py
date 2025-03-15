"""Add Wells Fargo bank

Revision ID: add_wells_fargo
Revises: initial_migration
Create Date: 2025-03-09 15:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_wells_fargo'
down_revision: str = 'initial_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create Wells Fargo bank with fixed ID
    op.execute("""
        INSERT INTO banks (id, name, size_category)
        VALUES ('bank-001', 'Wells Fargo', 'Global Systemically Important')
    """)

def downgrade() -> None:
    # Remove Wells Fargo bank
    op.execute("""
        DELETE FROM banks WHERE id = 'bank-001'
    """)