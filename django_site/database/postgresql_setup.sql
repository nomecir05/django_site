-- Run this file as a PostgreSQL administrator, then configure Django with .env.
-- Change these values before running in a shared or production database.
CREATE USER buildcore WITH PASSWORD 'crime@110';
CREATE DATABASE buildcore OWNER buildcore;
GRANT ALL PRIVILEGES ON DATABASE buildcore TO buildcore;