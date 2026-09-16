# Aramco Grafana + PostgreSQL ETL System

A production-ready, idempotent Python ETL data pipeline for Aramco network monitoring datasets. Designed to safely process overlapping 24-hour rolling window files (Excel & CSV) into clean PostgreSQL tables for Grafana visual dashboards without creating duplicate business records.

---

## Key Architecture & Design Highlights

1. **Idempotent Rolling 24-Hour Processing**:
   - Uses PostgreSQL native `INSERT ... ON CONFLICT (...) DO UPDATE` based on business natural unique keys (`(stime, cscf)`, `(stime, cmg)`, `(stime, d1_plmn)`, `(stime, device_name, n_interface)`, `(alarm_id, event_time)`, `(issue_key)`).
   - When overlapping 24-hour files arrive, existing records are updated and new records are inserted cleanly.

2. **Fault Isolation Guarantee**:
   - Each file runs inside an isolated transaction batch.
   - If batch 14:15 fails (e.g. missing required header columns), the error is logged in `etl_file_errors`, batch status is set to `FAILED`, an alert is triggered, and the pipeline **immediately proceeds to batch 14:30**.
   - Rolling backfill data in batch 14:30 recovers the 14:15 business records cleanly.

3. **Full Traceability**:
   - Every file delivery receives a unique `batch_id`.
   - Original un-transformed source rows are preserved in `raw_source_records` as PostgreSQL `JSONB`.
   - All Grafana-facing core business records store `source_batch_id` for end-to-end data lineage back to raw source files.

4. **Scheduler Independent**:
   - Core ETL logic is completely decoupled from cron. Can be triggered via cron, Airflow, ECS scheduled tasks, or EventBridge without modifying any ETL code.

---

## Directory Structure

```
.
├── app/
│   ├── alerts/           # Alerting notifier (webhooks)
│   ├── config/           # Configuration settings & env loader
│   ├── db/               # PostgreSQL connection pool & repositories
│   ├── discovery/        # File scanner, SHA-256 hash & lifecycle manager
│   ├── etl/              # Batch manager, retry mechanism, main pipeline
│   ├── ingestion/        # CSV & Excel readers
│   ├── logging/          # Structured logger
│   ├── loaders/          # PostgreSQL native UPSERT loaders
│   ├── transformation/   # Domain transformers (RAN, IMS, CMG, CMM, Alarms, SMSC, Transport, Tickets)
│   ├── utils/            # Hashing and timestamp extraction utilities
│   ├── validation/       # Header & row validation engine
│   └── reprocess.py      # CLI tool for re-executing failed batches/files
├── sql/
│   ├── schema.sql        # Table DDL definitions & unique constraints
│   └── indexes.sql       # Performance & Grafana query indexes
├── scripts/
│   └── run_etl.sh        # Cron execution script
├── grafana/
│   └── queries.sql       # Grafana dashboard SQL queries
├── tests/                # Automated pytest suite
├── main.py               # Main pipeline execution entrypoint
├── Dockerfile            # Container image definition
├── docker-compose.yml    # Local development stack (PostgreSQL + ETL App)
├── requirements.txt      # Python dependencies
├── .env.example          # Environment configuration template
└── README.md             # System documentation
```

---

## Quick Start & Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure your database and folder settings:

```bash
cp .env.example .env
```

Example `.env` settings:

```ini
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=aramco_etl
DATABASE_USER=postgres
DATABASE_PASSWORD=postgrespassword

INPUT_FOLDER=./data/input
PROCESSING_FOLDER=./data/processing
PROCESSED_FOLDER=./data/processed
FAILED_FOLDER=./data/failed
ARCHIVE_FOLDER=./data/archive

CRON_SCHEDULE=*/15 * * * *
LOG_LEVEL=INFO
SUPPORTED_FILE_EXTENSIONS=.xlsx,.xls,.csv
ALERT_ENABLED=true
ALERT_WEBHOOK_URL=http://localhost:8080/alerts
```

### 2. Database Migration

Run the DDL scripts to create PostgreSQL schemas and indexes:

```bash
psql -h localhost -U postgres -d aramco_etl -f sql/schema.sql
psql -h localhost -U postgres -d aramco_etl -f sql/indexes.sql
```

### 3. Local Execution

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the pipeline:

```bash
python main.py
```

### 4. Running with Docker Compose

To launch the complete local stack (PostgreSQL + ETL application container):

```bash
docker-compose up -d --build
```

---

## Scheduling with Cron

Add the execution script to crontab:

```bash
crontab -e
```

Add entry (runs every 15 minutes):

```cron
*/15 * * * * /path/to/pyton_newETL/scripts/run_etl.sh >> /path/to/pyton_newETL/cron.log 2>&1
```

---

## Reprocessing Commands

Reprocess a batch by `batch_id`:

```bash
python -m app.reprocess --batch-id 1025
```

Reprocess a specific file by filename:

```bash
python -m app.reprocess --file RAN_2026-09-15_14-15.xlsx
```

---

## Automated Test Suite

Run the full pytest suite:

```bash
python -m pytest -v tests/
```

Test coverage includes:
- File discovery, hashing, and chronological sorting
- Duplicate file delivery skipping via content SHA-256 hash
- Header mismatch detection & error logging
- Domain transformations & device name extraction
- PostgreSQL `ON CONFLICT DO UPDATE` UPSERT logic
- **Critical Failure Isolation Test**: Simulates 14:00 (SUCCESS), 14:15 (FAILED header mismatch), and 14:30 (SUCCESS with overlapping 14:15 data), verifying that missing 14:15 records exist exactly once after 14:30 processing.
