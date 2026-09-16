#!/usr/bin/env bash
set -e

# Change directory to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] Running Aramco ETL cron job..."

# Activate virtualenv if present
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run main Python ETL application
python3 main.py

echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] Aramco ETL cron execution finished."
