-- Create validation_records table for storing order validation results
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

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_order_id ON validation_records(order_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON validation_records(timestamp DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE validation_records ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for authenticated users
-- Using anon key means we need to allow public access for the API
CREATE POLICY "Allow public access to validation_records"
    ON validation_records
    FOR ALL
    USING (true)
    WITH CHECK (true);
