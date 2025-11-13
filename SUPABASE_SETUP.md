# Supabase Setup Instructions

## Database Migration Complete

The codebase has been migrated from SQLite to Supabase. Follow these steps to complete the setup:

## 1. Create Table in Supabase

Run this SQL in your Supabase SQL Editor (Dashboard → SQL Editor):

```sql
CREATE TABLE IF NOT EXISTS validation_records (
    id BIGSERIAL PRIMARY KEY,
    order_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operator TEXT,
    is_complete BOOLEAN NOT NULL,
    expected_order_json JSONB NOT NULL,
    detected_order_json JSONB NOT NULL,
    comparison_result_json JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_order_id ON validation_records(order_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON validation_records(timestamp DESC);
```

## 2. Environment Variables (Required)

Create a `.env` file in the project root with:

```
SUPABASE_URL=https://ynouixvprefkbscxldan.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Note:** The application requires these environment variables to be set. The code will raise a `ValueError` if they are missing.

Alternative environment variable names are also supported:
- `NEXT_PUBLIC_SUPABASE_URL` (instead of `SUPABASE_URL`)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` (instead of `SUPABASE_KEY`)

## 3. Install Dependencies

```bash
uv sync
```

This will install the `supabase` package and remove `aiosqlite`.

## 4. Verify Setup

The application will automatically connect to Supabase when you run it. Validation results will be saved to Supabase instead of a local SQLite file.

## Changes Made

- ✅ Replaced `aiosqlite` with `supabase` dependency
- ✅ Updated `src/staff_meal/database.py` to use Supabase client
- ✅ Updated `src/staff_meal/storage.py` to use Supabase PostgREST API
- ✅ Maintained async function signatures for compatibility
- ✅ Environment variables required (no hardcoded credentials)

## Benefits

- Cloud-based storage (accessible from multiple devices)
- Better scalability
- No local database file management
- Real-time capabilities (can be extended later)
