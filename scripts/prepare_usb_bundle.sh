#!/usr/bin/env bash
set -e

# ==========================================
# Script: prepare_usb_bundle.sh
# Purpose: Run this script on your INTERNET-CONNECTED MacBook/PC.
#          Downloads Docker packages (Debian/Ubuntu & RHEL/CentOS),
#          builds Docker images, and packages Python dependencies into a USB bundle.
# ==========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

BUNDLE_DIR="$PROJECT_ROOT/USB_OFFLINE_BUNDLE"
mkdir -p "$BUNDLE_DIR/docker_deb_packages"
mkdir -p "$BUNDLE_DIR/docker_rpm_packages"
mkdir -p "$BUNDLE_DIR/python_wheels"
mkdir -p "$BUNDLE_DIR/docker_images"

echo "=========================================================="
echo " 1. Checking Docker Availability"
echo "=========================================================="
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo "Docker engine detected and running."

    echo "Building Custom Grafana Docker Image (Offline Plugins)..."
    cat << 'EOF' > Dockerfile.grafana
FROM grafana/grafana:latest
USER root
RUN grafana-cli plugins install marcusolsson-dynamictext-panel || true
RUN grafana-cli plugins install volkovlabs-echarts-panel || true
USER grafana
EOF

    docker build -t custom_grafana:latest -f Dockerfile.grafana .
    rm Dockerfile.grafana

    echo "Building Aramco ETL App Docker Image..."
    docker build -t aramco_etl_app:latest .

    echo "Pulling PostgreSQL Docker Image..."
    docker pull postgres:15-alpine

    echo "Exporting Docker Images to tar.gz Archive..."
    docker save postgres:15-alpine custom_grafana:latest aramco_etl_app:latest | gzip > "$BUNDLE_DIR/docker_images/offline_docker_images.tar.gz"
else
    echo "NOTICE: Docker is not currently running on this computer."
    echo "If Docker Desktop is installed, please start it to export Docker images."
    echo "Skipping Docker image build on this machine..."
fi

echo "=========================================================="
echo " 2. Downloading Python Wheel Dependencies"
echo "=========================================================="
if command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1; then
    PIP_CMD=$(command -v pip3 || command -v pip)
    $PIP_CMD download -r requirements.txt -d "$BUNDLE_DIR/python_wheels" || true
fi

echo "=========================================================="
echo " 3. Downloading Ubuntu / Debian Docker .deb Packages"
echo "=========================================================="
cd "$BUNDLE_DIR/docker_deb_packages"
CONTAINERD_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/containerd.io_1.6.33-1_amd64.deb"
DOCKER_CE_CLI_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-ce-cli_26.1.4-1~ubuntu.22.04~jammy_amd64.deb"
DOCKER_CE_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-ce_26.1.4-1~ubuntu.22.04~jammy_amd64.deb"
BUILDX_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-buildx-plugin_0.14.1-1~ubuntu.22.04~jammy_amd64.deb"
COMPOSE_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-compose-plugin_2.27.1-1~ubuntu.22.04~jammy_amd64.deb"

curl -L -O -s "$CONTAINERD_URL" || true
curl -L -O -s "$DOCKER_CE_CLI_URL" || true
curl -L -O -s "$DOCKER_CE_URL" || true
curl -L -O -s "$BUILDX_URL" || true
curl -L -O -s "$COMPOSE_URL" || true

echo "=========================================================="
echo " 4. Downloading RHEL / CentOS / Rocky Docker .rpm Packages"
echo "=========================================================="
cd "$BUNDLE_DIR/docker_rpm_packages"
RPM_CONTAINERD="https://download.docker.com/linux/centos/8/x86_64/stable/Packages/containerd.io-1.6.33-3.1.el8.x86_64.rpm"
RPM_DOCKER_CLI="https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-cli-26.1.4-1.el8.x86_64.rpm"
RPM_DOCKER_CE="https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-ce-26.1.4-1.el8.x86_64.rpm"
RPM_COMPOSE="https://download.docker.com/linux/centos/8/x86_64/stable/Packages/docker-compose-plugin-2.27.1-1.el8.x86_64.rpm"

curl -L -O -s "$RPM_CONTAINERD" || true
curl -L -O -s "$RPM_DOCKER_CLI" || true
curl -L -O -s "$RPM_DOCKER_CE" || true
curl -L -O -s "$RPM_COMPOSE" || true

cd "$PROJECT_ROOT"

echo "=========================================================="
echo " 5. Copying Application Code & Environment Config"
echo "=========================================================="
mkdir -p "$BUNDLE_DIR/pyton_newETL"
rsync -av --exclude='USB_OFFLINE_BUNDLE' --exclude='.git' --exclude='__pycache__' "$PROJECT_ROOT/" "$BUNDLE_DIR/pyton_newETL/"

if [ ! -f "$BUNDLE_DIR/pyton_newETL/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$BUNDLE_DIR/pyton_newETL/.env"
fi

cp "$PROJECT_ROOT/scripts/install_offline.sh" "$BUNDLE_DIR/install-offline.sh"
chmod +x "$BUNDLE_DIR/install-offline.sh" "$BUNDLE_DIR/pyton_newETL/scripts/install_offline.sh"

echo "=========================================================="
echo " SUCCESS! USB Offline Bundle generated at:"
echo " $BUNDLE_DIR"
echo "=========================================================="
