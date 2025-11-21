# Nexterm Installation Documentation

**Date:** 2025-11-18
**Application:** Nexterm v1.0.4-OPEN-PREVIEW
**Purpose:** Server management software for SSH, VNC & RDP connections

## Overview

Nexterm has been successfully added to the NYC App House walled garden setup. It provides a web-based interface for managing remote server connections via SSH, VNC, and RDP protocols.

## Installation Steps Performed

### 1. Research and Configuration Preparation

**Docker Image:** `germannewsmaker/nexterm:latest`
**Port:** 6989 (internal only, no published ports)
**Subdomain:** nexterm.example.com

Generated encryption key for secure password storage:
```bash
openssl rand -hex 32
# Example output: REPLACE_WITH_YOUR_GENERATED_ENCRYPTION_KEY
```

### 2. Docker Compose Configuration

Added Nexterm service to `/opt/authelia-stack/docker-compose.yml`:

```yaml
nexterm:
  image: germannewsmaker/nexterm:latest
  container_name: nexterm
  restart: unless-stopped
  environment:
    - ENCRYPTION_KEY=${NEXTERM_ENCRYPTION_KEY}  # Generate with: openssl rand -hex 32
  volumes:
    - nexterm_data:/app/data
  networks:
    - internal
```

Added corresponding volume:
```yaml
volumes:
  nexterm_data:
```

**Key Configuration Details:**
- Uses internal Docker network only (no direct external access)
- Persistent data storage in Docker volume `nexterm_data` at `/app/data`
- Encryption key secures stored passwords, SSH keys, and passphrases

### 3. Reverse Proxy Configuration (Caddy)

Added subdomain routing to `/opt/authelia-stack/Caddyfile`:

```caddyfile
# Nexterm server management
nexterm.example.com {
    encode gzip

    forward_auth authelia:9091 {
        uri /api/verify?rd=https://example.com/auth/
        copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    }

    reverse_proxy nexterm:6989 {
        transport http {
            compression off
        }
    }
}
```

**Configuration Notes:**
- Uses subdomain routing (not path-based) due to Nexterm's lack of base path support
- Compression disabled to support WebSocket connections properly
- Forward authentication to Authelia for SSO

### 4. Authelia Access Control

Updated `/opt/authelia-stack/authelia/configuration.yml` to allow access:

```yaml
access_control:
  default_policy: deny
  rules:
    - domain:
        - "example.com"
        - "excalidraw.example.com"
        - "storage.example.com"
        - "collab.example.com"
        - "nexterm.example.com"  # Added
      policy: one_factor
```

**Security Note:** This was the critical step - without adding nexterm.example.com to the access control rules, all requests were returning 403 Forbidden errors.

### 5. DNS Configuration

Added DNS A record:
```
Type: A
Host: nexterm
Domain: example.com
Value: YOUR_SERVER_IP
```

### 6. Dashboard Integration

Updated `/opt/authelia-stack/dashboard/index.html` to add Nexterm tile:

```html
<li class="app-card">
  <span class="app-icon">🖥️</span>
  <a href="https://nexterm.example.com">Nexterm</a>
  <p class="app-description">Server management via SSH, VNC & RDP</p>
</li>
```

### 7. SSL Certificate

Caddy automatically obtained SSL certificate from Let's Encrypt after DNS propagation.

**Certificate Details:**
- Issuer: Let's Encrypt (ACME v02)
- Domain: nexterm.example.com
- Status: Valid

### 8. Service Deployment

Deployment commands:
```bash
cd /opt/authelia-stack
docker compose pull nexterm
docker compose up -d nexterm
docker compose restart authelia caddy
```

## Troubleshooting Steps Performed

### Issue 1: Path-Based Routing (Failed Approach)

**Problem:** Initial attempt used path-based routing `/nexterm/*`
**Error:** `Failed to load module script: Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of "text/html"`

**Root Cause:** Nexterm is a single-page application that loads assets from absolute paths (e.g., `/assets/index.js`). These paths don't match the `/nexterm/*` pattern, causing Caddy to return the dashboard's index.html instead of proxying to Nexterm.

**Resolution:** Switched to subdomain-based routing (nexterm.example.com)

### Issue 2: SSL Certificate Acquisition Failed

**Problem:** `ERR_SSL_PROTOCOL_ERROR` - Certificate acquisition failed
**Error in logs:** `DNS problem: NXDOMAIN looking up A for nexterm.example.com`

**Root Cause:** Caddy attempted certificate acquisition before DNS had fully propagated to Let's Encrypt's servers.

**Resolution:** Restarted Caddy after DNS propagation completed (~5 minutes)

### Issue 3: 403 Forbidden Errors

**Problem:** All requests to nexterm.example.com returned 403 Forbidden
**Error in Authelia logs:** `Access to 'https://nexterm.example.com/' is forbidden to user '[username]'`

**Root Cause:** nexterm.example.com was not included in Authelia's access control rules, causing the default deny policy to block all requests.

**Resolution:** Added nexterm.example.com to the allowed domains in Authelia configuration

## Initial Setup Instructions

### First-Time Access

1. **Authenticate with Authelia:**
   - Visit https://example.com
   - Login with Authelia credentials

2. **Access Nexterm:**
   - Click the Nexterm tile on the dashboard
   - Or visit https://nexterm.example.com directly

3. **Language Selection:**
   - Select "English" when prompted

4. **Create First User:**
   - Username: [your_username]
   - Password: [your_password]
   - First user is automatically assigned administrator role

### Authentication Model

**Double Authentication:** Users must authenticate with both Authelia and Nexterm
- **Layer 1:** Authelia SSO (protects access to the application)
- **Layer 2:** Nexterm built-in authentication (application-level access control)

This provides defense in depth with separate authentication boundaries.

## Technical Details

### Network Architecture

- **External Access:** Port 80/443 on Caddy only
- **Internal Network:** All services communicate via Docker bridge network `internal`
- **No Direct Access:** Nexterm container has no published ports, accessible only through Caddy

### Data Persistence

**Volume:** `authelia-stack_nexterm_data`
**Mount Point:** `/app/data` inside container
**Contents:**
- SQLite database (accounts, servers, sessions, etc.)
- Server connection configurations
- Encrypted credentials

### Environment Variables

- `ENCRYPTION_KEY`: 64-character hex string for encrypting sensitive data (passwords, SSH keys, passphrases)

### Database Migrations

On first startup, Nexterm automatically ran 9 database migrations:
1. Initial database setup (accounts, organizations, identities, servers, etc.)
2. Add organization ID
3. Migrate old data
4. Encrypt data
5. Make first user admin
6. Update organization members primary key
7. Remove owner ID from organizations
8. Add internal auth provider
9. Add node name to PVE servers

## Security Considerations

### Network Isolation
- Backend application on isolated Docker network
- No direct external access to container
- All traffic proxied through Caddy with Authelia authentication

### Encryption
- Sensitive data encrypted at rest using ENCRYPTION_KEY
- SSL/TLS encryption in transit via Let's Encrypt certificates
- Built-in support for 2FA (can be enabled per-user in Nexterm)

### Access Control
- Authelia SSO provides first authentication layer
- Nexterm manages its own user accounts and permissions
- Session management with configurable expiration

### Secrets Management

**Critical Secrets:**
- ENCRYPTION_KEY: Never commit to version control
- Authelia session/JWT secrets
- User password hashes

## Maintenance

### Container Logs
```bash
cd /opt/authelia-stack
docker compose logs -f nexterm
```

### Restart Service
```bash
docker compose restart nexterm
```

### Update to Latest Version
```bash
docker compose pull nexterm
docker compose up -d nexterm
```

### Backup Data
```bash
# Backup Nexterm data volume
docker run --rm -v authelia-stack_nexterm_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/nexterm-backup-$(date +%Y%m%d).tar.gz /data
```

## Integration Points

### With Authelia
- Forward authentication for all requests
- User context headers passed to application (Remote-User, Remote-Groups, Remote-Name, Remote-Email)

### With Caddy
- Automatic SSL certificate management
- HTTP/2 support
- WebSocket support (compression disabled)

### With Dashboard
- Tile-based launcher integration
- Consistent UI/UX with other applications

## References

- **GitHub:** https://github.com/gnmyt/Nexterm
- **Docker Hub:** https://hub.docker.com/r/germannewsmaker/nexterm
- **Documentation:** https://docs.nexterm.dev
- **Version:** 1.0.4-OPEN-PREVIEW
- **Node.js Version:** v22.17.0

## Files Modified

1. `/opt/authelia-stack/docker-compose.yml` - Added nexterm service and volume
2. `/opt/authelia-stack/Caddyfile` - Added subdomain routing
3. `/opt/authelia-stack/authelia/configuration.yml` - Added access control rule
4. `/opt/authelia-stack/dashboard/index.html` - Added dashboard tile

## Deployment Verification

✅ Container running: `docker compose ps nexterm`
✅ SSL certificate valid: https://nexterm.example.com
✅ Authelia authentication: Access control configured
✅ Database initialized: 9 migrations completed
✅ Dashboard integration: Tile visible at https://example.com
✅ DNS resolution: nexterm.example.com → YOUR_SERVER_IP

## Post-Installation Notes

- Language preference stored in browser local storage
- First user created automatically becomes administrator
- Supports SSH, VNC, and RDP connections
- Built-in file management via SFTP
- Docker deployment support
- Proxmox container management support
- AI assistant features available (configurable)
