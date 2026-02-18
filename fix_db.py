"""
fix_db.py — Direct database fix script
Adds ALL missing columns to the invoices table in Supabase.
Run with: python fix_db.py
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set in .env")
    sys.exit(1)

print(f"🔗 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    print("✅ Connected!\n")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)


def column_exists(table, column):
    cur.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
          AND column_name = %s
    """, (table, column))
    return cur.fetchone() is not None


def table_exists(table):
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = %s
    """, (table,))
    return cur.fetchone() is not None


def constraint_exists(constraint_name):
    cur.execute("""
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = %s
    """, (constraint_name,))
    return cur.fetchone() is not None


print("=" * 60)
print("STEP 1: Create 'users' table")
print("=" * 60)
if not table_exists('users'):
    cur.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    print("✅ Created 'users' table")
else:
    print("⏭  'users' table already exists")


print("\n" + "=" * 60)
print("STEP 2: Add 'user_id' column to invoices (THE crash column)")
print("=" * 60)
if not column_exists('invoices', 'user_id'):
    cur.execute("ALTER TABLE invoices ADD COLUMN user_id UUID")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_invoices_user_id ON invoices (user_id)")
    if not constraint_exists('fk_invoices_user_id'):
        cur.execute("""
            ALTER TABLE invoices
            ADD CONSTRAINT fk_invoices_user_id
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        """)
    print("✅ Added 'user_id' column + index + FK constraint")
else:
    print("⏭  'user_id' already exists")


print("\n" + "=" * 60)
print("STEP 3: Add 'line_items' column")
print("=" * 60)
if not column_exists('invoices', 'line_items'):
    cur.execute("ALTER TABLE invoices ADD COLUMN line_items TEXT")
    print("✅ Added 'line_items'")
else:
    print("⏭  'line_items' already exists")


print("\n" + "=" * 60)
print("STEP 4: Add 'subtotal' column")
print("=" * 60)
if not column_exists('invoices', 'subtotal'):
    cur.execute("ALTER TABLE invoices ADD COLUMN subtotal FLOAT")
    print("✅ Added 'subtotal'")
else:
    print("⏭  'subtotal' already exists")


print("\n" + "=" * 60)
print("STEP 5: Add discount columns")
print("=" * 60)
if not column_exists('invoices', 'discount_percentage'):
    cur.execute("ALTER TABLE invoices ADD COLUMN discount_percentage FLOAT")
    print("✅ Added 'discount_percentage'")
else:
    print("⏭  'discount_percentage' already exists")

if not column_exists('invoices', 'discount_amount'):
    cur.execute("ALTER TABLE invoices ADD COLUMN discount_amount FLOAT")
    print("✅ Added 'discount_amount'")
else:
    print("⏭  'discount_amount' already exists")


print("\n" + "=" * 60)
print("STEP 6: Add CGST tax columns")
print("=" * 60)
if not column_exists('invoices', 'cgst_rate'):
    cur.execute("ALTER TABLE invoices ADD COLUMN cgst_rate FLOAT")
    print("✅ Added 'cgst_rate'")
else:
    print("⏭  'cgst_rate' already exists")

if not column_exists('invoices', 'cgst_amount'):
    cur.execute("ALTER TABLE invoices ADD COLUMN cgst_amount FLOAT")
    print("✅ Added 'cgst_amount'")
else:
    print("⏭  'cgst_amount' already exists")


print("\n" + "=" * 60)
print("STEP 7: Add SGST tax columns")
print("=" * 60)
if not column_exists('invoices', 'sgst_rate'):
    cur.execute("ALTER TABLE invoices ADD COLUMN sgst_rate FLOAT")
    print("✅ Added 'sgst_rate'")
else:
    print("⏭  'sgst_rate' already exists")

if not column_exists('invoices', 'sgst_amount'):
    cur.execute("ALTER TABLE invoices ADD COLUMN sgst_amount FLOAT")
    print("✅ Added 'sgst_amount'")
else:
    print("⏭  'sgst_amount' already exists")


print("\n" + "=" * 60)
print("STEP 8: Add 'status' column")
print("=" * 60)
if not column_exists('invoices', 'status'):
    cur.execute("ALTER TABLE invoices ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'PENDING'")
    print("✅ Added 'status'")
else:
    print("⏭  'status' already exists")


print("\n" + "=" * 60)
print("VERIFICATION — Current columns in 'invoices' table:")
print("=" * 60)
cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'invoices'
    ORDER BY ordinal_position
""")
rows = cur.fetchall()
for row in rows:
    print(f"  ✓ {row[0]:30s} {row[1]:20s} nullable={row[2]}")

cur.close()
conn.close()

print("\n🎉 ALL DONE! Database is now in sync with ORM models.")
print("   Restart your FastAPI server and the 'Failed to fetch invoices' error should be gone.")
