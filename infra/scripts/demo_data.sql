-- Demo data for ValidaHub
-- This file contains sample data for testing and demonstration

-- Create demo users (password for all: 'secret')
INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', 'demo@validahub.com', 'demo_user', 'Demo User', 
     '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, false, NOW()),
    ('550e8400-e29b-41d4-a716-446655440002', 'admin@validahub.com', 'admin', 'Admin User', 
     '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true, true, NOW())
ON CONFLICT (email) DO NOTHING;

-- Create sample jobs
INSERT INTO jobs (id, user_id, status, file_key, result, created_at)
VALUES
    ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 
     'completed', 'samples/mercadolivre_demo.csv', 
     '{"total_rows": 100, "errors_found": 15, "corrections_applied": 15}', NOW()),
    ('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 
     'completed', 'samples/shopee_demo.csv',
     '{"total_rows": 50, "errors_found": 8, "corrections_applied": 8}', NOW())
ON CONFLICT (id) DO NOTHING;

-- Sample marketplace configurations (future table)
-- CREATE TABLE IF NOT EXISTS marketplace_configs (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     marketplace VARCHAR(50) NOT NULL,
--     title_max_length INTEGER,
--     price_min DECIMAL(10,2),
--     requires_sku BOOLEAN,
--     created_at TIMESTAMP DEFAULT NOW()
-- );

-- INSERT INTO marketplace_configs (marketplace, title_max_length, price_min, requires_sku)
-- VALUES 
--     ('MERCADO_LIVRE', 60, 0.01, true),
--     ('SHOPEE', 100, 0.01, true),
--     ('AMAZON', 200, 0.01, true)
-- ON CONFLICT DO NOTHING;