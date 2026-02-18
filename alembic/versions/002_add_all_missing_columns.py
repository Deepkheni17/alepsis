"""add all missing columns to invoices and create users table

Revision ID: 002_add_all_missing
Revises: 001_add_user_auth
Create Date: 2026-02-18 22:10:00.000000

This migration is a SAFE, idempotent migration that adds ALL columns
that exist in the ORM model but are missing from the actual Supabase DB.

Missing columns detected from error:
  - invoices.user_id  (UndefinedColumn error)
  - invoices.line_items
  - invoices.subtotal
  - invoices.discount_percentage
  - invoices.discount_amount
  - invoices.cgst_rate
  - invoices.cgst_amount
  - invoices.sgst_rate
  - invoices.sgst_amount
  - invoices.status
  - users table (for FK)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = '002_add_all_missing'
down_revision = None   # Set to None so it runs independently (not chained to 001)
branch_labels = None
depends_on = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column already exists in the table (safe idempotent check)."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    """Check if a table already exists."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade():
    """
    Add ALL missing columns to bring the Supabase DB in sync with ORM models.
    Each operation is guarded with an existence check so it is safe to re-run.
    """

    # ------------------------------------------------------------------ #
    # 1. Create 'users' table if it doesn't exist
    # ------------------------------------------------------------------ #
    if not table_exists('users'):
        op.create_table(
            'users',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('now()'),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        print("✅ Created 'users' table")
    else:
        print("⏭  'users' table already exists — skipping")

    # ------------------------------------------------------------------ #
    # 2. Add 'user_id' column to invoices (THE column causing the crash)
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'user_id'):
        op.add_column(
            'invoices',
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_index(op.f('ix_invoices_user_id'), 'invoices', ['user_id'], unique=False)

        # Add FK constraint only after column exists
        op.create_foreign_key(
            'fk_invoices_user_id',
            'invoices', 'users',
            ['user_id'], ['id'],
            ondelete='CASCADE',
        )
        print("✅ Added 'user_id' column + FK to invoices")
    else:
        print("⏭  'user_id' already exists in invoices — skipping")

    # ------------------------------------------------------------------ #
    # 3. Add 'line_items' column (JSON text for line item storage)
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'line_items'):
        op.add_column('invoices', sa.Column('line_items', sa.Text(), nullable=True))
        print("✅ Added 'line_items' column")
    else:
        print("⏭  'line_items' already exists — skipping")

    # ------------------------------------------------------------------ #
    # 4. Add 'subtotal' column
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'subtotal'):
        op.add_column('invoices', sa.Column('subtotal', sa.Float(), nullable=True))
        print("✅ Added 'subtotal' column")
    else:
        print("⏭  'subtotal' already exists — skipping")

    # ------------------------------------------------------------------ #
    # 5. Add discount columns
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'discount_percentage'):
        op.add_column('invoices', sa.Column('discount_percentage', sa.Float(), nullable=True))
        print("✅ Added 'discount_percentage' column")
    else:
        print("⏭  'discount_percentage' already exists — skipping")

    if not column_exists('invoices', 'discount_amount'):
        op.add_column('invoices', sa.Column('discount_amount', sa.Float(), nullable=True))
        print("✅ Added 'discount_amount' column")
    else:
        print("⏭  'discount_amount' already exists — skipping")

    # ------------------------------------------------------------------ #
    # 6. Add CGST tax columns (Indian GST)
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'cgst_rate'):
        op.add_column('invoices', sa.Column('cgst_rate', sa.Float(), nullable=True))
        print("✅ Added 'cgst_rate' column")
    else:
        print("⏭  'cgst_rate' already exists — skipping")

    if not column_exists('invoices', 'cgst_amount'):
        op.add_column('invoices', sa.Column('cgst_amount', sa.Float(), nullable=True))
        print("✅ Added 'cgst_amount' column")
    else:
        print("⏭  'cgst_amount' already exists — skipping")

    # ------------------------------------------------------------------ #
    # 7. Add SGST tax columns (Indian GST)
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'sgst_rate'):
        op.add_column('invoices', sa.Column('sgst_rate', sa.Float(), nullable=True))
        print("✅ Added 'sgst_rate' column")
    else:
        print("⏭  'sgst_rate' already exists — skipping")

    if not column_exists('invoices', 'sgst_amount'):
        op.add_column('invoices', sa.Column('sgst_amount', sa.Float(), nullable=True))
        print("✅ Added 'sgst_amount' column")
    else:
        print("⏭  'sgst_amount' already exists — skipping")

    # ------------------------------------------------------------------ #
    # 8. Add 'status' column (approval workflow: PENDING / REVIEW_REQUIRED / APPROVED)
    # ------------------------------------------------------------------ #
    if not column_exists('invoices', 'status'):
        op.add_column(
            'invoices',
            sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        )
        print("✅ Added 'status' column")
    else:
        print("⏭  'status' already exists — skipping")

    print("\n🎉 Migration 002 complete — all missing columns added!")


def downgrade():
    """
    Rollback: remove all columns added by this migration.
    """
    # Drop FK and user_id
    try:
        op.drop_constraint('fk_invoices_user_id', 'invoices', type_='foreignkey')
    except Exception:
        pass

    for col in ['status', 'sgst_amount', 'sgst_rate', 'cgst_amount', 'cgst_rate',
                'discount_amount', 'discount_percentage', 'subtotal', 'line_items', 'user_id']:
        if column_exists('invoices', col):
            if col == 'user_id':
                try:
                    op.drop_index(op.f('ix_invoices_user_id'), table_name='invoices')
                except Exception:
                    pass
            op.drop_column('invoices', col)

    if table_exists('users'):
        try:
            op.drop_index(op.f('ix_users_email'), table_name='users')
        except Exception:
            pass
        op.drop_table('users')
