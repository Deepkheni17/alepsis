-- ============================================================
-- FIX SCRIPT: Add all missing columns to invoices table
-- 
-- HOW TO RUN:
--   1. Go to https://app.supabase.com
--   2. Open your project: xpypmlgmeruqvzrmhyiy
--   3. Click "SQL Editor" in the left sidebar
--   4. Paste this entire script and click "Run"
-- ============================================================


-- STEP 1: Create 'users' table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_users_email ON public.users (email);


-- STEP 2: Add 'user_id' column to invoices (THE column causing the crash)
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES public.users(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS ix_invoices_user_id ON public.invoices (user_id);


-- STEP 3: Add 'line_items' column (stores JSON array of line items)
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS line_items TEXT;


-- STEP 4: Add 'subtotal' column
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS subtotal FLOAT;


-- STEP 5: Add discount columns
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS discount_percentage FLOAT;

ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS discount_amount FLOAT;


-- STEP 6: Add CGST tax columns (Indian GST)
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS cgst_rate FLOAT;

ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS cgst_amount FLOAT;


-- STEP 7: Add SGST tax columns (Indian GST)
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS sgst_rate FLOAT;

ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS sgst_amount FLOAT;


-- STEP 8: Add 'status' column (approval workflow)
ALTER TABLE public.invoices
    ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'PENDING';


-- ============================================================
-- VERIFICATION: Check all columns exist after migration
-- ============================================================
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public' 
  AND table_name = 'invoices'
ORDER BY ordinal_position;
