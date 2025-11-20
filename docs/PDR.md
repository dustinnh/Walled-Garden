# Project Design Record: Authelia-Based Walled Garden Implementation

## Document Control

| Attribute | Value |
|-----------|-------|
| **Document ID** | PDR-AUTH-001 |
| **Version** | 1.0 |
| **Status** | Draft |
| **Date** | November 17, 2025 |
| **Author(s)** | System Architecture Team |
| **Target Audience** | System Administrators, Web Developers |
| **Classification** | Internal Technical Documentation |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-17 | System Architecture | Initial PDR creation |

---

## 1. Executive Summary

### 1.1 Purpose
This PDR documents the design and implementation of a secure, authenticated "walled garden" web application platform using Authelia as the authentication gateway, Caddy as the reverse proxy, and Docker for container orchestration.

### 1.2 Scope
The system will provide:
- Single sign-on (SSO) authentication for multiple internal web applications
- Centralized access control and session management
- Automatic SSL/TLS certificate provisioning via Let's Encrypt
- Unified dashboard interface for application access
- Scalable architecture for future application additions

### 1.3 Key Stakeholders
- **System Administrators**: Responsible for deployment, configuration, and maintenance
- **Web Developers**: Responsible for application integration and dashboard customization
- **End Users**: Internal staff requiring authenticated access to web applications

### 1.4 Success Criteria
- All web applications accessible through single authentication point
- SSL/TLS certificates automatically provisioned and renewed
- User sessions persist across multiple applications
- Zero external port exposure for backend applications
- Deployment completed within 2 hours from clean VPS state

---

## 2. System Overview

### 2.1 Architecture Summary
The system implements a reverse proxy pattern with integrated authentication middleware. All external requests enter through Caddy, which forwards authentication checks to Authelia before proxying to backend services.

### 2.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Reverse Proxy | Caddy | latest | Public entry point, SSL/TLS, routing |
| Authentication Gateway | Authelia | latest | SSO, 2FA, access control |
| Container Orchestration | Docker Compose | 3.9+ | Service management |
| Backend Applications | Various | N/A | Excalidraw, Nextcloud, etc. |
| Operating System | Ubuntu Server | 24.04 LTS | Host platform |

### 2.3 Network Architecture

```
Internet
    |
    | (ports 80/443)
    v
[Caddy Reverse Proxy]
    |
    |-- Forward Auth --> [Authelia]
    |
    |-- Proxied Requests
    |
    +-- Dashboard (static HTML)
    +-- /excalidraw/ --> [Excalidraw Container]
    +-- /cloud/ --> [Nextcloud Container]
    +-- [Future Applications]

All containers on isolated Docker network "internal"
No direct external access to backend services
```

### 2.4 Design Principles
1. **Security First**: No backend services exposed directly to internet
2. **Zero Trust**: All requests authenticated before reaching applications
3. **Simplicity**: Minimal configuration complexity
4. **Maintainability**: Standard tools, clear separation of concerns
5. **Scalability**: Easy addition of new services
6. **Observability**: Clear logging and error reporting

---

## 3. System Requirements

### 3.1 Infrastructure Requirements

#### Hardware (VPS Specifications)
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 40GB minimum (depends on application data)
- **Network**: 100Mbps+ connection with static IP

#### Software Prerequisites
- Ubuntu Server 24.04 LTS (or compatible Linux distribution)
- Docker Engine 24.0+
- Docker Compose 2.20+
- UFW firewall (or equivalent)
- Root/sudo access for initial setup

### 3.2 Domain Requirements
- Valid domain name (example: run.nycapphouse.com)
- DNS access for A/AAAA record configuration
- Email address for ACME certificate registration

### 3.3 Security Requirements
- SSH key-based authentication (password auth disabled)
- Firewall rules limiting access to ports 22, 80, 443
- Regular security updates via unattended-upgrades
- Backup strategy for configuration and application data
- Password policy: Argon2id hashing with specified parameters

### 3.4 Functional Requirements

#### FR-001: Authentication
- System shall provide web-based login interface
- System shall support username/password authentication
- System shall optionally support TOTP-based 2FA
- System shall maintain session state across applications
- System shall redirect unauthenticated users to login page

#### FR-002: Authorization
- System shall enforce access control policies per application
- System shall support user groups and role-based access
- System shall provide configurable policy enforcement (one_factor/two_factor)

#### FR-003: Application Access
- System shall provide unified dashboard listing available applications
- System shall proxy requests to backend applications transparently
- System shall preserve user context across proxied requests
- System shall support path-based routing (/excalidraw, /cloud)

#### FR-004: SSL/TLS Management
- System shall automatically obtain SSL/TLS certificates via ACME protocol
- System shall renew certificates before expiration
- System shall enforce HTTPS for all connections
- System shall redirect HTTP to HTTPS automatically

### 3.5 Non-Functional Requirements

#### NFR-001: Performance
- Authentication check latency: < 50ms
- Page load time (excluding app rendering): < 2s
- Support for 100+ concurrent authenticated sessions

#### NFR-002: Availability
- Target uptime: 99.5% (excluding maintenance windows)
- Graceful degradation if authentication service unavailable
- Automatic container restart on failure

#### NFR-003: Maintainability
- Configuration changes via text files (no database required)
- One-command deployment and updates
- Clear error messages and logging
- Self-documenting configuration files

---

## 4. Detailed Design

### 4.1 Directory Structure

The deployment uses the following filesystem layout:

```
/opt/authelia-stack/          # Base deployment directory
├── docker-compose.yml         # Service orchestration configuration
├── Caddyfile                  # Reverse proxy routing and SSL config
├── dashboard/                 # Static web dashboard
│   └── index.html            # Application listing page
├── authelia/                  # Authentication service configuration
│   ├── configuration.yml      # Main Authelia config
│   ├── users_database.yml     # User accounts and hashes
│   └── notification.log       # File-based notification log
└── volumes/                   # Docker named volume data (auto-created)
    ├── caddy_data/            # Caddy SSL certificates and data
    └── caddy_config/          # Caddy runtime configuration
```

### 4.2 Service Definitions

#### 4.2.1 Caddy Service
**Purpose**: Public-facing reverse proxy and SSL termination

**Container Configuration**:
```yaml
caddy:
  image: caddy:latest
  container_name: caddy
  restart: unless-stopped
  ports:
    - "80:80"      # HTTP (redirects to HTTPS)
    - "443:443"    # HTTPS
  volumes:
    - ./Caddyfile:/etc/caddy/Caddyfile:ro
    - ./dashboard:/srv
    - caddy_data:/data
    - caddy_config:/config
  networks:
    - internal
```

**Key Features**:
- Automatic Let's Encrypt certificate issuance
- HTTP/2 and HTTP/3 support
- Gzip compression
- Forward authentication to Authelia

#### 4.2.2 Authelia Service
**Purpose**: Authentication gateway and session management

**Container Configuration**:
```yaml
authelia:
  image: authelia/authelia:latest
  container_name: authelia
  restart: unless-stopped
  volumes:
    - ./authelia:/config
  environment:
    - TZ=America/New_York
  networks:
    - internal
```

**Key Features**:
- File-based user storage (initial deployment)
- Argon2id password hashing
- Optional TOTP 2FA support
- Policy-based access control
- Session management with configurable timeout

#### 4.2.3 Backend Application Services
**Purpose**: Host actual web applications

**Example Configuration** (Excalidraw):
```yaml
excalidraw:
  image: excalidraw/excalidraw:latest
  container_name: excalidraw
  restart: unless-stopped
  networks:
    - internal
```

**Security Characteristics**:
- No published ports (not accessible from internet)
- Only accessible via internal Docker network
- Communication with Caddy only
- Isolated from other containers except via defined routes

### 4.3 Routing Configuration

#### 4.3.1 Caddy Forward Authentication Pattern

The Caddyfile implements forward authentication using Authelia's verification endpoint:

```caddyfile
run.nycapphouse.com {
    encode gzip
    tls email@example.com

    route {
        # Forward auth to Authelia
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }

        # Dashboard at root
        handle_path / {
            root * /srv
            file_server
        }

        # Application routes
        handle_path /excalidraw/* {
            reverse_proxy excalidraw:80
        }

        handle_path /cloud/* {
            reverse_proxy nextcloud:80
        }
    }
}
```

**Authentication Flow**:
1. Request arrives at Caddy
2. Caddy sends authentication check to Authelia at `/api/verify`
3. If authenticated: Authelia returns 200, request proceeds to backend
4. If not authenticated: Authelia returns 302 redirect to login page
5. After successful login: User redirected back to original URL

### 4.4 Authentication Configuration

#### 4.4.1 Authelia Core Settings

**File**: `authelia/configuration.yml`

**Critical Parameters**:
```yaml
host: 0.0.0.0
port: 9091

jwt:
  secret: "<REPLACE_WITH_RANDOM_64_CHAR_STRING>"

default_redirection_url: https://run.nycapphouse.com

authentication_backend:
  file:
    path: /config/users_database.yml
    password:
      algorithm: argon2id
      iterations: 3
      key_length: 32
      salt_length: 16
      memory: 65536      # 64 MB
      parallelism: 4

session:
  name: authelia_session
  secret: "<REPLACE_WITH_RANDOM_64_CHAR_STRING>"
  inactivity: 3600      # 1 hour
  expiration: 7200      # 2 hours
  domain: nycapphouse.com  # Parent domain for session cookie
  same_site: lax

totp:
  issuer: nycapphouse.com
  period: 30
  skew: 1

access_control:
  default_policy: deny
  rules:
    - domain: "run.nycapphouse.com"
      policy: one_factor  # Change to two_factor for TOTP requirement

notifier:
  filesystem:
    filename: /config/notification.log
```

**Security Notes**:
- JWT and session secrets MUST be unique random strings
- Never commit secrets to version control
- Use `openssl rand -base64 64` to generate secrets
- Parent domain setting allows session sharing across subdomains

#### 4.4.2 User Database

**File**: `authelia/users_database.yml`

**Structure**:
```yaml
users:
  username:
    displayname: "Full Name"
    password: "$argon2id$v=19$m=65536,t=3,p=4$<base64_salt>$<base64_hash>"
    email: "user@example.com"
    groups:
      - admins
      - users
```

**Password Hash Generation**:
```bash
docker run --rm -it authelia/authelia:latest authelia hash-password 'PlainTextPassword'
```

**Output Example**:
```
Password hash: $argon2id$v=19$m=65536,t=3,p=4$RGFuZ2Vyb3VzCg$YXNzd29yZA
```

Copy the entire hash string into the `password:` field.

### 4.5 Dashboard Implementation

#### 4.5.1 Dashboard HTML

**File**: `dashboard/index.html`

**Purpose**: Provide user-friendly application launcher after authentication

**Features**:
- Clean, responsive design
- System-native font stack
- Minimal dependencies (no external CSS/JS)
- Easy to maintain and extend

**Example Content**:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>NYC App House – Internal Dashboard</title>
    <style>
      * { box-sizing: border-box; }
      body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        margin: 0;
        padding: 2rem;
        background: #f5f5f5;
      }
      .container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      h1 {
        margin: 0 0 1rem 0;
        color: #333;
      }
      .intro {
        color: #666;
        margin-bottom: 2rem;
      }
      .app-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        list-style: none;
        padding: 0;
        margin: 0;
      }
      .app-card {
        background: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s;
      }
      .app-card:hover {
        background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
      }
      .app-card a {
        text-decoration: none;
        color: #0066cc;
        font-weight: 600;
        font-size: 1.1rem;
      }
      .app-card a:hover {
        color: #0052a3;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Internal Dashboard</h1>
      <p class="intro">Welcome to the walled garden. Select a service to get started:</p>
      <ul class="app-grid">
        <li class="app-card">
          <a href="/excalidraw/">Excalidraw</a>
          <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Drawing & Diagrams</p>
        </li>
        <li class="app-card">
          <a href="/cloud/">Nextcloud</a>
          <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">File Storage</p>
        </li>
        <!-- Add more applications here -->
      </ul>
    </div>
  </body>
</html>
```

#### 4.5.2 Adding New Applications to Dashboard

To add new applications:
1. Add container to `docker-compose.yml`
2. Add routing rule to `Caddyfile`
3. Add card to dashboard HTML:
```html
<li class="app-card">
  <a href="/newapp/">Application Name</a>
  <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Description</p>
</li>
```

### 4.6 Network Security Design

#### 4.6.1 Docker Network Isolation

**Network Name**: `internal`  
**Driver**: bridge (default)  
**Access**: Container-to-container only via service names

**Connectivity Matrix**:
```
                Caddy   Authelia   Excalidraw   Nextcloud   Internet
Caddy             -        Yes        Yes          Yes        Yes
Authelia         Yes        -         No           No         No
Excalidraw       Yes       No         -            No         No
Nextcloud        Yes       No         No           -          No
Internet         Yes       No         No           No         -
```

**Benefits**:
- Backend applications unreachable from internet
- Service discovery via DNS (container names)
- No IP address management required
- Easy addition of new services

#### 4.6.2 Firewall Configuration

**UFW Rules**:
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw enable
```

**Rationale**:
- Only required services exposed
- SSH retained for administration
- Outgoing unrestricted (for updates, ACME)

---

## 5. Implementation Guide

### 5.1 Prerequisites Checklist

Before beginning deployment, verify:
- [ ] VPS provisioned with Ubuntu 24.04 LTS
- [ ] Root or sudo access configured
- [ ] SSH key authentication enabled
- [ ] Domain registered and DNS access available
- [ ] Docker and Docker Compose installed
- [ ] Firewall configured (UFW or equivalent)
- [ ] VPS IP address documented

### 5.2 Pre-Deployment Steps

#### 5.2.1 DNS Configuration

Configure A record pointing to VPS IP:
```
Type: A
Name: run
Domain: nycapphouse.com
Value: <VPS_IP_ADDRESS>
TTL: 3600
```

**Verification**:
```bash
dig run.nycapphouse.com +short
# Should return: <VPS_IP_ADDRESS>
```

#### 5.2.2 System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installations
docker --version
docker compose version

# Configure firewall
sudo ufw allow 22,80,443/tcp
sudo ufw enable
sudo ufw status

# Create deployment directory
sudo mkdir -p /opt/authelia-stack
sudo chown $(whoami):$(whoami) /opt/authelia-stack
cd /opt/authelia-stack
```

### 5.3 Configuration File Creation

#### 5.3.1 Create docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: "3.9"

services:
  caddy:
    image: caddy:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./dashboard:/srv
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - internal

  authelia:
    image: authelia/authelia:latest
    container_name: authelia
    restart: unless-stopped
    volumes:
      - ./authelia:/config
    environment:
      - TZ=America/New_York
    networks:
      - internal

  excalidraw:
    image: excalidraw/excalidraw:latest
    container_name: excalidraw
    restart: unless-stopped
    networks:
      - internal

  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    restart: unless-stopped
    networks:
      - internal

networks:
  internal:

volumes:
  caddy_data:
  caddy_config:
EOF
```

#### 5.3.2 Create Caddyfile

**Important**: Replace `run.nycapphouse.com` with your actual domain and `you@example.com` with your email.

```bash
cat > Caddyfile << 'EOF'
{
    email you@example.com
}

run.nycapphouse.com {
    encode gzip
    tls you@example.com

    route {
        # Forward auth to Authelia
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }

        # Dashboard root
        handle_path / {
            root * /srv
            file_server
        }

        # Excalidraw under /excalidraw
        handle_path /excalidraw/* {
            reverse_proxy excalidraw:80
        }

        # Nextcloud under /cloud
        handle_path /cloud/* {
            reverse_proxy nextcloud:80
        }
    }
}
EOF
```

#### 5.3.3 Create Dashboard

```bash
mkdir -p dashboard
cat > dashboard/index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Internal Dashboard</title>
    <style>
      * { box-sizing: border-box; }
      body {
        font-family: system-ui, -apple-system, sans-serif;
        margin: 0;
        padding: 2rem;
        background: #f5f5f5;
      }
      .container {
        max-width: 800px;
        margin: 0 auto;
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      h1 { margin: 0 0 1rem 0; color: #333; }
      .intro { color: #666; margin-bottom: 2rem; }
      .app-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
        list-style: none;
        padding: 0;
        margin: 0;
      }
      .app-card {
        background: #f9f9f9;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.2s;
      }
      .app-card:hover {
        background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
      }
      .app-card a {
        text-decoration: none;
        color: #0066cc;
        font-weight: 600;
        font-size: 1.1rem;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Internal Dashboard</h1>
      <p class="intro">Welcome to the walled garden. Select a service:</p>
      <ul class="app-grid">
        <li class="app-card">
          <a href="/excalidraw/">Excalidraw</a>
        </li>
        <li class="app-card">
          <a href="/cloud/">Nextcloud</a>
        </li>
      </ul>
    </div>
  </body>
</html>
EOF
```

#### 5.3.4 Create Authelia Configuration

```bash
mkdir -p authelia

# Generate secrets (SAVE THESE VALUES!)
JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')
SESSION_SECRET=$(openssl rand -base64 64 | tr -d '\n')

echo "Generated secrets (SAVE THESE):"
echo "JWT_SECRET: $JWT_SECRET"
echo "SESSION_SECRET: $SESSION_SECRET"

# Create configuration file
cat > authelia/configuration.yml << EOF
host: 0.0.0.0
port: 9091

log:
  level: info

theme: light

jwt:
  secret: "${JWT_SECRET}"

default_redirection_url: https://run.nycapphouse.com

authentication_backend:
  file:
    path: /config/users_database.yml
    password:
      algorithm: argon2id
      iterations: 3
      key_length: 32
      salt_length: 16
      memory: 65536
      parallelism: 4

session:
  name: authelia_session
  secret: "${SESSION_SECRET}"
  inactivity: 3600
  expiration: 7200
  domain: nycapphouse.com
  same_site: lax

totp:
  issuer: nycapphouse.com
  period: 30
  skew: 1

access_control:
  default_policy: deny
  rules:
    - domain: "run.nycapphouse.com"
      policy: one_factor

notifier:
  filesystem:
    filename: /config/notification.log
EOF
```

#### 5.3.5 Create User Database

```bash
# Generate password hash for initial user
echo "Enter password for initial user:"
HASH=$(docker run --rm -it authelia/authelia:latest authelia hash-password 'YourPasswordHere')

# Create users database
cat > authelia/users_database.yml << EOF
users:
  admin:
    displayname: "Administrator"
    password: "${HASH}"
    email: "admin@example.com"
    groups:
      - admins
EOF
```

**Manual Alternative**:
```bash
# Run hash generator interactively
docker run --rm -it authelia/authelia:latest authelia hash-password

# Then manually create authelia/users_database.yml and paste the hash
```

### 5.4 Deployment Steps

#### 5.4.1 Initial Deployment

```bash
# Navigate to deployment directory
cd /opt/authelia-stack

# Pull latest images
docker compose pull

# Start services
docker compose up -d

# Verify all containers are running
docker compose ps

# Expected output:
# NAME        IMAGE                     STATUS
# authelia    authelia/authelia:latest  Up
# caddy       caddy:latest              Up
# excalidraw  excalidraw/excalidraw     Up
# nextcloud   nextcloud:latest          Up
```

#### 5.4.2 Log Monitoring

```bash
# Watch all service logs
docker compose logs -f

# Watch specific service
docker compose logs -f caddy
docker compose logs -f authelia

# Check for errors
docker compose logs --tail=50 authelia | grep -i error
```

### 5.5 Verification Testing

#### 5.5.1 SSL Certificate Check

```bash
# Test SSL certificate provisioning
curl -I https://run.nycapphouse.com

# Expected: HTTP/2 200, valid certificate from Let's Encrypt
```

#### 5.5.2 Authentication Flow Test

**Test Procedure**:
1. Open browser to `https://run.nycapphouse.com`
2. Expected: Redirect to Authelia login page
3. Enter credentials from users_database.yml
4. Expected: Redirect to dashboard
5. Click "Excalidraw" link
6. Expected: Application loads without additional authentication
7. Open new browser tab to `https://run.nycapphouse.com/cloud/`
8. Expected: Direct access to Nextcloud (session preserved)

#### 5.5.3 Security Verification

```bash
# Verify backend applications not directly accessible
curl http://<VPS_IP>:80/excalidraw/
# Expected: Connection refused or timeout

# Verify firewall rules
sudo ufw status numbered
# Expected: Only 22, 80, 443 allowed

# Check container network isolation
docker network inspect authelia-stack_internal
# Verify: Only expected containers attached
```

---

## 6. Operations & Maintenance

### 6.1 Routine Maintenance Tasks

#### 6.1.1 Daily
- Monitor service logs for errors
- Review authentication logs in Authelia

#### 6.1.2 Weekly
- Check disk space usage
- Review Docker container status
- Check SSL certificate expiration dates (Caddy auto-renews)

#### 6.1.3 Monthly
- Apply system security updates
- Update Docker images
- Review and rotate secrets if required by policy
- Backup configuration files

### 6.2 Update Procedures

#### 6.2.1 Update Docker Images

```bash
cd /opt/authelia-stack

# Pull latest images
docker compose pull

# Restart with new images (minimal downtime)
docker compose up -d

# Clean old images
docker image prune -a
```

#### 6.2.2 Configuration Updates

```bash
# After editing configuration files:
docker compose restart <service_name>

# Example: After updating Caddyfile
docker compose restart caddy

# Example: After updating Authelia config
docker compose restart authelia
```

### 6.3 User Management

#### 6.3.1 Add New User

```bash
# Generate password hash
docker run --rm -it authelia/authelia:latest authelia hash-password 'NewUserPassword'

# Edit users database
nano authelia/users_database.yml

# Add new user:
#   newuser:
#     displayname: "New User"
#     password: "<GENERATED_HASH>"
#     email: "newuser@example.com"
#     groups:
#       - users

# Restart Authelia
docker compose restart authelia
```

#### 6.3.2 Reset User Password

```bash
# Generate new hash
docker run --rm -it authelia/authelia:latest authelia hash-password 'NewPassword'

# Update password in authelia/users_database.yml
# Restart Authelia
docker compose restart authelia
```

#### 6.3.3 Remove User

```bash
# Edit users database
nano authelia/users_database.yml

# Delete user entry
# Restart Authelia
docker compose restart authelia
```

### 6.4 Adding New Applications

#### Step-by-Step Process:

1. **Add to docker-compose.yml**:
```yaml
newapp:
  image: newapp/newapp:latest
  container_name: newapp
  restart: unless-stopped
  networks:
    - internal
```

2. **Add route to Caddyfile**:
```caddyfile
handle_path /newapp/* {
    reverse_proxy newapp:80
}
```

3. **Add to dashboard** (dashboard/index.html):
```html
<li class="app-card">
  <a href="/newapp/">New Application</a>
</li>
```

4. **Deploy**:
```bash
docker compose up -d
docker compose restart caddy
```

### 6.5 Backup Procedures

#### 6.5.1 Configuration Backup

```bash
# Create backup directory
mkdir -p ~/backups/authelia-stack

# Backup configuration (excluding secrets in separate file)
tar -czf ~/backups/authelia-stack/config-$(date +%Y%m%d).tar.gz \
  -C /opt/authelia-stack \
  --exclude='authelia/notification.log' \
  --exclude='volumes' \
  .

# Backup secrets separately (encrypted)
gpg --symmetric --cipher-algo AES256 \
  -o ~/backups/authelia-stack/secrets-$(date +%Y%m%d).gpg \
  /opt/authelia-stack/authelia/configuration.yml
```

#### 6.5.2 Application Data Backup

```bash
# Backup Docker volumes
docker run --rm \
  -v authelia-stack_caddy_data:/source \
  -v ~/backups:/backup \
  alpine \
  tar -czf /backup/caddy-data-$(date +%Y%m%d).tar.gz -C /source .

# For application-specific data (e.g., Nextcloud)
docker compose exec nextcloud tar -czf /tmp/nextcloud-data.tar.gz /var/www/html/data
docker cp nextcloud:/tmp/nextcloud-data.tar.gz ~/backups/
```

#### 6.5.3 Automated Backup Script

```bash
#!/bin/bash
# /opt/authelia-stack/backup.sh

BACKUP_DIR="$HOME/backups/authelia-stack"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# Configuration backup
tar -czf "$BACKUP_DIR/config-$DATE.tar.gz" \
  -C /opt/authelia-stack \
  --exclude='volumes' \
  --exclude='*.log' \
  .

# Retain only last 7 days
find "$BACKUP_DIR" -name "config-*.tar.gz" -mtime +7 -delete

echo "Backup completed: config-$DATE.tar.gz"
```

**Cron Schedule**:
```bash
# Run daily at 2 AM
0 2 * * * /opt/authelia-stack/backup.sh >> /var/log/authelia-backup.log 2>&1
```

### 6.6 Monitoring & Logging

#### 6.6.1 Log Locations

| Service | Log Location | Access Method |
|---------|-------------|---------------|
| Caddy | Container logs | `docker compose logs caddy` |
| Authelia | Container logs | `docker compose logs authelia` |
| Authelia Notifications | `/opt/authelia-stack/authelia/notification.log` | `tail -f authelia/notification.log` |
| System | `/var/log/syslog` | `tail -f /var/log/syslog` |

#### 6.6.2 Key Metrics to Monitor

- Failed authentication attempts (Authelia logs)
- Certificate renewal status (Caddy logs)
- Container restart count
- Disk space usage
- Memory consumption
- Network connectivity

#### 6.6.3 Simple Monitoring Script

```bash
#!/bin/bash
# /opt/authelia-stack/health-check.sh

echo "=== Container Status ==="
docker compose ps

echo -e "\n=== Recent Errors ==="
docker compose logs --tail=20 --since=1h | grep -i error

echo -e "\n=== Disk Usage ==="
df -h /opt/authelia-stack

echo -e "\n=== Authentication Failures (Last Hour) ==="
docker compose logs authelia --since=1h | grep -i "authentication failed" | wc -l
```

---

## 7. Security Considerations

### 7.1 Threat Model

#### Identified Threats:
1. **T-01**: Unauthorized access to backend applications
   - **Mitigation**: Network isolation, no published ports
2. **T-02**: Brute force authentication attacks
   - **Mitigation**: Rate limiting (Authelia built-in), strong password policy
3. **T-03**: Session hijacking
   - **Mitigation**: Secure cookies, HTTPS only, session timeout
4. **T-04**: SSL/TLS certificate compromise
   - **Mitigation**: Automatic rotation, ACME protocol
5. **T-05**: Container escape
   - **Mitigation**: Docker security best practices, regular updates
6. **T-06**: Configuration disclosure
   - **Mitigation**: File permissions, no secrets in version control

### 7.2 Security Best Practices

#### 7.2.1 Secret Management

**Critical Secrets**:
- JWT secret (Authelia)
- Session secret (Authelia)
- User password hashes
- ACME account key (Caddy auto-managed)

**Protection Measures**:
```bash
# Restrict configuration file permissions
chmod 600 authelia/configuration.yml
chmod 600 authelia/users_database.yml

# Verify no secrets in git
echo "authelia/configuration.yml" >> .gitignore
echo "authelia/users_database.yml" >> .gitignore

# Regular secret rotation (recommended annually)
```

#### 7.2.2 Password Policy

**Requirements**:
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, special characters
- No common passwords or dictionary words
- Argon2id hashing with specified parameters

**Enforcement**:
- Hashing parameters in configuration.yml
- User education and training
- Regular password audits

#### 7.2.3 Two-Factor Authentication

**Recommendation**: Enable for all administrative accounts

**Implementation**:
```yaml
# In authelia/configuration.yml
access_control:
  default_policy: deny
  rules:
    - domain: "run.nycapphouse.com"
      policy: two_factor  # Requires TOTP
      subject:
        - "group:admins"
    - domain: "run.nycapphouse.com"
      policy: one_factor  # Password only
      subject:
        - "group:users"
```

#### 7.2.4 Network Security

**Best Practices**:
- Keep firewall rules minimal (only 22, 80, 443)
- Consider SSH key-only authentication
- Use fail2ban for SSH protection
- Consider IP whitelisting for SSH if feasible
- Regular security updates via unattended-upgrades

#### 7.2.5 Docker Security

**Recommendations**:
```yaml
# Add security options to docker-compose.yml
services:
  caddy:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

**Additional Measures**:
- Run containers as non-root users when possible
- Limit container capabilities
- Regular image updates
- Scan images for vulnerabilities

### 7.3 Incident Response

#### 7.3.1 Suspected Breach

**Immediate Actions**:
1. Isolate affected containers: `docker compose stop <service>`
2. Capture logs: `docker compose logs > incident-$(date +%Y%m%d).log`
3. Check authentication logs for unusual activity
4. Review firewall logs
5. Rotate all secrets
6. Force logout all users (restart Authelia with new session secret)

#### 7.3.2 Failed Authentication Monitoring

```bash
# Check for brute force attempts
docker compose logs authelia | grep "authentication failed" | \
  awk '{print $NF}' | sort | uniq -c | sort -rn

# If suspicious activity detected, consider IP blocking at firewall level
```

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Issue 8.1.1: SSL Certificate Not Provisioning

**Symptoms**:
- Browser shows certificate error
- Caddy logs show ACME errors
- Cannot access site via HTTPS

**Diagnosis**:
```bash
docker compose logs caddy | grep -i acme
docker compose logs caddy | grep -i certificate
```

**Common Causes & Solutions**:
1. **DNS not propagated**:
   - Wait 1-24 hours for DNS propagation
   - Verify: `dig run.nycapphouse.com +short`
2. **Port 80 blocked**:
   - ACME requires port 80 for HTTP-01 challenge
   - Check: `sudo ufw status`
3. **Rate limiting**:
   - Let's Encrypt has rate limits (5 failures per hour)
   - Wait and retry
4. **Email not configured**:
   - Ensure `email` directive in Caddyfile

**Resolution Steps**:
```bash
# Stop Caddy
docker compose stop caddy

# Remove certificates
docker volume rm authelia-stack_caddy_data

# Verify DNS
dig run.nycapphouse.com +short

# Verify firewall
sudo ufw status | grep -E '80|443'

# Restart with verbose logging
docker compose up -d caddy
docker compose logs -f caddy
```

#### Issue 8.1.2: Authentication Loop / Constant Redirects

**Symptoms**:
- Login appears successful but redirects back to login
- Browser console shows redirect loop errors

**Diagnosis**:
```bash
# Check Authelia logs
docker compose logs authelia | tail -50

# Check session configuration
cat authelia/configuration.yml | grep -A 10 session

# Check browser cookies
# Look for "authelia_session" cookie in Developer Tools
```

**Common Causes & Solutions**:
1. **Domain mismatch**:
   - `session.domain` must match actual domain
   - Use parent domain: `nycapphouse.com` not `run.nycapphouse.com`
2. **Cookie settings**:
   - `same_site: lax` required for cross-path cookies
3. **Time synchronization**:
   - JWT tokens require accurate time
   - Check: `date` on server

**Resolution**:
```bash
# Fix session domain in configuration
nano authelia/configuration.yml
# Ensure: domain: nycapphouse.com (parent domain)

# Restart Authelia
docker compose restart authelia

# Clear browser cookies and test again
```

#### Issue 8.1.3: Backend Application Not Loading

**Symptoms**:
- Dashboard loads correctly
- Clicking application link shows error or blank page
- Caddy logs show 502 Bad Gateway

**Diagnosis**:
```bash
# Check if container is running
docker compose ps

# Check container logs
docker compose logs excalidraw

# Test internal connectivity
docker compose exec caddy wget -O- http://excalidraw:80
```

**Common Causes & Solutions**:
1. **Container not running**:
   ```bash
   docker compose up -d excalidraw
   ```
2. **Wrong internal port**:
   - Verify application listens on expected port
   - Check: `docker compose exec excalidraw netstat -tlnp`
3. **Application startup delay**:
   - Some apps take time to initialize
   - Check container logs for "ready" messages

**Resolution**:
```bash
# Restart specific container
docker compose restart excalidraw

# If persistent, check application-specific requirements
docker compose logs excalidraw | tail -50
```

#### Issue 8.1.4: "Permission Denied" Errors

**Symptoms**:
- Authelia cannot read configuration files
- Caddy cannot access dashboard files

**Diagnosis**:
```bash
# Check file permissions
ls -la authelia/
ls -la dashboard/

# Check file ownership
docker compose exec authelia ls -la /config
```

**Solution**:
```bash
# Fix permissions
chmod 644 authelia/configuration.yml
chmod 644 authelia/users_database.yml
chmod 644 dashboard/index.html

# Restart affected services
docker compose restart authelia caddy
```

### 8.2 Debug Mode Activation

#### Enable Verbose Logging

**Authelia**:
```yaml
# In authelia/configuration.yml
log:
  level: debug  # Change from 'info' to 'debug'
```

**Caddy**:
```caddyfile
# Add at top of Caddyfile
{
    debug
}
```

**Restart Services**:
```bash
docker compose restart authelia caddy
docker compose logs -f
```

### 8.3 Health Check Commands

```bash
# Quick system health check
cat << 'EOF' > /opt/authelia-stack/healthcheck.sh
#!/bin/bash
echo "=== Container Status ==="
docker compose ps

echo -e "\n=== Connectivity Tests ==="
curl -I -s https://run.nycapphouse.com | head -1

echo -e "\n=== Certificate Check ==="
openssl s_client -connect run.nycapphouse.com:443 -servername run.nycapphouse.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

echo -e "\n=== Recent Errors ==="
docker compose logs --tail=20 --since=10m | grep -i error | wc -l

echo -e "\n=== Disk Usage ==="
df -h /opt/authelia-stack
EOF

chmod +x /opt/authelia-stack/healthcheck.sh
```

---

## 9. Performance Optimization

### 9.1 Resource Allocation

#### Recommended Container Limits

```yaml
# Add to docker-compose.yml services
services:
  caddy:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 256M
        reservations:
          cpus: '0.5'
          memory: 128M
  
  authelia:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 128M
        reservations:
          cpus: '0.25'
          memory: 64M
```

### 9.2 Caching Strategy

#### Caddy Response Caching

```caddyfile
# Add to Caddyfile for static assets
handle_path /static/* {
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
}
```

### 9.3 Connection Pooling

#### Authelia Session Storage

For high-traffic deployments, consider Redis:

```yaml
# Add to docker-compose.yml
redis:
  image: redis:alpine
  container_name: redis
  restart: unless-stopped
  networks:
    - internal

# Update authelia/configuration.yml
session:
  redis:
    host: redis
    port: 6379
```

### 9.4 Monitoring Performance

```bash
# Monitor container resource usage
docker stats

# Check response times
time curl -I https://run.nycapphouse.com

# Monitor authentication latency
docker compose logs authelia | grep "authentication" | tail -20
```

---

## 10. Migration & Scalability

### 10.1 Adding Cloudflare (Future)

When ready to add Cloudflare CDN:

1. **Update DNS**:
   - Change A record to Cloudflare proxy
   - Enable "Proxied" status in Cloudflare dashboard

2. **Update Caddy Configuration**:
```caddyfile
{
    servers {
        trusted_proxies cloudflare {
            interval 12h
            timeout 15s
        }
    }
}
```

3. **Authelia Configuration**:
```yaml
# No changes required - Authelia operates normally behind Cloudflare
```

**Benefits**:
- DDoS protection
- CDN for static assets
- Additional rate limiting
- Analytics

**Considerations**:
- Real IP forwarding (handled by trusted_proxies)
- Cloudflare SSL mode: "Full (strict)"

### 10.2 Subdomain-Based Routing

To migrate from path-based (`/excalidraw`) to subdomain-based (`excalidraw.run.nycapphouse.com`):

**DNS Changes**:
```
A record: excalidraw.run.nycapphouse.com -> <VPS_IP>
A record: cloud.run.nycapphouse.com -> <VPS_IP>
```

**Caddyfile Changes**:
```caddyfile
excalidraw.run.nycapphouse.com {
    encode gzip
    
    route {
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }
        
        reverse_proxy excalidraw:80
    }
}

cloud.run.nycapphouse.com {
    encode gzip
    
    route {
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }
        
        reverse_proxy nextcloud:80
    }
}
```

**Authelia Access Control**:
```yaml
access_control:
  rules:
    - domain:
        - "excalidraw.run.nycapphouse.com"
        - "cloud.run.nycapphouse.com"
      policy: one_factor
```

### 10.3 Multi-Server Deployment

For scaling beyond single VPS:

**Architecture Changes**:
1. Separate auth server (Authelia + Redis)
2. Separate application servers
3. Shared Redis for session storage
4. Load balancer (additional Caddy or HAProxy)

**Considerations**:
- Session sharing via Redis
- Certificate management across servers
- Health checks and failover
- Database replication for user storage

---

## 11. Compliance & Documentation

### 11.1 Data Handling

#### Personal Information Stored:
- Usernames (identifiers)
- Display names
- Email addresses
- Password hashes (Argon2id)
- Session tokens (temporary, in-memory or Redis)

#### Data Retention:
- User accounts: Until manually deleted
- Session data: Expires per configuration (default: 2 hours)
- Authentication logs: Retained in Docker logs (recommend 7-day rotation)

### 11.2 Access Logs

**Recommendation**: Implement log rotation for compliance:

```yaml
# Add to docker-compose.yml
services:
  caddy:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 11.3 System Documentation

**Required Documentation** (this PDR serves as foundation):
- Architecture diagrams
- Network topology
- Data flow diagrams
- Incident response procedures
- Backup and recovery procedures
- User onboarding and offboarding procedures

---

## 12. Future Enhancements

### 12.1 Short-Term (1-3 months)

1. **Enhanced Monitoring**:
   - Prometheus metrics export
   - Grafana dashboards
   - Alert manager integration

2. **Backup Automation**:
   - Automated off-site backups
   - Restore testing procedures

3. **Documentation Expansion**:
   - User-facing documentation
   - Video tutorials
   - Runbook automation

### 12.2 Medium-Term (3-6 months)

1. **Database Backend**:
   - Migrate from file-based to PostgreSQL
   - Centralized user management
   - Audit logging

2. **Identity Provider Integration**:
   - LDAP/Active Directory sync
   - OAuth2/OIDC provider capability
   - External IdP integration (Google, GitHub, etc.)

3. **Advanced Security**:
   - Hardware security key support (WebAuthn)
   - Biometric authentication
   - Anomaly detection

### 12.3 Long-Term (6-12 months)

1. **High Availability**:
   - Multi-node deployment
   - Geographic redundancy
   - Automated failover

2. **Performance Optimization**:
   - CDN integration
   - Edge caching
   - Load balancing

3. **Advanced Features**:
   - Per-application access policies
   - Time-based access restrictions
   - IP geolocation filtering

---

## 13. Appendices

### Appendix A: Quick Reference Commands

```bash
# Deployment
cd /opt/authelia-stack
docker compose up -d

# Status check
docker compose ps
docker compose logs

# Restart services
docker compose restart
docker compose restart caddy
docker compose restart authelia

# Update images
docker compose pull
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f
docker compose logs --tail=100 authelia

# Generate password hash
docker run --rm -it authelia/authelia:latest authelia hash-password

# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz -C /opt/authelia-stack .
```

### Appendix B: Port Reference

| Port | Service | Purpose | Exposed Externally |
|------|---------|---------|-------------------|
| 22 | SSH | Server administration | Yes (restricted) |
| 80 | Caddy | HTTP (redirects to HTTPS) | Yes |
| 443 | Caddy | HTTPS | Yes |
| 9091 | Authelia | Authentication API | No (internal only) |
| 80 | Excalidraw | Application | No (via Caddy proxy) |
| 80 | Nextcloud | Application | No (via Caddy proxy) |

### Appendix C: File Locations Quick Reference

| Purpose | Location |
|---------|----------|
| Deployment base | `/opt/authelia-stack/` |
| Docker Compose config | `/opt/authelia-stack/docker-compose.yml` |
| Caddy routing | `/opt/authelia-stack/Caddyfile` |
| Dashboard HTML | `/opt/authelia-stack/dashboard/index.html` |
| Authelia config | `/opt/authelia-stack/authelia/configuration.yml` |
| User database | `/opt/authelia-stack/authelia/users_database.yml` |
| Caddy SSL certs | Docker volume: `authelia-stack_caddy_data` |
| Backup location | `~/backups/authelia-stack/` |
| Health check script | `/opt/authelia-stack/healthcheck.sh` |

### Appendix D: Environment Variables

Optional environment variables for docker-compose.yml:

```yaml
services:
  authelia:
    environment:
      - TZ=America/New_York
      - AUTHELIA_JWT_SECRET=${JWT_SECRET}
      - AUTHELIA_SESSION_SECRET=${SESSION_SECRET}
```

Create `.env` file:
```bash
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here
```

**Security Note**: Add `.env` to `.gitignore`

### Appendix E: Glossary

| Term | Definition |
|------|------------|
| **ACME** | Automated Certificate Management Environment - protocol for automated SSL certificates |
| **Argon2id** | Password hashing algorithm resistant to GPU cracking attacks |
| **Forward Auth** | Authentication pattern where reverse proxy delegates auth to separate service |
| **JWT** | JSON Web Token - compact, self-contained way for securely transmitting information |
| **TOTP** | Time-based One-Time Password - 2FA method using rotating codes |
| **SSO** | Single Sign-On - one login for multiple applications |
| **Reverse Proxy** | Server that forwards client requests to backend servers |
| **VPS** | Virtual Private Server - virtualized server instance |

### Appendix F: Support Resources

| Resource | URL / Command |
|----------|---------------|
| Authelia Documentation | https://www.authelia.com/docs/ |
| Caddy Documentation | https://caddyserver.com/docs/ |
| Docker Compose Reference | https://docs.docker.com/compose/ |
| Let's Encrypt Status | https://letsencrypt.status.io/ |
| Ubuntu Server Guide | https://ubuntu.com/server/docs |
| System Logs | `journalctl -xe` |
| Docker Logs | `docker compose logs` |

### Appendix G: Change Log Template

For tracking changes to production deployment:

```markdown
## Change Log

### [Date] - [Change Type: Config/Security/Feature]
**Changed By**: [Name]
**Description**: [What was changed and why]
**Files Modified**: [List of files]
**Rollback Procedure**: [How to undo if needed]
**Verification**: [How to confirm change worked]
```

---

## 14. Conclusion

This PDR provides a comprehensive guide for deploying and maintaining an Authelia-based walled garden authentication system. The architecture balances security, simplicity, and scalability while providing clear operational procedures for system administrators and integration guidelines for web developers.

Key takeaways:
- **Security-first design** with network isolation and centralized authentication
- **Simple deployment** using Docker Compose and standard tools
- **Production-ready** with SSL automation and monitoring guidance
- **Maintainable** with clear procedures and troubleshooting guides
- **Scalable** with clear paths for future expansion

For questions, issues, or suggestions for improvement, maintain a change log and update this document as the system evolves.

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| System Administrator | | | |
| Security Officer | | | |
| Technical Lead | | | |

---

**End of Document**
