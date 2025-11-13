-- Create orders table for storing order definitions
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    order_id TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    items_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index for efficient order_id lookups
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);

-- Enable Row Level Security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public access
CREATE POLICY "Allow public access" ON orders FOR ALL USING (true) WITH CHECK (true);
