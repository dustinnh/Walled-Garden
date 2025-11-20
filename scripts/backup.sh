#!/bin/bash
#
# Authelia Walled Garden - Backup Script
#
# This script creates a backup of your Authelia configuration and data.
# Run this regularly (e.g., via cron) to maintain backups.
#
# Usage:
#   ./scripts/backup.sh [backup-directory]
#
# Example:
#   ./scripts/backup.sh /backups/authelia
#
# What gets backed up:
#   - Authelia configuration (configuration.yml)
#   - User database (users_database.yml)
#   - Session database (db.sqlite3)
#   - Audit logs (if present)
#   - Docker Compose configuration
#   - Caddyfile
#
# What does NOT get backed up:
#   - Let's Encrypt certificates (Caddy will regenerate if needed)
#   - Docker volumes (backup separately with docker volume commands if needed)

set -e

# Default backup directory
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="authelia-walled-garden-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Deployment directory (where docker-compose.yml is located)
DEPLOY_DIR="/opt/authelia-stack"

echo "════════════════════════════════════════════════════════════════"
echo "  Authelia Walled Garden - Backup Script"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backup directory: ${BACKUP_PATH}"
echo "Source directory: ${DEPLOY_DIR}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# Check if deployment directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ ERROR: Deployment directory not found: $DEPLOY_DIR"
    echo "Please update DEPLOY_DIR variable in this script to match your deployment location"
    exit 1
fi

echo "✅ Backup directory created"
echo ""

# Backup Authelia configuration
echo "Backing up Authelia configuration..."
if [ -f "${DEPLOY_DIR}/authelia/configuration.yml" ]; then
    cp "${DEPLOY_DIR}/authelia/configuration.yml" "${BACKUP_PATH}/"
    echo "  ✅ configuration.yml"
else
    echo "  ⚠️  configuration.yml not found"
fi

# Backup user database
if [ -f "${DEPLOY_DIR}/authelia/users_database.yml" ]; then
    cp "${DEPLOY_DIR}/authelia/users_database.yml" "${BACKUP_PATH}/"
    echo "  ✅ users_database.yml"
else
    echo "  ⚠️  users_database.yml not found"
fi

# Backup session database
if [ -f "${DEPLOY_DIR}/authelia/db.sqlite3" ]; then
    cp "${DEPLOY_DIR}/authelia/db.sqlite3" "${BACKUP_PATH}/"
    echo "  ✅ db.sqlite3"
else
    echo "  ⚠️  db.sqlite3 not found"
fi

echo ""

# Backup audit logs (if present)
echo "Backing up audit logs..."
if [ -f "${DEPLOY_DIR}/logs/authelia-admin-audit.jsonl" ]; then
    mkdir -p "${BACKUP_PATH}/logs"
    cp "${DEPLOY_DIR}/logs/authelia-admin-audit.jsonl" "${BACKUP_PATH}/logs/"
    echo "  ✅ authelia-admin-audit.jsonl"
else
    echo "  ⚠️  Audit logs not found"
fi

echo ""

# Backup Docker Compose configuration
echo "Backing up Docker Compose configuration..."
if [ -f "${DEPLOY_DIR}/docker-compose.yml" ]; then
    cp "${DEPLOY_DIR}/docker-compose.yml" "${BACKUP_PATH}/"
    echo "  ✅ docker-compose.yml"
else
    echo "  ⚠️  docker-compose.yml not found"
fi

# Backup Caddyfile
if [ -f "${DEPLOY_DIR}/Caddyfile" ]; then
    cp "${DEPLOY_DIR}/Caddyfile" "${BACKUP_PATH}/"
    echo "  ✅ Caddyfile"
else
    echo "  ⚠️  Caddyfile not found"
fi

echo ""

# Create compressed archive
echo "Creating compressed archive..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"

BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)

echo "  ✅ ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  Backup Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Backup saved to: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "Backup size: ${BACKUP_SIZE}"
echo ""
echo "SECURITY REMINDER:"
echo "  - This backup contains sensitive data (passwords, secrets)"
echo "  - Encrypt the backup before storing long-term"
echo "  - Store backups in a secure location (not in git!)"
echo "  - Test restoration process regularly"
echo ""
echo "To restore from this backup:"
echo "  1. Extract: tar -xzf ${BACKUP_NAME}.tar.gz"
echo "  2. Copy files to deployment directory"
echo "  3. Restart services: docker compose restart"
echo ""
