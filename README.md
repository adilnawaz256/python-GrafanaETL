# Aramco Network Monitoring ETL & Grafana Platform - Client Deployment Guide

This document outlines the steps required to configure, deploy, and operate the **Aramco Network Monitoring ETL Data Pipeline & Grafana Visualization Platform** using the provided deployment package.

---

## 1. Package Contents

The deployment archive contains the following components:

```
.
├── docker-compose.yml               # Multi-container orchestration (PostgreSQL, ETL Worker, Grafana)
├── Dockerfile                       # Python 3.11 ETL Worker container specification
├── .env.example                     # Environment configuration template
├── aramco_grafana_dashboard.json    # Complete pre-configured Grafana dashboard JSON
├── sql/
│   ├── schema.sql                   # Database table definitions & unique constraints
│   └── indexes.sql                  # Query performance indexes
├── app/                             # Core Python ETL application source code
├── data/                            # File storage directories (input, processing, processed, failed)
└── grafana/                         # Grafana provisioning & datasource configurations
```

---

## 2. Step 1: Environment Configuration (`.env`)

Before launching the application, create your local environment file by copying `.env.example`:

```bash
cp .env.example .env
```

Open `.env` in a text editor and customize the parameters for your deployment environment:

### Mandatory Fields to Customize:

```ini
# =====================================================================
# 1. Database Credentials
# =====================================================================
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=aramco_etl
DATABASE_USER=postgres
DATABASE_PASSWORD=Set_Your_Database_Password_Here

# =====================================================================
# 2. Grafana Configuration
# =====================================================================
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=Set_Your_Grafana_Admin_Password_Here

# Set your server IP or domain URL here (e.g., http://192.168.1.100:3000/ or https://grafana.yourdomain.com/)
GRAFANA_SERVER_ROOT_URL=http://localhost:3000/

# =====================================================================
# 3. ETL Worker Sweep Interval (in seconds)
# =====================================================================
# 900 = 15 minutes sweep cycle
RUN_INTERVAL_SECONDS=900

# =====================================================================
# 4. Remote SFTP Credentials (Optional)
# Set SFTP_ENABLED=true if downloading files from a remote SFTP server
# =====================================================================
SFTP_ENABLED=false
SFTP_HOST=sftp.yourdomain.com
SFTP_PORT=22
SFTP_USERNAME=your_sftp_user
SFTP_PASSWORD=your_sftp_password
SFTP_REMOTE_DIR=.
SFTP_DELETE_AFTER_DOWNLOAD=false
```

---

## 3. Step 2: Deploying the Application

Execute the following commands from the root directory of the unzipped package:

```bash
# Build container images and start services in detached mode
DOCKER_BUILDKIT=0 docker-compose build etl_app
docker-compose up -d
```

### Verify Service Status

Check that all three containers are running:

```bash
docker-compose ps
```

You should see:
* `aramco_postgres` (Healthy)
* `aramco_etl_app` (Running)
* `aramco_grafana` (Running)

---

## 4. Step 3: Accessing Grafana & Importing Dashboard

1. Open your web browser and navigate to your Grafana URL:
   * **URL**: `http://<YOUR_SERVER_IP>:3000` (or configured `GRAFANA_SERVER_ROOT_URL`)
   * **Username**: Value of `GRAFANA_ADMIN_USER` from `.env` (default: `admin`)
   * **Password**: Value of `GRAFANA_ADMIN_PASSWORD` from `.env`

2. **Database Datasource**:
   * The PostgreSQL data source (`PostgreSQL`) is automatically provisioned and pre-connected.

3. **Importing the Dashboard**:
   * In Grafana, click **Dashboards** -> **New** -> **Import**.
   * Click **Upload dashboard JSON file** and select **`aramco_grafana_dashboard.json`** from the root folder.
   * Click **Import**.

All 45 pre-configured panels covering all 9 network domains will automatically populate with live data.

---

## 5. Operations & Maintenance

### View Live Pipeline Logs
```bash
docker logs -f aramco_etl_app
```

### Restart Services
```bash
docker-compose restart
```

### Stop Application Stack
```bash
docker-compose down
```

### Complete Database Reset (Clear All Data & Re-process Files)
If you ever need to reset the database and re-process all source files:

```bash
# 1. Stop stack and delete database volume
docker-compose down -v

# 2. Reset input files
mkdir -p data/input data/processed data/failed
mv data/failed/* data/input/ 2>/dev/null || true
mv data/processed/* data/input/ 2>/dev/null || true

# 3. Start stack fresh
DOCKER_BUILDKIT=0 docker-compose build etl_app
docker-compose up -d
```
