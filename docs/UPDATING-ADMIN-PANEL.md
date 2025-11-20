# Updating the Authelia Admin Panel Docker Image

**For Maintainers Only** - This guide explains how to build and publish new versions of the Authelia Admin Panel Docker image.

## Overview

The Walled Garden uses a **pre-built Docker image** (`dutdok4/authelia-admin`) for the user management interface. This eliminates the need for users to clone multiple repositories and simplifies deployment.

**Docker Hub Repository**: https://hub.docker.com/r/dutdok4/authelia-admin
**Source Code**: https://github.com/dustinnh/Authelia-Admin-Panel
**Current Version**: 1.10.0

## When to Build a New Image

Build and publish a new image when:
- New Admin Panel version is released
- Security patches are applied
- Bug fixes are merged
- New features are added to the Admin Panel

## Building and Publishing Process

### Step 1: Update Admin Panel Source Code

```bash
# Navigate to Admin Panel repository
cd /home/dust/projects/authelia-admin/authelia-file-admin

# Pull latest changes (if working with git)
git pull

# Or make your changes directly
nano src/app.py
nano src/admin.html

# Test locally (optional but recommended)
docker build -t authelia-admin:test .
docker run -p 5000:5000 authelia-admin:test
# Visit http://localhost:5000 to verify
```

### Step 2: Update Version Number

Update the version in the Admin Panel's documentation:

```bash
# Update CHANGELOG.md
nano CHANGELOG.md
# Add new version entry

# Update README.md if needed
nano README.md
# Update version badge if present
```

### Step 3: Build Docker Image

Build with both version tag and latest tag:

```bash
cd /home/dust/projects/authelia-admin/authelia-file-admin

# Replace 1.11.0 with actual new version
docker build -t dutdok4/authelia-admin:1.11.0 -t dutdok4/authelia-admin:latest .
```

**Tag naming convention**:
- `dutdok4/authelia-admin:latest` - Always points to the newest version
- `dutdok4/authelia-admin:1.11.0` - Specific version (allows pinning)

### Step 4: Test the Image

Before pushing to Docker Hub, test the image locally:

```bash
# Run the container
docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=test-key \
  -e AUDIT_HMAC_KEY=test-hmac \
  --name test-admin \
  dutdok4/authelia-admin:1.11.0

# Test the web interface
curl http://localhost:5000/health
# Should return: {"status": "healthy", "version": "1.11.0", ...}

# View logs
docker logs test-admin

# Clean up
docker stop test-admin
docker rm test-admin
```

### Step 5: Push to Docker Hub

Login to Docker Hub (if not already logged in):

```bash
# Login with credentials
echo 'YOUR_PASSWORD' | docker login -u dutdok4 --password-stdin

# Or interactive login
docker login
# Username: dutdok4
# Password: [your password]
```

Push both tags:

```bash
# Push versioned tag
docker push dutdok4/authelia-admin:1.11.0

# Push latest tag
docker push dutdok4/authelia-admin:latest
```

### Step 6: Update Walled Garden Documentation

Update references in the Walled Garden repository:

```bash
cd /home/dust/projects/walledgarden/walledgarden-gh

# Update README.md if version is mentioned
nano README.md
# Update version numbers in code examples

# Update this document
nano docs/UPDATING-ADMIN-PANEL.md
# Update "Current Version" at top

# Commit changes
git add .
git commit -m "Update Admin Panel image to version 1.11.0"
git push
```

### Step 7: Notify Users (Optional)

For significant updates:
- Create a GitHub release in the Walled Garden repo
- Update the README.md with a "What's New" section
- Post in discussions or relevant communities

## Version Pinning Recommendations

**For users of the Walled Garden**:

**Development/Testing**:
```yaml
user-admin:
  image: dutdok4/authelia-admin:latest  # Auto-update to newest
```

**Production**:
```yaml
user-admin:
  image: dutdok4/authelia-admin:1.10.0  # Pin to specific version
```

**Why pin in production?**
- Prevents unexpected breaking changes
- Allows controlled testing before upgrade
- Ensures reproducible deployments

## Troubleshooting

### Build Fails

**Issue**: Docker build fails with error

**Solutions**:
```bash
# Check Dockerfile syntax
cd /home/dust/projects/authelia-admin/authelia-file-admin
cat Dockerfile

# Verify requirements.txt dependencies
cat requirements.txt

# Try building with no cache
docker build --no-cache -t dutdok4/authelia-admin:test .
```

### Push Access Denied

**Issue**: `push access denied, repository does not exist or may require authorization`

**Solutions**:
```bash
# Verify you're logged in
docker logout
docker login -u dutdok4

# Check repository exists on Docker Hub
# Visit: https://hub.docker.com/r/dutdok4/authelia-admin

# If repository doesn't exist, create it at:
# https://hub.docker.com/repository/create
```

### Image Too Large

**Issue**: Image size is unexpectedly large

**Solutions**:
```bash
# Check image size
docker images dutdok4/authelia-admin

# Use multi-stage builds in Dockerfile
# Use python:3.11-slim instead of python:3.11
# Remove unnecessary files in .dockerignore

# Example .dockerignore:
*.pyc
__pycache__
.git
.gitignore
README.md
docs/
tests/
```

## Docker Hub Credentials

**Username**: dutdok4
**Email**: dustin8ai@gmail.com
**Password**: [Stored securely - do not commit to git]

**Security Note**: Never commit Docker Hub credentials to git. Store in a password manager.

## Automation (Future Enhancement)

Consider setting up automated builds using GitHub Actions:

```yaml
# .github/workflows/docker-publish.yml
name: Build and Push Docker Image

on:
  release:
    types: [published]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: |
            dutdok4/authelia-admin:latest
            dutdok4/authelia-admin:${{ github.event.release.tag_name }}
```

## Quick Reference

**Build new version**:
```bash
cd /home/dust/projects/authelia-admin/authelia-file-admin
docker build -t dutdok4/authelia-admin:1.11.0 -t dutdok4/authelia-admin:latest .
docker push dutdok4/authelia-admin:1.11.0
docker push dutdok4/authelia-admin:latest
```

**Update Walled Garden docs**:
```bash
cd /home/dust/projects/walledgarden/walledgarden-gh
nano README.md docs/UPDATING-ADMIN-PANEL.md
git commit -am "Update Admin Panel to 1.11.0"
git push
```

**Users update their deployment**:
```bash
docker compose pull user-admin
docker compose up -d user-admin
```

---

**Last Updated**: 2024-11-19
**Current Image Version**: 1.10.0
**Maintainer**: Dustin @ NYC App House
