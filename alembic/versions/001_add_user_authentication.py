"""add user authentication

Revision ID: 001_add_user_auth
Revises: 
Create Date: 2026-02-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_user_auth'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Add user authentication support:
    1. Create users table
    2. Add user_id to invoices table
    3. Create foreign key relationship
    """
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Add user_id to invoices table (nullable initially for existing data)
    op.add_column('invoices', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_invoices_user_id'), 'invoices', ['user_id'], unique=False)
    
    # Create foreign key constraint
    op.create_foreign_key('fk_invoices_user_id', 'invoices', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    
    # For production: If you have existing invoices, you'll need to:
    # 1. Create a migration user or assign existing invoices to real users
    # 2. Then make user_id NOT NULL with: 
    #    op.alter_column('invoices', 'user_id', nullable=False)


def downgrade():
    """
    Rollback user authentication changes
    """
    # Drop foreign key constraint
    op.drop_constraint('fk_invoices_user_id', 'invoices', type_='foreignkey')
    
    # Drop indices
    op.drop_index(op.f('ix_invoices_user_id'), table_name='invoices')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    
    # Drop columns and tables
    op.drop_column('invoices', 'user_id')
    op.drop_table('users')
