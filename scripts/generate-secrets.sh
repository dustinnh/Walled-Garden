#!/bin/bash
#
# Authelia Walled Garden - Secret Generation Script
#
# This script generates all cryptographic secrets needed for deployment.
# Save the output securely and use it to populate your .env file.
#
# Usage:
#   ./scripts/generate-secrets.sh > secrets.txt
#   # Review secrets.txt and copy values to .env file
#   # Store secrets.txt in a secure location (password manager, encrypted backup)
#   # DO NOT commit secrets.txt to version control!

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  Authelia Walled Garden - Secret Generation"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "IMPORTANT: Save this output securely!"
echo "Do NOT commit these values to version control."
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if openssl is available
if ! command -v openssl &> /dev/null; then
    echo "ERROR: openssl is not installed or not in PATH"
    echo "Please install openssl and try again."
    exit 1
fi

# Authelia secrets (base64, 64 bytes)
echo "# Authelia Configuration Secrets"
echo "# Add these to examples/authelia-config.yml"
echo ""
echo "JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')"
echo "SESSION_SECRET=$(openssl rand -base64 64 | tr -d '\n')"
echo "STORAGE_ENCRYPTION_KEY=$(openssl rand -base64 64 | tr -d '\n')"
echo ""

# User Admin secrets (base64, 32 bytes)
echo "# User Admin (authelia-file-admin) Secrets"
echo "# Add these to examples/docker-compose.yml (user-admin service)"
echo ""
echo "SECRET_KEY=$(openssl rand -base64 32 | tr -d '\n')"
echo "AUDIT_HMAC_KEY=$(openssl rand -base64 32 | tr -d '\n')"
echo ""

# Nexterm secret (hex, 32 bytes)
echo "# Nexterm Secret (optional - only if deploying Nexterm)"
echo "# Add to examples/docker-compose.yml (nexterm service)"
echo ""
echo "NEXTERM_ENCRYPTION_KEY=$(openssl rand -hex 32)"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "  Generation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Copy examples/.env.template to examples/.env"
echo "  2. Replace placeholders in .env with the secrets above"
echo "  3. Replace 'example.com' with your actual domain in all configs"
echo "  4. Review examples/authelia-config.yml and update secrets"
echo "  5. Store this output securely (password manager or encrypted backup)"
echo ""
echo "SECURITY REMINDER:"
echo "  - Never commit .env file to version control"
echo "  - Never reuse secrets across environments"
echo "  - Rotate secrets periodically (e.g., every 90 days)"
echo ""
