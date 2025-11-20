# Authelia Walled Garden - Reference Architecture

Production-ready reference architecture for deploying an Authelia-based authentication gateway with Caddy reverse proxy.

**Version**: 1.0.0
**Status**: Production-Ready Reference Implementation
**License**: MIT

## What This Is

This repository contains a **complete reference architecture** for deploying a secure, SSO-enabled service gateway using:
- **Authelia** - Authentication and authorization server
- **Caddy** - Reverse proxy with automatic HTTPS
- **Docker Compose** - Service orchestration
- **Multiple backend services** - Example integrations

**This is NOT** a software package or turnkey solution. It's a comprehensive guide and example implementation designed to be cloned, studied, and customized for your specific needs.

**Perfect for**:
- System administrators deploying Authelia
- DevOps engineers building authenticated service platforms
- Security engineers implementing SSO
- Homelab enthusiasts protecting self-hosted services

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Examples](#examples)
- [Screenshots](#screenshots)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

## Features

### Security-First Architecture
- **Zero Trust Model**: All services require authentication by default
- **Single Sign-On (SSO)**: One login for all services
- **Two-Factor Authentication (2FA)**: TOTP support via Authelia
- **Network Isolation**: Backend services on internal Docker network
- **Automatic HTTPS**: Caddy handles SSL/TLS via Let's Encrypt
- **Password Breach Detection**: HaveIBeenPwned integration
- **Audit Logging**: HMAC-signed audit trail

### Production-Ready Components
- **Reverse Proxy**: Caddy with automatic certificate management
- **Authentication Gateway**: Authelia with file-based or LDAP backends
- **User Management**: Web-based admin interface (authelia-file-admin)
- **Service Discovery**: Dynamic routing configuration
- **Health Monitoring**: Container health checks
- **Backup & Recovery**: Documented procedures

### Developer-Friendly
- **Pre-Built Images**: All custom components available on Docker Hub - no build required
- **Clear Documentation**: Comprehensive guides and examples
- **Example Services**: Pre-configured integrations (Excalidraw, Portainer, n8n, etc.)
- **Custom Dashboard**: Application launcher with service cards
- **DNS Tools**: Built-in troubleshooting utilities
- **Modular Design**: Easy to add/remove services
- **One-Command Deploy**: Clone and run `docker compose up -d`

## Architecture

### High-Level Overview

```
Internet
  │
  ↓
[Caddy Reverse Proxy :443]
  │
  ↓
[Authelia :9091] ← Authentication Check
  │
  ├─ Not Authenticated → Redirect to /auth/
  │
  └─ Authenticated → Forward to Backend
                        │
                        ↓
              [Internal Docker Network]
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    [Service 1]    [Service 2]    [Service 3]
```

### Authentication Flow

1. User requests `https://example.com/service/`
2. Caddy performs `forward_auth` check to Authelia
3. Authelia checks session cookie
4. If not authenticated → redirect to `https://example.com/auth/`
5. User logs in with username + password (+ optional 2FA)
6. Authelia sets session cookie (domain-wide)
7. User redirected back to original service
8. Caddy proxies request with user context headers
9. Backend receives request with `Remote-User`, `Remote-Groups`, etc.

See [Architecture Documentation](docs/ARCHITECTURE.md) for detailed diagrams.

### Network Topology

**External Access**:
- Port 80 (HTTP) → Caddy → Redirects to HTTPS
- Port 443 (HTTPS) → Caddy → Terminates TLS

**Internal Docker Network**:
- Authelia (internal:9091)
- Backend services (no published ports)
- All inter-service communication on bridge network

**Security Benefits**:
- Backend services never exposed directly to internet
- All traffic encrypted (HTTPS)
- Centralized authentication
- Session sharing across services

## Quick Start

**Everything included!** All components use pre-built Docker images - no separate repositories to clone, no build process required. Just configure and deploy.

### Prerequisites

- Docker and Docker Compose installed
- Domain name with DNS control
- Ports 80 and 443 available
- Basic understanding of Docker and reverse proxies

### 5-Minute Deployment

1. **Clone this repository**:
   ```bash
   git clone https://github.com/dustinnh/Walled-Garden.git
   cd Walled-Garden/examples
   ```

2. **Generate secrets**:
   ```bash
   chmod +x scripts/generate-secrets.sh
   ./scripts/generate-secrets.sh > secrets.txt
   # Save these secrets securely!
   ```

3. **Configure your domain**:
   ```bash
   # Edit examples/docker-compose.yml
   # Edit examples/Caddyfile
   # Edit examples/authelia-config.yml
   # Replace "example.com" with your actual domain
   ```

4. **Create your first user**:
   ```bash
   # Generate password hash
   docker run --rm -it authelia/authelia:latest \
     authelia hash-password 'YourSecurePassword123!'
   
   # Add to examples/users_database.yml
   ```

5. **Deploy the stack**:
   ```bash
   cp examples/* /opt/authelia-stack/  # Or your deployment directory
   cd /opt/authelia-stack
   docker compose up -d
   ```

6. **Verify deployment**:
   ```bash
   docker compose ps
   curl https://your-domain.com/health
   ```

See [Full Deployment Guide](docs/PDR.md) for comprehensive instructions.

## Development Workflow

If you're running this in production and want to develop safely:

### Quick Workflow
1. **Edit** in this git repository (`walledgarden-gh/`)
2. **Commit** changes to git
3. **Test** in staging environment
4. **Deploy** to production with deployment script

### Deployment Scripts
- `scripts/deploy-staging.sh` - Deploy to staging for testing
- `scripts/deploy-production.sh` - Deploy tested changes to production
- `scripts/backup.sh` - Backup production before deployment

### Keeping Production Safe
- Git repository = source of truth (this directory)
- Staging environment = test changes safely
- Production = deploy only tested changes
- Secrets = separate .env files (never in git)

See [Development Workflow Guide](docs/DEVELOPMENT-WORKFLOW.md) for complete details on:
- Setting up staging environment
- Managing secrets across environments
- Daily development workflow
- Troubleshooting deployments

## Documentation

### Core Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design, network topology, security model
- **[Project Design Record (PDR)](docs/PDR.md)** - Complete deployment guide (1,955 lines)
- **[How-To: Add Services](docs/HOWTO-ADD-SERVICES.md)** - Step-by-step service integration
- **[Nexterm Integration](docs/NEXTERM-INSTALLATION.md)** - Terminal access example

### Advanced Topics

- **[DNS Tool Architecture](docs/advanced/dns-tool-architecture.md)** - Custom troubleshooting utilities
- **[Custom Styling](docs/advanced/custom-styling.md)** - Theming Authelia and dashboard
- **[Backup & Recovery](docs/OPERATIONS.md)** - Operational procedures

### Quick References

- **[Configuration Guide](docs/CONFIGURATION.md)** - All environment variables explained
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Security Best Practices](docs/SECURITY.md)** - Hardening recommendations

## Examples

All example configurations are in the [`examples/`](examples/) directory:

### Configuration Files

- **[docker-compose.yml](examples/docker-compose.yml)** - Full stack orchestration
- **[Caddyfile](examples/Caddyfile)** - Reverse proxy routing
- **[authelia-config.yml](examples/authelia-config.yml)** - Authentication server config
- **[.env.template](examples/.env.template)** - Environment variables template

### Dashboard Templates

- **[Application Launcher](examples/dashboard/index.html)** - Main dashboard UI
- **[User Management](examples/dashboard/admin.html)** - Admin interface
- **[DNS Tools](examples/dashboard/dns.html)** - Troubleshooting utilities

### Helper Scripts

- **[generate-secrets.sh](scripts/generate-secrets.sh)** - Generate Authelia secrets
- **[backup.sh](scripts/backup.sh)** - Backup configurations and data
- **[check-config.sh](scripts/check-config.sh)** - Validate configurations

**IMPORTANT**: All example configurations have been sanitized. You MUST:
- Generate your own secrets (never use examples in production)
- Replace `example.com` with your actual domain
- Configure SMTP settings for email notifications (optional)
- Review and customize access control rules

## Screenshots

### Main Dashboard
![Dashboard](screenshots/dashboard.png)
*Application launcher showing all authenticated services with SSO protection*

### Authelia Login
![Login](screenshots/authelia-login.png)
*Single sign-on authentication portal with 2FA support*

### Architecture Diagram
![Architecture](screenshots/architecture-overview.png)
*Complete system architecture showing network topology and authentication flow*

### DNS Tools
![DNS Tools](screenshots/dns-tools.png)
*Custom DNS troubleshooting utilities for diagnosing connectivity issues*

### User Management
![User Admin](screenshots/user-admin.png)
*Web-based interface for managing user accounts, passwords, and groups*

## Related Projects

### User Management Component

**[Authelia Admin Panel](https://github.com/dustinnh/Authelia-Admin-Panel)** - Production-ready web interface for managing file-based Authelia user accounts

[![Version](https://img.shields.io/badge/version-1.10.0-green.svg)](https://github.com/dustinnh/Authelia-Admin-Panel/releases)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/dustinnh/Authelia-Admin-Panel)

**The only dedicated GUI administration tool for file-based Authelia deployments.**

This walled garden **includes the Authelia Admin Panel** as the user management component (accessible at `/admin` endpoint). The admin panel provides:

**Security Features**:
- 🔒 Password breach detection via HaveIBeenPwned (600M+ breaches)
- 🔒 Password history tracking (prevent reuse of last N passwords)
- 🔒 Password expiration policies (configurable days)
- 🔒 HMAC-signed audit logging with tamper detection
- 🔒 Email notifications for security events

**Management Features**:
- 👤 Create, read, update, delete users via web interface
- 👤 Group management and bulk CSV import/export
- 👤 Real-time password validation with strength meter
- 👤 Search, filter, and sort users
- 👤 User statistics and password health dashboard

**Production-Ready**:
- ⚡ Gunicorn WSGI server (4 workers, production-grade)
- ⚡ File locking for safe concurrent access
- ⚡ CSRF protection and XSS prevention
- ⚡ Rate limiting and security headers

### Standalone Use

**The Admin Panel can also be used independently** with your existing Authelia setup if you already have Authelia running with Nginx, Traefik, or another reverse proxy.

See the [Admin Panel repository](https://github.com/dustinnh/Authelia-Admin-Panel) for standalone installation instructions.

### How It's Integrated

In this walled garden architecture, the admin panel is included as a **pre-built Docker image** in `examples/docker-compose.yml`:

```yaml
user-admin:
  image: dutdok4/authelia-admin:latest  # Pre-built image
  container_name: user-admin
  # ... configuration
```

**No separate installation required!** The image is automatically pulled when you run `docker compose up -d`.

To pin to a specific version (recommended for production):
```yaml
image: dutdok4/authelia-admin:1.10.0  # Pin to specific version
```

### Official Projects

- **[Authelia](https://www.authelia.com/)** - The authentication and authorization server
- **[Caddy](https://caddyserver.com/)** - The reverse proxy with automatic HTTPS

### Community Resources

- [Authelia Documentation](https://www.authelia.com/docs/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [r/selfhosted](https://www.reddit.com/r/selfhosted/) - Self-hosting community
- [r/homelab](https://www.reddit.com/r/homelab/) - Homelab community

## FAQ

### Is this a software product I can install?

No. This is a **reference architecture and documentation project**. Think of it as a comprehensive blueprint with working examples. You'll need to clone, study, and customize it for your environment.

### Can I use this in production?

Yes! The architecture is production-ready and battle-tested at run.nycapphouse.com. However, you MUST:
- Generate your own secrets (never use example values)
- Review and customize all configurations
- Understand what each component does
- Implement proper backup and monitoring

### What's the difference between this and Authelia Admin Panel?

- **[Authelia Admin Panel](https://github.com/dustinnh/Authelia-Admin-Panel)**: Standalone Flask application for managing Authelia users (can be used with any Authelia setup)
- **Walled Garden**: Complete reference architecture with Caddy + Authelia + multiple services + documentation

They complement each other:
- The **Admin Panel** is a software product that can be used independently
- The **Walled Garden** is a complete architecture that includes the Admin Panel as one component
- Use Admin Panel alone if you already have Authelia
- Use Walled Garden for complete SSO gateway deployment from scratch

### How do I add a new service?

See [How-To: Add Services](docs/HOWTO-ADD-SERVICES.md) for step-by-step instructions. The process is:
1. Add service to docker-compose.yml (internal network only)
2. Add routing rule to Caddyfile
3. Add access control rule to Authelia config
4. Restart services

### Can I use LDAP instead of file-based users?

Yes! Authelia supports multiple authentication backends. See [Authelia Documentation](https://www.authelia.com/configuration/first-factor/ldap/) for LDAP configuration.

### Do I need a real domain name?

Yes, for production. Authelia's session cookies require a proper domain for SSO to work. For testing, you can use:
- Local DNS (edit /etc/hosts)
- Wildcard DNS services (*.example.com)
- Self-signed certificates (not recommended)

### What services are included?

The example deployment includes:
- Excalidraw (whiteboard)
- Portainer (container management)
- n8n (workflow automation)
- User Admin (authelia-file-admin)
- DNS Tools (custom troubleshooting)

You can add any service that works with reverse proxies.

## Contributing

Contributions are welcome! We're especially interested in:

- **Documentation improvements** - Clarify confusing sections, fix typos
- **Example integrations** - Add guides for popular services
- **Configuration examples** - Alternative setups (LDAP, Redis, etc.)
- **Bug fixes** - Corrections to example configurations
- **Screenshot updates** - Better visuals

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-addition`)
3. Make your changes
4. Test thoroughly (validate configs, check for secrets)
5. Commit (`git commit -am 'Add amazing addition'`)
6. Push to branch (`git push origin feature/amazing-addition`)
7. Open a Pull Request

**Important**: Never commit production secrets or identifying information. All PRs are reviewed for security.

## Troubleshooting

### Authentication Loop

**Symptom**: Redirects back and forth between Authelia and service

**Solution**: Check that `session.domain` in Authelia config is the **parent domain** (e.g., `example.com` not `auth.example.com`)

### SSL Certificate Errors

**Symptom**: Let's Encrypt rate limit or cert not issued

**Solution**: 
- Verify DNS is correct: `dig your-domain.com +short`
- Check Caddy logs: `docker compose logs caddy | grep -i acme`
- Ensure ports 80/443 are open: `sudo ufw status`

### Service Not Accessible

**Symptom**: 404 or 502 error when accessing service

**Solution**:
- Verify service is running: `docker compose ps`
- Check service logs: `docker compose logs service-name`
- Test internal connectivity: `docker compose exec caddy wget -O- http://service:port`

See [Full Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

## License

MIT License

Copyright (c) 2024 Dustin @ NYC App House

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**Built with** ❤️ **for the self-hosted community**

**Questions?** Open an issue or start a discussion!

**Like this project?** Give it a ⭐ on GitHub!
