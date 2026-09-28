#!/usr/bin/env bash
set -e

# ==========================================
# Script: install_offline.sh
# Purpose: Universal Offline Installer script for target server.
#          Supports Ubuntu/Debian (.deb) & RHEL/CentOS/Rocky (.rpm).
# ==========================================

if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root or with sudo:"
  echo "  sudo bash install_offline.sh"
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Resolve bundle root directory
if [ -d "$SCRIPT_DIR/docker_deb_packages" ] || [ -d "$SCRIPT_DIR/docker_rpm_packages" ]; then
    BUNDLE_DIR="$SCRIPT_DIR"
elif [ -d "$SCRIPT_DIR/../../docker_deb_packages" ] || [ -d "$SCRIPT_DIR/../../docker_rpm_packages" ]; then
    BUNDLE_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"
else
    BUNDLE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
fi

APP_DIR="$BUNDLE_DIR/pyton_newETL"

echo "=========================================================="
echo " 1. Installing Docker Offline (Auto-Detecting OS Package Manager)"
echo "=========================================================="

if command -v docker >/dev/null 2>&1; then
    echo "Docker is already installed on this machine."
else
    DEB_DIR="$BUNDLE_DIR/docker_deb_packages"
    RPM_DIR="$BUNDLE_DIR/docker_rpm_packages"

    if command -v dpkg >/dev/null 2>&1 && [ -d "$DEB_DIR" ] && [ "$(ls -A "$DEB_DIR"/*.deb 2>/dev/null)" ]; then
        echo "Detected Ubuntu/Debian system. Installing .deb packages..."
        dpkg -i "$DEB_DIR"/*.deb || apt-get install -f -y
    elif command -v rpm >/dev/null 2>&1 && [ -d "$RPM_DIR" ] && [ "$(ls -A "$RPM_DIR"/*.rpm 2>/dev/null)" ]; then
        echo "Detected RHEL/CentOS/Rocky Linux. Installing .rpm packages..."
        rpm -Uvh --replacepkgs "$RPM_DIR"/*.rpm || true
    else
        echo "ERROR: Could not find valid offline Docker packages (.deb or .rpm)."
        exit 1
    fi

    systemctl enable --now docker || true
    echo "Docker service installed and started!"
fi

echo "=========================================================="
echo " 2. Loading Offline Docker Images"
echo "=========================================================="
IMAGE_DIR="$BUNDLE_DIR/docker_images"
if [ -d "$IMAGE_DIR" ] && [ "$(ls -A "$IMAGE_DIR"/*.tar* 2>/dev/null)" ]; then
    echo "Loading Docker images into daemon..."
    for img in "$IMAGE_DIR"/*.tar*; do
        if [ -f "$img" ]; then
            FILE_NAME=$(basename "$img")
            FILE_SIZE=$(du -h "$img" | awk '{print $1}')
            echo "----------------------------------------------------------"
            echo "Loading image archive: $FILE_NAME ($FILE_SIZE)..."
            echo "Decompressing layer archives into Docker daemon. Please wait..."
            
            if [[ "$img" == *.gz ]]; then
                gunzip -c "$img" | docker load
            else
                docker load -i "$img"
            fi
            echo "✓ Successfully loaded $FILE_NAME into Docker!"
        fi
    done
    echo "=========================================================="
    echo "All Docker images loaded successfully!"
else
    echo "ERROR: No Docker image archives found in: $IMAGE_DIR"
    exit 1
fi

echo "=========================================================="
echo " 3. Launching Container Stack via Docker Compose"
echo "=========================================================="
cd "$APP_DIR"

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Starting PostgreSQL, Grafana, and ETL Application..."
if docker compose version >/dev/null 2>&1; then
    docker compose up -d
elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d
else
    echo "ERROR: Docker Compose CLI plugin not found."
    exit 1
fi

echo "=========================================================="
echo " 4. Verifying Running Containers"
echo "=========================================================="
sleep 5
docker ps

echo ""
echo "=========================================================="
echo " DEPLOYMENT COMPLETE & SUCCESSFUL! "
echo "=========================================================="
