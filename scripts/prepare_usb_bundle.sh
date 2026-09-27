#!/usr/bin/env bash
set -e

# ==========================================
# Script: prepare_usb_bundle.sh
# Purpose: Run this script on your INTERNET-CONNECTED machine.
#          It downloads all Ubuntu packages, Docker images, Grafana plugins,
#          and Python wheels into a single USB bundle folder.
# ==========================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$PROJECT_ROOT"

BUNDLE_DIR="$PROJECT_ROOT/USB_OFFLINE_BUNDLE"
mkdir -p "$BUNDLE_DIR/docker_deb_packages"
mkdir -p "$BUNDLE_DIR/python_wheels"
mkdir -p "$BUNDLE_DIR/docker_images"

echo "=========================================================="
echo " 1. Building Custom Grafana Docker Image (Offline Plugins)"
echo "=========================================================="
cat << 'EOF' > Dockerfile.grafana
FROM grafana/grafana:latest
USER root
RUN grafana-cli plugins install marcusolsson-dynamictext-panel || true
RUN grafana-cli plugins install volkovlabs-echarts-panel || true
USER grafana
EOF

docker build -t custom_grafana:latest -f Dockerfile.grafana .
rm Dockerfile.grafana

echo "=========================================================="
echo " 2. Building Aramco ETL App Docker Image"
echo "=========================================================="
docker build -t aramco_etl_app:latest .

echo "=========================================================="
echo " 3. Pulling PostgreSQL Docker Image"
echo "=========================================================="
docker pull postgres:15-alpine

echo "=========================================================="
echo " 4. Exporting Docker Images to tar.gz Archive"
echo "=========================================================="
echo "Saving images (this may take a few minutes)..."
docker save postgres:15-alpine custom_grafana:latest aramco_etl_app:latest | gzip > "$BUNDLE_DIR/docker_images/offline_docker_images.tar.gz"

echo "=========================================================="
echo " 5. Downloading Python Wheel Dependencies (Fallback)"
echo "=========================================================="
pip download -r requirements.txt -d "$BUNDLE_DIR/python_wheels"

echo "=========================================================="
echo " 6. Downloading Ubuntu Docker .deb Packages"
echo "=========================================================="
echo "Downloading Ubuntu 22.04 LTS Docker packages..."
mkdir -p "$BUNDLE_DIR/docker_deb_packages"
cd "$BUNDLE_DIR/docker_deb_packages"

# Ubuntu 22.04 (Jammy) Docker CE download links
BASE_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64"
# Standard Ubuntu download paths from official Docker repo
CONTAINERD_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/containerd.io_1.6.33-1_amd64.deb"
DOCKER_CE_CLI_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-ce-cli_26.1.4-1~ubuntu.22.04~jammy_amd64.deb"
DOCKER_CE_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-ce_26.1.4-1~ubuntu.22.04~jammy_amd64.deb"
BUILDX_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-buildx-plugin_0.14.1-1~ubuntu.22.04~jammy_amd64.deb"
COMPOSE_URL="https://download.docker.com/linux/ubuntu/dags/jammy/pool/stable/amd64/docker-compose-plugin_2.27.1-1~ubuntu.22.04~jammy_amd64.deb"

# Fetch packages if curl or wget available
curl -L -O -s "$CONTAINERD_URL" || true
curl -L -O -s "$DOCKER_CE_CLI_URL" || true
curl -L -O -s "$DOCKER_CE_URL" || true
curl -L -O -s "$BUILDX_URL" || true
curl -L -O -s "$COMPOSE_URL" || true

cd "$PROJECT_ROOT"

echo "=========================================================="
echo " 7. Copying Application Code & Environment Config"
echo "=========================================================="
mkdir -p "$BUNDLE_DIR/pyton_newETL"
rsync -av --exclude='USB_OFFLINE_BUNDLE' --exclude='.git' --exclude='__pycache__' "$PROJECT_ROOT/" "$BUNDLE_DIR/pyton_newETL/"

if [ ! -f "$BUNDLE_DIR/pyton_newETL/.env" ]; then
    cp "$PROJECT_ROOT/.env.example" "$BUNDLE_DIR/pyton_newETL/.env"
fi

# Copy install-offline.sh to the root of USB_OFFLINE_BUNDLE
cp "$PROJECT_ROOT/scripts/install_offline.sh" "$BUNDLE_DIR/install-offline.sh"
chmod +x "$BUNDLE_DIR/install-offline.sh" "$BUNDLE_DIR/pyton_newETL/scripts/install_offline.sh"

echo "=========================================================="
echo " SUCCESS! USB Offline Bundle generated at:"
echo " $BUNDLE_DIR"
echo "=========================================================="
echo "Instructions:"
echo "1. Copy the '$BUNDLE_DIR' folder onto your USB Pendrive."
echo "2. Insert USB Pendrive into target offline computer."
echo "3. Run 'sudo bash install-offline.sh' on the offline machine."
echo "=========================================================="
