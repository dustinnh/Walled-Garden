# Example Configurations

This directory contains **sanitized example configurations** for the Authelia Walled Garden. These are based on a production deployment but have been modified for security and generalization.

## ⚠️ CRITICAL SECURITY WARNING

**NEVER use these examples as-is in production!** All secrets, domains, and identifying information have been replaced with placeholders.

**Before deploying, you MUST**:
1. Generate your own secrets using `../scripts/generate-secrets.sh`
2. Replace all instances of `example.com` with your actual domain
3. Review and customize all configuration files
4. Test in a non-production environment first

## Configuration Files

### [docker-compose.yml](docker-compose.yml)
Complete Docker Compose stack configuration including:
- Caddy reverse proxy
- Authelia authentication server
- User management interface (authelia-file-admin)
- DNS tools
- Example services (Excalidraw, Portainer, n8n, Nexterm)

**Key placeholders to replace**:
- `${SECRET_KEY}` - Generate with `openssl rand -base64 32`
- `${AUDIT_HMAC_KEY}` - Generate with `openssl rand -base64 32`
- `${NEXTERM_ENCRYPTION_KEY}` - Generate with `openssl rand -hex 32`
- `example.com` - Your actual domain

### [Caddyfile](Caddyfile)
Caddy reverse proxy configuration with:
- Automatic HTTPS via Let's Encrypt
- Forward authentication to Authelia
- Multiple subdomain examples
- Service routing rules

**Key replacements**:
- `admin@example.com` - Your email for Let's Encrypt notifications
- All `example.com` references - Your actual domain

### [authelia-config.yml](authelia-config.yml)
Authelia authentication server configuration with:
- JWT and session secrets
- File-based user authentication
- Access control rules
- TOTP (2FA) settings

**Key placeholders**:
- `REPLACE_WITH_YOUR_JWT_SECRET_*` - Generate with `openssl rand -base64 64`
- `REPLACE_WITH_YOUR_SESSION_SECRET_*` - Generate with `openssl rand -base64 64`
- `REPLACE_WITH_YOUR_ENCRYPTION_KEY_*` - Generate with `openssl rand -base64 64`
- `example.com` - Your actual domain

### [.env.template](.env.template)
Environment variables template showing all required secrets and configuration options.

**Usage**:
```bash
cp .env.template .env
# Edit .env with your generated secrets
# Never commit .env to version control!
```

### [authelia-custom.css](authelia-custom.css) & [inject-custom-css.js](inject-custom-css.js)
Custom styling for Authelia login portal.

## Dashboard Files

### [dashboard/](dashboard/)
Static HTML/CSS/JS files for the application launcher dashboard:
- `index.html` - Main dashboard with service cards
- `admin.html` - User management interface (requires authelia-file-admin backend)
- `dns.html` - DNS troubleshooting tools interface

**Customization**:
- Update URLs in `index.html` to match your services
- Modify service cards to add/remove applications
- Customize styling to match your branding

## Service Implementations

### [dns-tools/](dns-tools/)
Flask application providing DNS troubleshooting utilities:
- `app.py` - Flask backend with whitelisted dig parameters
- `Dockerfile` - Container build instructions
- `requirements.txt` - Python dependencies

### [cockpit/](cockpit/)
Cockpit web console configuration for server management:
- `cockpit.conf` - Configuration for reverse proxy compatibility

## Quick Start

1. **Generate secrets**:
   ```bash
   cd ..
   ./scripts/generate-secrets.sh > secrets.txt
   ```

2. **Copy and configure**:
   ```bash
   cp .env.template .env
   # Edit .env with your secrets and domain
   # Edit all configuration files to replace example.com
   ```

3. **Validate configuration**:
   ```bash
   ../scripts/check-config.sh
   ```

4. **Deploy**:
   ```bash
   docker compose up -d
   ```

5. **Check logs**:
   ```bash
   docker compose logs -f
   ```

## Configuration Checklist

Before deploying to production:

- [ ] All secrets generated and replaced in configuration files
- [ ] All `example.com` references replaced with your actual domain
- [ ] Email address updated in Caddyfile for Let's Encrypt notifications
- [ ] Authelia access control rules reviewed and customized
- [ ] User database created with at least one admin user
- [ ] SMTP configured if enabling email notifications
- [ ] Configuration validated with `scripts/check-config.sh`
- [ ] Tested in non-production environment
- [ ] Backup strategy implemented
- [ ] Monitoring and log rotation configured

## Security Notes

**Production Secrets**:
- Generate unique secrets for each environment (dev, staging, production)
- Never reuse secrets across deployments
- Rotate secrets periodically (recommended: every 90 days)
- Store secrets securely (password manager, encrypted vault)

**Domain Configuration**:
- Ensure DNS records point to your server
- Use parent domain for Authelia session cookies (enables SSO across subdomains)
- Configure SSL/TLS properly (Caddy handles this automatically with Let's Encrypt)

**Access Control**:
- Review Authelia access control rules carefully
- Use `two_factor` policy for sensitive resources (admin panels, terminals)
- Test access control rules thoroughly before production deployment
- Create separate admin and regular user accounts

## Additional Resources

- **Main Documentation**: See [../docs/](../docs/) for comprehensive guides
- **Helper Scripts**: See [../scripts/](../scripts/) for automation tools
- **Troubleshooting**: See [../docs/PDR.md](../docs/PDR.md) for common issues and solutions
- **Official Docs**:
  - [Authelia Documentation](https://www.authelia.com/docs/)
  - [Caddy Documentation](https://caddyserver.com/docs/)
