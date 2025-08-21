#!/bin/sh
set -e

# Use the default DB for connection (POSTGRES_DB may be set to 'airflow')
DB_NAME="${POSTGRES_DB:-postgres}"

# Create airflow DB if missing
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" -tc "SELECT 1 FROM pg_database WHERE datname = 'airflow'" | grep -q 1 || \
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" -c "CREATE DATABASE airflow;"

# Create stocks DB if missing
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" -tc "SELECT 1 FROM pg_database WHERE datname = 'stocks'" | grep -q 1 || \
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DB_NAME" -c "CREATE DATABASE stocks;"

