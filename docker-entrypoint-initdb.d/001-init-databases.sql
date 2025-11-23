-- ============================================
-- MySQL/MariaDB Initialization Script
-- ============================================
-- This script ensures the database and schema exist
-- Run automatically by MariaDB on container initialization
-- ============================================

-- Set client encoding and timezone
SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS colombia_green_travel
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE colombia_green_travel;

-- Grant privileges to user (if user exists)
-- Note: User creation is handled by MariaDB environment variables
GRANT ALL PRIVILEGES ON colombia_green_travel.* TO 'appuser'@'%';
FLUSH PRIVILEGES;

-- Log completion
SELECT 'Database colombia_green_travel initialized successfully' AS status;

