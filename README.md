# Stock-DAG: Dockerized Airflow + PostgreSQL Stock Data Pipeline

A complete data pipeline using Apache Airflow and PostgreSQL to fetch OHLCV stock prices from `yfinance` and upsert them into a Postgres table with robust error handling and modular architecture.

## 🚀 Features

- **Apache Airflow** with CeleryExecutor + Redis for distributed task execution
- **PostgreSQL** with dedicated databases for Airflow metadata and stock data
- **Modular Python utilities** for data fetching and database operations
- **Environment-driven configuration** with `.env` file for secrets and settings
- **Robust DAG pipeline** with retries, logging, and idempotent upserts
- **Database GUI access** via pgAdmin web interface
- **Configurable data intervals** and scheduling
- **Graceful error handling** for missing data and network issues

## 📋 Prerequisites

### System Requirements
- **Docker Desktop** (version 20.10+)
- **Git** (optional, for version control)
- **8GB+ RAM** (recommended for smooth operation)
- **2GB+ free disk space**

### Port Requirements
- **Port 8080**: Airflow Web UI
- **Port 5432**: PostgreSQL database
- **Port 5050**: pgAdmin web interface

## 🏗️ Project Structure

```
Stock-DAG/
├── airflow/
│   └── Dockerfile                 # Custom Airflow image with dependencies
├── app/
│   ├── db.py                      # Database connection and operations
│   └── fetcher.py                 # yfinance data fetching utilities
├── dags/
│   └── stock_pipeline_dag.py      # Main Airflow DAG definition
├── init/
│   └── create_databases.sh        # Database initialization script
├── logs/                          # Airflow logs (created at runtime)
├── plugins/                       # Airflow plugins (optional)
├── docker-compose.yml             # Multi-service orchestration
├── requirements.txt               # Python dependencies
├── example.env                    # Environment variables template
├── README.md                      # This file
└── setup.md                       # Detailed setup instructions
```

## 🔄 Project Flow

### 1. **Initialization Phase**
- Docker containers start (PostgreSQL, Redis, Airflow services)
- PostgreSQL creates `airflow` and `stocks` databases
- Airflow initializes metadata and admin user

### 2. **DAG Execution Flow**
```
Trigger DAG → init_schema → context_window → extract → load → Complete
     ↓              ↓              ↓           ↓        ↓
  Create      Ensure table    Get time      Fetch    Upsert data
  DAG run     exists         window        data     to database
```

### 3. **Data Pipeline**
- **Fetch**: yfinance retrieves OHLCV data for configured tickers
- **Process**: Data is normalized and validated
- **Store**: Upserted into PostgreSQL with duplicate prevention
- **Monitor**: Logs and metrics available in Airflow UI

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# Database Configuration
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_PORT=5432
POSTGRES_DB_AIRFLOW=airflow
POSTGRES_DB_STOCKS=stocks

# Airflow Configuration
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
AIRFLOW_UID=50000

# Pipeline Configuration
STOCK_TICKERS=AAPL,MSFT                    # Comma-separated ticker symbols
SCHEDULE_INTERVAL=0 18 * * 1-5             # Cron expression for DAG scheduling
```

### Data Volume Control
- **Tickers**: Set via `STOCK_TICKERS` (e.g., `AAPL,MSFT,GOOGL`)
- **Time Window**: Configured in DAG (currently 7 days)
- **Data Interval**: Set in DAG (currently daily `"1d"`)
- **Schedule**: Set via `SCHEDULE_INTERVAL` (cron expression)

## 🎯 Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Stock-DAG
   cp example.env .env
   ```

2. **Start the stack**:
   ```bash
   docker compose up -d
   ```

3. **Access interfaces**:
   - **Airflow UI**: http://localhost:8080 (airflow/airflow)
   - **pgAdmin**: http://localhost:5050 (admin@example.com/admin)

4. **Enable and trigger DAG**:
   - In Airflow UI, toggle `stock_prices_pipeline` to ON
   - Click "Trigger DAG" to run manually

5. **View data**:
   - Use pgAdmin to browse `stocks` database
   - Or run: `docker exec stock-postgres psql -U airflow -d stocks -c "SELECT * FROM public.stock_prices ORDER BY price_ts DESC LIMIT 10;"`

## 📊 Data Model

### Database Schema
```sql
CREATE TABLE public.stock_prices (
    ticker TEXT NOT NULL,
    price_ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    PRIMARY KEY (ticker, price_ts)
);
```

### Sample Data
```
 ticker |      price_ts       |   open   |   high   |    low    |  close   |  volume
--------+---------------------+----------+----------+-----------+----------+----------
 AAPL   | 2025-08-19 00:00:00 | 231.28   | 232.87   | 229.35    | 230.56   | 39320800
 AAPL   | 2025-08-18 00:00:00 | 231.70   | 233.12   | 230.11    | 230.89   | 37476200
```

## 🔧 Customization

### Change Data Interval
Edit `dags/stock_pipeline_dag.py` line 48:
```python
interval="1h"    # Hourly data
interval="5m"    # 5-minute data
interval="1d"    # Daily data (current)
```

### Change Schedule
Edit `.env` file:
```bash
SCHEDULE_INTERVAL="0 0 * * *"     # Daily at midnight
SCHEDULE_INTERVAL="0 */6 * * *"   # Every 6 hours
SCHEDULE_INTERVAL="0 9-17 * * 1-5" # Market hours only
```

### Add More Tickers
Edit `.env` file:
```bash
STOCK_TICKERS=AAPL,MSFT,GOOGL,TSLA,AMZN
```

## 🐛 Troubleshooting

### Common Issues
- **Port conflicts**: Ensure ports 8080, 5432, 5050 are available
- **Docker not running**: Start Docker Desktop and wait for full initialization
- **DAG not appearing**: Check scheduler logs and ensure DAG file is valid
- **No data**: Verify ticker symbols and check yfinance availability

### Health Checks
```bash
# Check container status
docker compose ps

# Check service logs
docker compose logs airflow-scheduler
docker compose logs airflow-worker
docker compose logs postgres

# Verify database
docker exec stock-postgres psql -U airflow -l
```
