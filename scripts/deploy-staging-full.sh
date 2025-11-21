#!/bin/bash
#
# Walledgarden + Authelia-Admin - Full Staging Deployment
#
# This script deploys both walledgarden configurations and authelia-admin
# to the staging environment for integrated testing.
#
# Usage:
#   ./scripts/deploy-staging-full.sh
#
# Prerequisites:
#   - Staging environment exists at /opt/authelia-staging/
#   - Walledgarden source at /home/dust/projects/walledgarden/walledgarden-gh/
#   - Authelia-admin source at /home/dust/projects/authelia-admin/authelia-file-admin/
#

set -e

# Configuration
WALLEDGARDEN_DIR="/home/dust/projects/walledgarden/walledgarden-gh"
AUTHELIA_ADMIN_DIR="/home/dust/projects/authelia-admin"

echo "════════════════════════════════════════════════════════════════"
echo "  Full Staging Deployment - Walledgarden + Authelia-Admin"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Deploy walledgarden configurations
echo "Step 1: Deploying walledgarden configurations..."
echo "────────────────────────────────────────────────────────────────"
if [ -f "${WALLEDGARDEN_DIR}/scripts/deploy-staging.sh" ]; then
    cd "${WALLEDGARDEN_DIR}"
    ./scripts/deploy-staging.sh
else
    echo "⚠️  Walledgarden deploy script not found, skipping..."
fi

echo ""
echo "Step 2: Deploying authelia-admin from source..."
echo "────────────────────────────────────────────────────────────────"
if [ -f "${AUTHELIA_ADMIN_DIR}/scripts/deploy-staging.sh" ]; then
    cd "${AUTHELIA_ADMIN_DIR}"
    ./scripts/deploy-staging.sh
else
    echo "❌ ERROR: Authelia-admin deploy script not found!"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Full Staging Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Staging URL: https://staging.nycapphouse.com:8443"
echo "Admin Panel: https://staging.nycapphouse.com:8443/api/admin/"
echo ""
echo "Test credentials:"
echo "  admin1 / TestAdmin123! (admin)"
echo "  testuser1 / TestUser123! (user)"
echo ""
echo "Monitor all services:"
echo "  cd /opt/authelia-staging && docker compose logs -f"
echo ""