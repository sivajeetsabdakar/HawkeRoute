"""add location fields

Revision ID: add_location_fields
Revises: 
Create Date: 2024-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_location_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add location fields to User table
    op.add_column('user', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('address', sa.String(length=255), nullable=True))
    
    # Add location fields to Order table
    op.add_column('order', sa.Column('delivery_latitude', sa.Float(), nullable=True))
    op.add_column('order', sa.Column('delivery_longitude', sa.Float(), nullable=True))
    op.add_column('order', sa.Column('delivery_address', sa.String(length=255), nullable=True))
    op.add_column('order', sa.Column('delivery_sequence', sa.Integer(), nullable=True))

def downgrade():
    # Remove location fields from User table
    op.drop_column('user', 'latitude')
    op.drop_column('user', 'longitude')
    op.drop_column('user', 'address')
    
    # Remove location fields from Order table
    op.drop_column('order', 'delivery_latitude')
    op.drop_column('order', 'delivery_longitude')
    op.drop_column('order', 'delivery_address')
    op.drop_column('order', 'delivery_sequence') 