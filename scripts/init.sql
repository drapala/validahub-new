-- Initial database setup for ValidaHub

-- Create schema
CREATE SCHEMA IF NOT EXISTS validahub;

-- Set default search path
SET search_path TO validahub, public;

-- Create enum types
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE user_role AS ENUM ('admin', 'user', 'viewer');
CREATE TYPE marketplace AS ENUM ('MERCADO_LIVRE', 'SHOPEE', 'AMAZON', 'MAGALU', 'AMERICANAS');

-- Grant permissions
GRANT ALL ON SCHEMA validahub TO validahub;
GRANT ALL ON ALL TABLES IN SCHEMA validahub TO validahub;
GRANT ALL ON ALL SEQUENCES IN SCHEMA validahub TO validahub;

-- Comments
COMMENT ON SCHEMA validahub IS 'ValidaHub main schema for CSV validation platform';
COMMENT ON TYPE job_status IS 'Status of async processing jobs';
COMMENT ON TYPE user_role IS 'User roles for access control';
COMMENT ON TYPE marketplace IS 'Supported marketplace platforms';