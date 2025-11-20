#!/bin/bash
#
# Authelia Walled Garden - Configuration Validation Script
#
# This script validates your Authelia configuration before deployment.
# It checks for common misconfigurations and security issues.
#
# Usage:
#   ./scripts/check-config.sh
#
# Requirements:
#   - Docker installed and running
#   - authelia-config.yml must exist in examples/ directory

set -e

CONFIG_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../examples" && pwd)/authelia-config.yml"

echo "════════════════════════════════════════════════════════════════"
echo "  Authelia Configuration Validator"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if config file exists
if [ ! -f "$CONFIG_PATH" ]; then
    echo "❌ ERROR: Configuration file not found at: $CONFIG_PATH"
    echo ""
    echo "Please ensure authelia-config.yml exists in the examples/ directory"
    exit 1
fi

echo "✅ Configuration file found: $CONFIG_PATH"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ ERROR: Docker is not installed or not in PATH"
    echo "Please install Docker and try again."
    exit 1
fi

echo "✅ Docker is available"
echo ""

# Check for placeholder secrets
echo "Checking for placeholder secrets..."
if grep -q "REPLACE_WITH" "$CONFIG_PATH"; then
    echo "⚠️  WARNING: Found placeholder secrets in configuration"
    echo "Please replace all REPLACE_WITH_YOUR_* placeholders with actual secrets"
    echo ""
    echo "Generate secrets with: ./scripts/generate-secrets.sh"
    echo ""
else
    echo "✅ No placeholder secrets found"
    echo ""
fi

# Check for example.com domain
echo "Checking for example.com domain..."
if grep -q "example.com" "$CONFIG_PATH"; then
    echo "⚠️  WARNING: Found 'example.com' in configuration"
    echo "Please replace all instances of example.com with your actual domain"
    echo ""
else
    echo "✅ No example.com references found"
    echo ""
fi

# Validate Authelia configuration using Docker
echo "Validating Authelia configuration syntax..."
echo ""

if docker run --rm -v "$CONFIG_PATH:/config/configuration.yml:ro" \
    authelia/authelia:latest \
    authelia validate-config /config/configuration.yml; then
    echo ""
    echo "✅ Authelia configuration is valid!"
    echo ""
else
    echo ""
    echo "❌ Authelia configuration validation failed"
    echo "Please review the errors above and fix your configuration"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "  Validation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Ensure all secrets are replaced (not REPLACE_WITH placeholders)"
echo "  2. Replace example.com with your actual domain"
echo "  3. Review access control rules in authelia-config.yml"
echo "  4. Test deployment: docker compose up -d"
echo ""
