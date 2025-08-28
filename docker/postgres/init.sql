-- PostgreSQL Initialization Script for PyLadies Seoul Production Database

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create read-only user for monitoring and backups
DO $body$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user WHERE usename = 'pyladies_readonly'
   ) THEN
      CREATE USER pyladies_readonly WITH PASSWORD 'readonly_password_change_in_production';
   END IF;
END
$body$;

-- Grant read-only permissions
GRANT CONNECT ON DATABASE pyladies_seoul TO pyladies_readonly;
GRANT USAGE ON SCHEMA public TO pyladies_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pyladies_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO pyladies_readonly;

-- Create backup user
DO $body$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_user WHERE usename = 'pyladies_backup'
   ) THEN
      CREATE USER pyladies_backup WITH PASSWORD 'backup_password_change_in_production';
   END IF;
END
$body$;

-- Grant backup permissions
GRANT CONNECT ON DATABASE pyladies_seoul TO pyladies_backup;
GRANT USAGE ON SCHEMA public TO pyladies_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pyladies_backup;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO pyladies_backup;

-- Performance optimizations
-- Increase statistics target for better query planning
ALTER DATABASE pyladies_seoul SET default_statistics_target = 100;

-- Set work_mem for complex queries
ALTER DATABASE pyladies_seoul SET work_mem = '8MB';

-- Configure connection limits
ALTER USER postgres CONNECTION LIMIT 50;
ALTER USER pyladies_readonly CONNECTION LIMIT 10;
ALTER USER pyladies_backup CONNECTION LIMIT 5;

-- Create indexes for common Django patterns (will be created by migrations, but keeping as reference)
-- These will be created by Django migrations, but documented here for reference:
-- 
-- Common Django indexes:
-- - auth_user(username)  
-- - auth_user(email)
-- - django_session(session_key)
-- - django_session(expire_date)
-- - wagtailcore_page(path)
-- - wagtailcore_page(url_path)
-- - wagtailcore_pagerevision(page_id)
--
-- Custom application indexes will be created by Django migrations

-- Log the initialization
\echo 'PostgreSQL database initialized successfully for PyLadies Seoul'
\echo 'Extensions created: uuid-ossp, pg_trgm, unaccent'  
\echo 'Users created: pyladies_readonly, pyladies_backup'
\echo 'Performance settings applied'