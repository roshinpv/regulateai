"""Add employee training table

Revision ID: add_employee_training
Revises: update_risk_compliance_mapping
Create Date: 2025-03-09 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_employee_training'
down_revision: str = 'update_risk_compliance_mapping'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create TrainingStatus enum
    op.execute("""
        CREATE TYPE trainingstatus AS ENUM ('Pending', 'In Progress', 'Completed')
    """)
    
    # Create employee_trainings table
    op.create_table(
        'employee_trainings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_name', sa.String(), nullable=False),
        sa.Column('employee_email', sa.String(), nullable=False),
        sa.Column('manager_name', sa.String(), nullable=False),
        sa.Column('manager_email', sa.String(), nullable=False),
        sa.Column('training_name', sa.String(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('Pending', 'In Progress', 'Completed', name='trainingstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(
        'ix_employee_trainings_employee_email',
        'employee_trainings',
        ['employee_email']
    )
    op.create_index(
        'ix_employee_trainings_manager_email',
        'employee_trainings',
        ['manager_email']
    )
    op.create_index(
        'ix_employee_trainings_due_date',
        'employee_trainings',
        ['due_date']
    )
    op.create_index(
        'ix_employee_trainings_status',
        'employee_trainings',
        ['status']
    )

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_employee_trainings_status')
    op.drop_index('ix_employee_trainings_due_date')
    op.drop_index('ix_employee_trainings_manager_email')
    op.drop_index('ix_employee_trainings_employee_email')
    
    # Drop table
    op.drop_table('employee_trainings')
    
    # Drop enum
    op.execute('DROP TYPE trainingstatus')