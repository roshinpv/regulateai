"""Initial database schema

Revision ID: initial_migration
Revises: 
Create Date: 2025-03-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Create jurisdictions table
    op.create_table(
        'jurisdictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('type', sa.Enum(
            'Global', 'Regional', 'National', 'State/Province', 'Local',
            name='jurisdictiontype'
        ), nullable=False),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['jurisdictions.id'])
    )
    
    # Create agencies table
    op.create_table(
        'agencies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('jurisdiction_id', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id']),
        sa.UniqueConstraint('name')
    )
    
    # Create banks table
    op.create_table(
        'banks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('jurisdiction_id', sa.String(), nullable=True),
        sa.Column('size_category', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id']),
        sa.UniqueConstraint('name')
    )
    
    # Create risk_assessment_units table
    op.create_table(
        'risk_assessment_units',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Enum(
            'Application', 'Infrastructure', 'Security', 'Governance', 'Operations',
            name='unitcategory'
        ), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create regulations table
    op.create_table(
        'regulations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('agency_id', sa.String(), nullable=False),
        sa.Column('jurisdiction_id', sa.String(), nullable=True),
        sa.Column('impact_level', sa.Enum(
            'High', 'Medium', 'Low',
            name='impactlevel'
        ), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('effective_date', sa.DateTime(), nullable=True),
        sa.Column('compliance_deadline', sa.DateTime(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('official_reference', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id']),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id'])
    )
    
    # Create regulation_categories table
    op.create_table(
        'regulation_categories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('category', sa.Enum(
            'Risk Management', 'Capital & Liquidity', 'Consumer Protection',
            'Financial Regulation', 'Fraud Prevention', 'Data Privacy',
            'Anti-Money Laundering', 'Financial Reporting', 'Corporate Governance',
            'Market Conduct', 'Cybersecurity', 'Operational Risk', 'Other',
            name='regulationcategory'
        ), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create compliance_steps table
    op.create_table(
        'compliance_steps',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create bank_regulation association table
    op.create_table(
        'bank_regulation',
        sa.Column('bank_id', sa.String(), nullable=False),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('bank_id', 'regulation_id'),
        sa.ForeignKeyConstraint(['bank_id'], ['banks.id']),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create regulation_unit association table
    op.create_table(
        'regulation_unit',
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('unit_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('regulation_id', 'unit_id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id']),
        sa.ForeignKeyConstraint(['unit_id'], ['risk_assessment_units.id'])
    )
    
    # Create related_regulations association table
    op.create_table(
        'related_regulations',
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('related_regulation_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('regulation_id', 'related_regulation_id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id']),
        sa.ForeignKeyConstraint(['related_regulation_id'], ['regulations.id'])
    )
    
    # Create compliance_alerts table
    op.create_table(
        'compliance_alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('priority', sa.Enum(
            'High', 'Medium', 'Low',
            name='impactlevel'
        ), nullable=False),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create regulatory_updates table
    op.create_table(
        'regulatory_updates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('agency', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    
    # Create citations table
    op.create_table(
        'citations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('regulation_id', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id']),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id'])
    )
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('regulation_id', sa.String(), nullable=True),
        sa.Column('jurisdiction_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['regulation_id'], ['regulations.id']),
        sa.ForeignKeyConstraint(['jurisdiction_id'], ['jurisdictions.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('documents')
    op.drop_table('citations')
    op.drop_table('chat_messages')
    op.drop_table('regulatory_updates')
    op.drop_table('compliance_alerts')
    op.drop_table('related_regulations')
    op.drop_table('regulation_unit')
    op.drop_table('bank_regulation')
    op.drop_table('compliance_steps')
    op.drop_table('regulation_categories')
    op.drop_table('regulations')
    op.drop_table('risk_assessment_units')
    op.drop_table('banks')
    op.drop_table('agencies')
    op.drop_table('jurisdictions')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE jurisdictiontype')
    op.execute('DROP TYPE unitcategory')
    op.execute('DROP TYPE impactlevel')
    op.execute('DROP TYPE regulationcategory')