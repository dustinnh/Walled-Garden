#!/bin/bash
#
# Authelia Walled Garden - Deploy to Staging Environment
#
# This script deploys the current git repository state to a staging environment
# for testing before production deployment.
#
# Usage:
#   ./scripts/deploy-staging.sh
#
# Prerequisites:
#   - Staging environment exists at /opt/authelia-staging/
#   - Staging .env file configured with secrets
#   - Docker and Docker Compose installed

set -e

# Configuration
REPO_DIR="/home/dust/projects/walledgarden/walledgarden-gh"
STAGING_DIR="/opt/authelia-staging"

echo "════════════════════════════════════════════════════════════════"
echo "  Authelia Walled Garden - Deploy to STAGING"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Repository: ${REPO_DIR}"
echo "Target: ${STAGING_DIR}"
echo ""

# Verify we're in the repository directory
if [ ! -d "${REPO_DIR}/examples" ]; then
    echo "❌ ERROR: Repository directory not found or invalid"
    echo "Expected: ${REPO_DIR}/examples/"
    exit 1
fi

# Check if staging directory exists
if [ ! -d "${STAGING_DIR}" ]; then
    echo "⚠️  WARNING: Staging directory does not exist: ${STAGING_DIR}"
    echo ""
    echo "To create a staging environment, run:"
    echo "  sudo cp -r /opt/authelia-stack ${STAGING_DIR}"
    echo "  sudo chown -R \$(whoami):\$(whoami) ${STAGING_DIR}"
    echo ""
    echo "Then generate staging secrets:"
    echo "  ${REPO_DIR}/scripts/generate-secrets.sh > ${STAGING_DIR}/.env.staging"
    echo ""
    exit 1
fi

# Confirm deployment
echo "This will deploy the following to staging:"
echo "  - docker-compose.yml"
echo "  - Caddyfile"
echo "  - authelia-config.yml"
echo "  - Dashboard files"
echo "  - DNS tools"
echo ""
echo "Existing .env and users_database.yml will be preserved."
echo ""
read -p "Continue with staging deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Deploying to staging..."
echo ""

# Stop current staging services
echo "Stopping staging services..."
cd "${STAGING_DIR}"
docker compose down || true

# Copy base configurations from git repository
echo "Copying configurations..."
cp "${REPO_DIR}/examples/docker-compose.yml" "${STAGING_DIR}/"
cp "${REPO_DIR}/examples/Caddyfile" "${STAGING_DIR}/"

# Copy Authelia configuration
mkdir -p "${STAGING_DIR}/authelia"
cp "${REPO_DIR}/examples/authelia-config.yml" "${STAGING_DIR}/authelia/configuration.yml"

# Copy dashboard files
echo "Copying dashboard files..."
mkdir -p "${STAGING_DIR}/dashboard"
cp "${REPO_DIR}/examples/dashboard/"*.html "${STAGING_DIR}/dashboard/" 2>/dev/null || true

# Copy DNS tools
echo "Copying DNS tools..."
mkdir -p "${STAGING_DIR}/dns-tools"
cp -r "${REPO_DIR}/examples/dns-tools/"* "${STAGING_DIR}/dns-tools/" 2>/dev/null || true

# Copy Cockpit config (optional)
if [ -d "${STAGING_DIR}/cockpit-config" ]; then
    echo "Copying Cockpit configuration..."
    cp "${REPO_DIR}/examples/cockpit/cockpit.conf" "${STAGING_DIR}/cockpit-config/" 2>/dev/null || true
fi

# Copy custom CSS/JS
echo "Copying custom styling..."
cp "${REPO_DIR}/examples/authelia-custom.css" "${STAGING_DIR}/dashboard/css/" 2>/dev/null || true
cp "${REPO_DIR}/examples/inject-custom-css.js" "${STAGING_DIR}/dashboard/" 2>/dev/null || true

# Verify .env exists (staging secrets)
if [ ! -f "${STAGING_DIR}/.env" ]; then
    echo ""
    echo "⚠️  WARNING: ${STAGING_DIR}/.env not found"
    echo "Staging environment needs a .env file with secrets"
    echo ""
    echo "Generate with:"
    echo "  ${REPO_DIR}/scripts/generate-secrets.sh > ${STAGING_DIR}/.env"
    echo ""
    read -p "Continue anyway? (yes/no): " continue_confirm
    if [ "$continue_confirm" != "yes" ]; then
        exit 1
    fi
fi

# Pull latest images
echo ""
echo "Pulling latest Docker images..."
docker compose pull

# Start services
echo ""
echo "Starting staging services..."
docker compose up -d

# Wait for services to start
echo ""
echo "Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "Service status:"
docker compose ps

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Staging Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Check logs: cd ${STAGING_DIR} && docker compose logs -f"
echo "  2. Test staging environment thoroughly"
echo "  3. If tests pass, deploy to production with: ./scripts/deploy-production.sh"
echo ""
echo "Staging URL: https://staging.example.com (or your configured staging domain)"
echo ""
