-- Run this file as a PostgreSQL administrator, then configure Django with .env.
-- Replace the placeholder outside version control. Never commit a real password.
CREATE USER buildcore WITH PASSWORD 'CHANGE_ME_BEFORE_RUNNING';
CREATE DATABASE buildcore OWNER buildcore;
GRANT ALL PRIVILEGES ON DATABASE buildcore TO buildcore;
