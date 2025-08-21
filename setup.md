# Stock-DAG Setup Guide

Detailed step-by-step instructions for setting up the Stock-DAG pipeline from scratch.

## 📋 Prerequisites Verification

### 1. System Requirements Check

#### Docker Desktop Installation
```bash
# Check Docker version (should be 20.10+)
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker is running
docker info
```

**Expected Output:**
```
Docker version 28.3.2, build 578ccf6
Docker Compose version v2.38.2-desktop.1
```

#### System Resources
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Disk Space**: Minimum 2GB free space
- **CPU**: 2+ cores recommended

#### Port Availability Check
```bash
# Check if required ports are available
netstat -an | findstr ":8080\|:5432\|:5050"
```

**Expected Output:** No output (ports should be free)

### 2. Project Structure Verification

Ensure your project directory contains:
```
Stock-DAG/
├── airflow/Dockerfile
├── app/db.py
├── app/fetcher.py
├── dags/stock_pipeline_dag.py
├── init/create_databases.sh
├── docker-compose.yml
├── requirements.txt
├── example.env
├── README.md
└── setup.md
```

## 🚀 Step-by-Step Setup

### Step 1: Environment Configuration



**Default Environment Variables:**
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
STOCK_TICKERS=AAPL,MSFT
SCHEDULE_INTERVAL=0 18 * * 1-5
```

### Step 2: Docker Image Build

```bash
# Build custom Airflow image with all dependencies
docker compose build

# Expected output: Successfully built images for all services
```

**What happens during build:**
- Downloads Python 3.11 base image
- Installs Apache Airflow 2.9.1 with Celery, PostgreSQL, Redis providers
- Installs project dependencies (yfinance, psycopg2-binary, etc.)
- Copies application code into the image

### Step 3: Database Initialization

```bash
# Initialize Airflow database and create admin user
docker compose up airflow-init

# Expected output: 
# - Creates airflow and stocks databases
# - Runs Airflow database migrations
# - Creates admin user (airflow/airflow)
# - Exits with success message
```

### Step 4: Start All Services

```bash
# Start all services in detached mode
docker compose up -d

# Expected output: All containers started successfully
```

**Services started:**
- `stock-postgres`: PostgreSQL database
- `stock-redis`: Redis message broker
- `airflow-webserver`: Airflow web interface
- `airflow-scheduler`: Airflow task scheduler
- `airflow-worker`: Airflow task executor
- `airflow-triggerer`: Airflow triggerer
- `stock-pgadmin`: pgAdmin web interface

### Step 5: Verify Services

```bash
# Check container status
docker compose ps

# Expected output: All containers should show "Running" status
```

**Health Check Commands:**
```bash
# Check Airflow webserver health
curl http://localhost:8080/health

# Check PostgreSQL connection
docker exec stock-postgres pg_isready -U airflow

# Check Redis connection
docker exec stock-redis redis-cli ping
```

## 🔧 Configuration Options

### 1. Stock Tickers Configuration

Edit `.env` file:
```bash
# Single ticker
STOCK_TICKERS=AAPL

# Multiple tickers
STOCK_TICKERS=AAPL,MSFT,GOOGL,TSLA,AMZN

# Different markets
STOCK_TICKERS=AAPL,MSFT,^GSPC,^DJI
```

### 2. Schedule Configuration

Edit `.env` file with cron expressions:
```bash
# Daily at midnight
SCHEDULE_INTERVAL="0 0 * * *"

# Market close daily (Mon-Fri)
SCHEDULE_INTERVAL="0 18 * * 1-5"

# Every 6 hours
SCHEDULE_INTERVAL="0 */6 * * *"

# Market hours only (9 AM - 5 PM, Mon-Fri)
SCHEDULE_INTERVAL="0 9-17 * * 1-5"

# Every 15 minutes during market hours
SCHEDULE_INTERVAL="*/15 9-16 * * 1-5"
```



### 4. Time Window Configuration

Edit `dags/stock_pipeline_dag.py` lines 68-69:
```python
# 7 days (current)
start_dt = now - timedelta(days=7)
end_dt = now - timedelta(days=1)

# 30 days
start_dt = now - timedelta(days=30)
end_dt = now - timedelta(days=1)

# Just yesterday
start_dt = now - timedelta(days=1)
end_dt = now - timedelta(days=1)
```

## 🌐 Accessing Interfaces

### 1. Airflow Web UI

**URL:** http://localhost:8080
**Credentials:**
- Username: `airflow`
- Password: `airflow`

**Initial Setup:**
1. Login with credentials
2. Navigate to "DAGs" tab
3. Find `stock_prices_pipeline`
4. Toggle the switch to enable the DAG
5. Click "Trigger DAG" to run manually

### 2. pgAdmin Database Interface

**URL:** http://localhost:5050
**Credentials:**
- Email: `admin@example.com`
- Password: `admin`

**Database Connection Setup:**
1. Login to pgAdmin
2. Right-click "Servers" → "Register" → "Server"
3. **General Tab:**
   - Name: `Stock Database`
4. **Connection Tab:**
   - Host: `stock-postgres`
   - Port: `5432`
   - Database: `stocks`
   - Username: `airflow`
   - Password: `airflow`
5. Click "Save"
6. Navigate to: Servers → Stock Database → Databases → stocks → Schemas → public → Tables → stock_prices
7. Right-click → "View/Edit Data" → "All Rows"



### Run the Applications:
docker compose build

docker compose up -d

### 3. Command Line Database Access

```bash
# Connect to PostgreSQL
docker exec -it stock-postgres psql -U airflow -d stocks

# View table structure
\d public.stock_prices

# Query recent data
SELECT ticker, price_ts, open, high, low, close, volume 
FROM public.stock_prices 
ORDER BY price_ts DESC 
LIMIT 10;

# Count total rows
SELECT COUNT(*) FROM public.stock_prices;

# Exit PostgreSQL
\q
```
