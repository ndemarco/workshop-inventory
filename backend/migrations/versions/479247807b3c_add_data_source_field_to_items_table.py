"""Add data_source field to items table

Revision ID: 479247807b3c
Revises: 6bcf6f19115a
Create Date: 2025-11-03 13:15:28.451170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '479247807b3c'
down_revision = '6bcf6f19115a'
branch_labels = None
depends_on = None


def upgrade():
    # Add data_source column with default value
    op.add_column('items', sa.Column('data_source', sa.String(length=50), nullable=False, server_default='user'))


def downgrade():
    # Remove data_source column
    op.drop_column('items', 'data_source')
