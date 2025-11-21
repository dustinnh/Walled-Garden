# Development Workflow Guide

This guide explains how to safely develop, test, and deploy changes to your Authelia Walled Garden while keeping production stable.

## Overview

The recommended workflow uses:
- **Git repository** (`walledgarden-gh/`) as source of truth
- **Staging environment** for testing changes
- **Production environment** for live deployment
- **Deployment scripts** to automate the process

```
Development Flow:
  Edit in Git → Deploy to Staging → Test → Deploy to Production
```

---

## Environment Setup

### Three Environments

| Environment | Location | Purpose | Domain |
|-------------|----------|---------|--------|
| **Git Repository** | `/home/dust/projects/walledgarden/walledgarden-gh/` | Source of truth, version control | N/A (templates only) |
| **Staging** | `/opt/authelia-staging/` | Test changes before production | staging.example.com |
| **Production** | `/opt/authelia-stack/` | Live deployment | example.com |

### File Organization

```
Git Repository (walledgarden-gh/)
├── examples/              # Sanitized templates with placeholders
│   ├── docker-compose.yml    # Uses ${ENV_VARS}
│   ├── Caddyfile             # Uses example.com
│   ├── authelia-config.yml   # Uses REPLACE_WITH_*
│   └── .env.template         # Template for secrets
├── scripts/
│   ├── deploy-staging.sh     # Deploy to staging
│   ├── deploy-production.sh  # Deploy to production
│   └── generate-secrets.sh   # Generate secrets
└── docs/

Staging Environment (/opt/authelia-staging/)
├── docker-compose.yml     # From git (deployed)
├── Caddyfile              # From git (deployed)
├── .env                   # STAGING SECRETS (not in git)
├── authelia/
│   ├── configuration.yml  # From git (deployed)
│   └── users_database.yml # Test users (not in git)
└── dashboard/             # From git (deployed)

Production Environment (/opt/authelia-stack/)
├── docker-compose.yml     # From git (deployed)
├── Caddyfile              # From git (deployed)
├── .env                   # PRODUCTION SECRETS (not in git)
├── authelia/
│   ├── configuration.yml  # From git (deployed)
│   └── users_database.yml # Real users (not in git)
└── dashboard/             # From git (deployed)
```

---

## Initial Setup

### 1. Create Staging Environment

If you don't have a staging environment yet:

```bash
# Copy production to staging
sudo cp -r /opt/authelia-stack /opt/authelia-staging

# Fix ownership
sudo chown -R $(whoami):$(whoami) /opt/authelia-staging

# Generate staging secrets (DIFFERENT from production!)
cd /home/dust/projects/walledgarden/walledgarden-gh
./scripts/generate-secrets.sh > /opt/authelia-staging/.env

# Edit staging .env to add staging-specific values
nano /opt/authelia-staging/.env
# Update DOMAIN=staging.example.com, etc.

# Update Caddyfile for staging domain
nano /opt/authelia-staging/Caddyfile
# Replace example.com with staging.example.com

# Change ports to avoid conflict with production
nano /opt/authelia-staging/docker-compose.yml
# Change ports from "80:80" to "8080:80" and "443:443" to "8443:443"

# Start staging
cd /opt/authelia-staging
docker compose up -d
```

### 2. Configure DNS (Optional)

For proper staging testing:
- Add DNS record: `staging.example.com` → your server IP
- Or use `/etc/hosts` for local testing:
  ```bash
  echo "127.0.0.1 staging.example.com" | sudo tee -a /etc/hosts
  ```

### 3. Verify Deployment Scripts

```bash
cd /home/dust/projects/walledgarden/walledgarden-gh
ls -la scripts/deploy-*.sh

# Should show:
# -rwx--x--x deploy-staging.sh
# -rwx--x--x deploy-production.sh
```

---

## Daily Development Workflow

### Step 1: Make Changes in Git Repository

All development happens in the git repository:

```bash
cd /home/dust/projects/walledgarden/walledgarden-gh

# Edit configuration files
nano examples/docker-compose.yml
nano examples/Caddyfile
nano examples/authelia-config.yml

# Edit dashboard files
nano examples/dashboard/index.html

# Edit documentation
nano docs/HOWTO-ADD-SERVICES.md
```

### Step 2: Commit Changes to Git

```bash
# Stage changes
git add .

# Review what changed
git diff --staged

# Commit with descriptive message
git commit -m "Add new service: Jellyfin media server

- Add Jellyfin to docker-compose.yml
- Add Caddyfile route for /jellyfin/
- Update dashboard with Jellyfin card
- Document setup in HOWTO-ADD-SERVICES.md"

# Push to GitHub
git push
```

### Step 3: Deploy to Staging

```bash
# Deploy to staging for testing
./scripts/deploy-staging.sh

# The script will:
# 1. Ask for confirmation
# 2. Stop staging services
# 3. Copy configurations from git
# 4. Start staging services
```

### Step 4: Test in Staging

```bash
# Check logs
cd /opt/authelia-staging
docker compose logs -f

# Test in browser
# Visit: https://staging.example.com

# Run tests:
# - Can you log in?
# - Do all services load?
# - Is the new service working?
# - Check for errors in logs
```

### Step 5: Deploy to Production (When Ready)

**Only after staging tests pass!**

```bash
cd /home/dust/projects/walledgarden/walledgarden-gh

# Deploy to production
./scripts/deploy-production.sh

# The script will:
# 1. Verify git is clean
# 2. Confirm you tested in staging
# 3. Create backup
# 4. Stop production services (brief downtime)
# 5. Deploy new configurations
# 6. Start production services
```

### Step 6: Monitor Production

```bash
# Watch logs
cd /opt/authelia-stack
docker compose logs -f

# Test production URL
# Visit: https://example.com

# Verify all services work
# Check for errors
```

---

## Common Scenarios

### Scenario 1: Adding a New Service

**Example**: Add Jellyfin media server

```bash
# 1. Edit docker-compose.yml in git repo
cd /home/dust/projects/walledgarden/walledgarden-gh
nano examples/docker-compose.yml

# Add service:
services:
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    volumes:
      - jellyfin_data:/config
    networks:
      - internal

volumes:
  jellyfin_data:

# 2. Add Caddyfile route
nano examples/Caddyfile

# Add inside example.com block:
handle_path /jellyfin/* {
    reverse_proxy jellyfin:8096
}

# 3. Add dashboard card
nano examples/dashboard/index.html

# Add card in app-grid

# 4. Commit to git
git add .
git commit -m "Add Jellyfin media server"
git push

# 5. Test in staging
./scripts/deploy-staging.sh
# Test at https://staging.example.com/jellyfin/

# 6. Deploy to production
./scripts/deploy-production.sh
```

### Scenario 2: Updating Configuration

**Example**: Change Authelia session timeout

```bash
# 1. Edit in git repo
cd /home/dust/projects/walledgarden/walledgarden-gh
nano examples/authelia-config.yml

# Change:
session:
  expiration: 12h  # Changed from 8h
  inactivity: 4h   # Changed from 2h

# 2. Commit
git commit -am "Increase session timeout to 12 hours"
git push

# 3. Test in staging
./scripts/deploy-staging.sh
# Test login, wait for timeout, verify behavior

# 4. Deploy to production
./scripts/deploy-production.sh
```

### Scenario 3: Emergency Hotfix

**Example**: Production is broken, need immediate fix

```bash
# Option 1: Fix in git and deploy (recommended)
cd /home/dust/projects/walledgarden/walledgarden-gh
nano examples/Caddyfile  # Fix the issue
git commit -am "Fix: Correct Caddyfile syntax error"
git push
./scripts/deploy-production.sh

# Option 2: Direct production fix (NOT recommended, but faster)
cd /opt/authelia-stack
nano Caddyfile  # Fix the issue
docker compose restart caddy
# Then update git repo to match:
cd /home/dust/projects/walledgarden/walledgarden-gh
nano examples/Caddyfile  # Apply same fix
git commit -am "Fix: Correct Caddyfile syntax error"
git push
```

### Scenario 4: Testing New Feature Without Staging

**If you can't run staging environment:**

```bash
# Use docker compose config to test syntax
cd /home/dust/projects/walledgarden/walledgarden-gh/examples
docker compose config  # Validates YAML syntax

# For Authelia config:
../scripts/check-config.sh

# Then deploy to production with extra caution
cd ..
./scripts/deploy-production.sh
# Monitor closely!
```

---

## Secrets Management

### How Secrets Work

**Three separate .env files** (none in git):

1. **Git repository** - `.env.template` (placeholder examples only)
2. **Staging** - `/opt/authelia-staging/.env` (staging secrets)
3. **Production** - `/opt/authelia-stack/.env` (production secrets)

### Generating Secrets

```bash
# Generate new secrets
cd /home/dust/projects/walledgarden/walledgarden-gh
./scripts/generate-secrets.sh

# Save output
./scripts/generate-secrets.sh > secrets-$(date +%Y%m%d).txt

# Copy relevant sections to each environment's .env file
```

### .env File Structure

```bash
# /opt/authelia-stack/.env (PRODUCTION)
JWT_SECRET=<production-secret-here>
SESSION_SECRET=<production-secret-here>
STORAGE_ENCRYPTION_KEY=<production-secret-here>
SECRET_KEY=<production-secret-here>
AUDIT_HMAC_KEY=<production-secret-here>
NEXTERM_ENCRYPTION_KEY=<production-secret-here>
DOMAIN=example.com

# /opt/authelia-staging/.env (STAGING)
JWT_SECRET=<different-staging-secret>
SESSION_SECRET=<different-staging-secret>
STORAGE_ENCRYPTION_KEY=<different-staging-secret>
SECRET_KEY=<different-staging-secret>
AUDIT_HMAC_KEY=<different-staging-secret>
NEXTERM_ENCRYPTION_KEY=<different-staging-secret>
DOMAIN=staging.example.com
```

**Important**:
- ✅ Production and staging use DIFFERENT secrets
- ✅ Secrets are environment-specific
- ❌ Never commit .env files to git
- ❌ Never use template values in production

---

## Troubleshooting

### Deployment Script Fails

**Check**:
```bash
# 1. Verify paths are correct
ls -la /home/dust/projects/walledgarden/walledgarden-gh/examples/
ls -la /opt/authelia-stack/

# 2. Check file permissions
ls -la /opt/authelia-stack/docker-compose.yml

# 3. Review script output for specific error
./scripts/deploy-staging.sh 2>&1 | tee deploy-error.log
```

### Services Won't Start After Deployment

**Check**:
```bash
# 1. View logs
cd /opt/authelia-stack  # or /opt/authelia-staging
docker compose logs -f

# 2. Check for common issues:
# - Missing .env file
# - Syntax errors in configs
# - Port conflicts
# - Volume mount issues

# 3. Validate configuration
docker compose config

# 4. Check individual service
docker compose logs authelia
docker compose logs caddy
```

### Need to Rollback

**From backup**:
```bash
# 1. Find latest backup
ls -lh /backups/authelia/

# 2. Stop current services
cd /opt/authelia-stack
docker compose down

# 3. Restore from backup
cd /backups/authelia
tar -xzf authelia-walled-garden-YYYYMMDD-HHMMSS.tar.gz
cp -r authelia-walled-garden-YYYYMMDD-HHMMSS/* /opt/authelia-stack/

# 4. Restart services
cd /opt/authelia-stack
docker compose up -d
```

**From git history**:
```bash
# 1. Find previous working commit
cd /home/dust/projects/walledgarden/walledgarden-gh
git log --oneline

# 2. Revert to previous commit
git revert <commit-hash>

# 3. Deploy the reverted version
./scripts/deploy-production.sh
```

---

## Best Practices

### Development

✅ **DO**:
- Always work in the git repository
- Commit frequently with descriptive messages
- Test in staging before production
- Review changes before deploying
- Keep secrets out of git

❌ **DON'T**:
- Edit files directly in production
- Skip staging tests
- Commit secrets to git
- Deploy untested changes
- Forget to backup before production deployment

### Deployment

✅ **DO**:
- Use deployment scripts
- Create backups before production deployment
- Monitor logs after deployment
- Test thoroughly in staging
- Document changes in commit messages

❌ **DON'T**:
- Deploy directly to production
- Skip confirmation prompts
- Ignore failed services
- Deploy with uncommitted changes
- Rush deployments

### Secrets

✅ **DO**:
- Generate unique secrets per environment
- Store secrets in .env files
- Keep .env files out of git
- Rotate secrets periodically
- Backup secrets securely

❌ **DON'T**:
- Reuse secrets across environments
- Commit secrets to git
- Use template/example secrets in production
- Share secrets in plain text
- Lose access to production secrets

---

## Quick Reference

### Common Commands

```bash
# Development workflow
cd /home/dust/projects/walledgarden/walledgarden-gh
git pull                              # Get latest from GitHub
# ... make changes ...
git add .
git commit -m "Description"
git push
./scripts/deploy-staging.sh          # Test in staging
./scripts/deploy-production.sh       # Deploy to production

# Check status
cd /opt/authelia-stack
docker compose ps                     # Service status
docker compose logs -f                # Watch logs
docker compose logs <service>         # Specific service logs

# Staging commands
cd /opt/authelia-staging
docker compose ps
docker compose logs -f

# Generate secrets
cd /home/dust/projects/walledgarden/walledgarden-gh
./scripts/generate-secrets.sh

# Validate configuration
./scripts/check-config.sh

# Create backup
./scripts/backup.sh /backups/authelia
```

### Directory Quick Reference

```bash
# Git repository (source of truth)
/home/dust/projects/walledgarden/walledgarden-gh/

# Staging environment
/opt/authelia-staging/

# Production environment
/opt/authelia-stack/

# Backups
/backups/authelia/
```

---

## Updating the Admin Panel

The Authelia Admin Panel runs as a **pre-built Docker image** (`dutdok4/authelia-admin:latest`) and doesn't require separate source code.

### When New Admin Panel Versions Are Released

**Updating to latest version**:
```bash
# Pull new image
cd /opt/authelia-stack
docker compose pull user-admin

# Restart service
docker compose up -d user-admin
```

**Pinning to specific version** (recommended for production):
```yaml
# In docker-compose.yml
user-admin:
  image: dutdok4/authelia-admin:1.10.0  # Pin to specific version
```

### For Maintainers: Building New Images

If you need to build and publish a new version (maintainers only):

```bash
# Build from Admin Panel source
cd /home/dust/projects/authelia-admin/authelia-file-admin
docker build -t dutdok4/authelia-admin:1.11.0 -t dutdok4/authelia-admin:latest .

# Push to Docker Hub
docker push dutdok4/authelia-admin:1.11.0
docker push dutdok4/authelia-admin:latest

# Update git repo
cd /home/dust/projects/walledgarden/walledgarden-gh
# Update version in README.md and commit
```

---

## Summary

**Recommended Workflow**:
1. Edit in git repository (`walledgarden-gh/`)
2. Commit and push to GitHub
3. Deploy to staging with `deploy-staging.sh`
4. Test thoroughly in staging
5. Deploy to production with `deploy-production.sh`
6. Monitor production logs

**Key Principles**:
- Git is the source of truth
- Always test before production
- Secrets stay out of git
- Automate with scripts
- Backup before production changes

For questions or issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open a GitHub issue.
