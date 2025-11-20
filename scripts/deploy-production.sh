#!/bin/bash
#
# Authelia Walled Garden - Deploy to Production Environment
#
# This script deploys TESTED changes from the git repository to production.
# ALWAYS test in staging first!
#
# Usage:
#   ./scripts/deploy-production.sh
#
# Prerequisites:
#   - Changes tested in staging environment
#   - Production environment at /opt/authelia-stack/
#   - Production .env file configured
#   - Backup directory exists

set -e

# Configuration
REPO_DIR="/home/dust/projects/walledgarden/walledgarden-gh"
PROD_DIR="/opt/authelia-stack"
BACKUP_DIR="/backups/authelia"

echo "════════════════════════════════════════════════════════════════"
echo "  ⚠️  PRODUCTION DEPLOYMENT ⚠️"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Repository: ${REPO_DIR}"
echo "Target: ${PROD_DIR}"
echo ""
echo "WARNING: This will deploy changes to your PRODUCTION environment!"
echo ""

# Verify we're in the repository directory
if [ ! -d "${REPO_DIR}/examples" ]; then
    echo "❌ ERROR: Repository directory not found or invalid"
    echo "Expected: ${REPO_DIR}/examples/"
    exit 1
fi

# Check if production directory exists
if [ ! -d "${PROD_DIR}" ]; then
    echo "❌ ERROR: Production directory not found: ${PROD_DIR}"
    exit 1
fi

# Safety checks
echo "Pre-deployment checks:"
echo ""

# Check 1: Git repository is clean
cd "${REPO_DIR}"
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  WARNING: Git repository has uncommitted changes"
    echo "It's recommended to commit and push before deploying to production"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? (yes/no): " continue_confirm
    if [ "$continue_confirm" != "yes" ]; then
        echo "Deployment cancelled"
        exit 1
    fi
fi

# Check 2: Confirm staging tested
echo ""
echo "Have you tested these changes in staging?"
read -p "Tested in staging? (yes/no): " staging_confirm

if [ "$staging_confirm" != "yes" ]; then
    echo ""
    echo "❌ ERROR: Changes must be tested in staging first!"
    echo ""
    echo "To deploy to staging:"
    echo "  ./scripts/deploy-staging.sh"
    echo ""
    exit 1
fi

# Check 3: Final confirmation
echo ""
echo "This deployment will:"
echo "  1. Create a backup of current production"
echo "  2. Stop production services (brief downtime)"
echo "  3. Deploy new configurations from git"
echo "  4. Restart production services"
echo ""
echo "Production services will be down for approximately 10-30 seconds."
echo ""
read -p "Proceed with PRODUCTION deployment? (yes/no): " final_confirm

if [ "$final_confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Starting production deployment..."
echo ""

# Step 1: Create backup
echo "Step 1/5: Creating backup..."
if [ -f "${REPO_DIR}/scripts/backup.sh" ]; then
    "${REPO_DIR}/scripts/backup.sh" "${BACKUP_DIR}"
    echo "✅ Backup created"
else
    echo "⚠️  Backup script not found, skipping backup"
    echo "Manual backup recommended!"
    read -p "Continue without backup? (yes/no): " backup_confirm
    if [ "$backup_confirm" != "yes" ]; then
        exit 1
    fi
fi

# Step 2: Stop production services
echo ""
echo "Step 2/5: Stopping production services..."
cd "${PROD_DIR}"
docker compose down
echo "✅ Services stopped"

# Step 3: Deploy configurations
echo ""
echo "Step 3/5: Deploying configurations..."

# Copy base configurations
cp "${REPO_DIR}/examples/docker-compose.yml" "${PROD_DIR}/"
echo "  ✅ docker-compose.yml"

cp "${REPO_DIR}/examples/Caddyfile" "${PROD_DIR}/"
echo "  ✅ Caddyfile"

# Copy Authelia configuration
cp "${REPO_DIR}/examples/authelia-config.yml" "${PROD_DIR}/authelia/configuration.yml"
echo "  ✅ authelia-config.yml"

# Copy dashboard files
cp "${REPO_DIR}/examples/dashboard/"*.html "${PROD_DIR}/dashboard/" 2>/dev/null || true
echo "  ✅ Dashboard files"

# Copy DNS tools
cp -r "${REPO_DIR}/examples/dns-tools/"* "${PROD_DIR}/dns-tools/" 2>/dev/null || true
echo "  ✅ DNS tools"

# Copy Cockpit config (if exists)
if [ -d "${PROD_DIR}/cockpit-config" ]; then
    cp "${REPO_DIR}/examples/cockpit/cockpit.conf" "${PROD_DIR}/cockpit-config/" 2>/dev/null || true
    echo "  ✅ Cockpit config"
fi

# Copy custom CSS/JS (if dashboard/css exists)
if [ -d "${PROD_DIR}/dashboard/css" ]; then
    cp "${REPO_DIR}/examples/authelia-custom.css" "${PROD_DIR}/dashboard/css/" 2>/dev/null || true
    cp "${REPO_DIR}/examples/inject-custom-css.js" "${PROD_DIR}/dashboard/" 2>/dev/null || true
    echo "  ✅ Custom styling"
fi

# Verify production .env exists
if [ ! -f "${PROD_DIR}/.env" ]; then
    echo ""
    echo "❌ ERROR: ${PROD_DIR}/.env not found!"
    echo "Production requires a .env file with secrets"
    exit 1
fi

echo ""
echo "✅ Configuration deployment complete"

# Step 4: Pull latest images
echo ""
echo "Step 4/5: Pulling latest Docker images..."
docker compose pull
echo "✅ Images updated"

# Step 5: Start production services
echo ""
echo "Step 5/5: Starting production services..."
docker compose up -d

# Wait for services to start
echo ""
echo "Waiting for services to start..."
sleep 5

# Check service status
echo ""
echo "Service status:"
docker compose ps

# Check for any failed services
FAILED=$(docker compose ps --filter "status=exited" --format "{{.Service}}" 2>/dev/null || true)
if [ -n "$FAILED" ]; then
    echo ""
    echo "⚠️  WARNING: Some services failed to start:"
    echo "$FAILED"
    echo ""
    echo "Check logs with: cd ${PROD_DIR} && docker compose logs -f"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ Production Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Deployment summary:"
echo "  - Backup location: ${BACKUP_DIR}"
echo "  - All services started successfully"
echo ""
echo "Next steps:"
echo "  1. Monitor logs: cd ${PROD_DIR} && docker compose logs -f"
echo "  2. Test production URL: https://run.nycapphouse.com"
echo "  3. Verify authentication works"
echo "  4. Check all services are accessible"
echo ""
echo "If issues occur, restore from backup:"
echo "  cd ${PROD_DIR}"
echo "  docker compose down"
echo "  # Extract backup and restore files"
echo "  docker compose up -d"
echo ""
