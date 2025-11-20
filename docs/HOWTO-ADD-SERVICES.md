# How-To Guide: Adding Services to the Walled Garden

Quick reference for adding new Docker containers, web pages, and routes to the run.nycapphouse.com setup.

**Last Updated**: 2025-11-18

---

## Table of Contents

1. [Adding a New Docker Container](#1-adding-a-new-docker-container)
2. [Adding a New Static Page](#2-adding-a-new-static-page)
3. [Adding a New Domain/Subdomain](#3-adding-a-new-domainsubdomain)
4. [Adding a Custom Python API](#4-adding-a-custom-python-api)
5. [Adding a Dashboard Card](#5-adding-a-dashboard-card)
6. [Configuring Authentication Rules](#6-configuring-authentication-rules)
7. [Common Troubleshooting](#7-common-troubleshooting)
8. [Quick Command Reference](#8-quick-command-reference)

---

## 1. Adding a New Docker Container

### Step-by-Step Process

#### 1.1 Edit docker-compose.yml

```bash
sudo nano /opt/authelia-stack/docker-compose.yml
```

Add your new service:

```yaml
  myservice:
    image: myorg/myapp:latest
    container_name: myservice
    restart: unless-stopped
    ports: []  # Leave empty - use internal network only
    environment:
      - MYVAR=value
    volumes:
      - myservice_data:/data
    networks:
      - internal
```

**Important**:
- Always use the `internal` network
- Never publish ports to host (keep `ports: []` empty)
- Use `restart: unless-stopped` for automatic startup

#### 1.2 Add Named Volume (if needed)

At the bottom of `docker-compose.yml`:

```yaml
volumes:
  caddy_data:
  caddy_config:
  portainer_data:
  n8n_data:
  nexterm_data:
  myservice_data:  # Add your new volume
```

#### 1.3 Add Caddy Route

```bash
sudo nano /opt/authelia-stack/Caddyfile
```

Inside the `run.nycapphouse.com` block, after the `forward_auth` section:

```caddyfile
run.nycapphouse.com {
    encode gzip

    # ... existing auth bypass rules ...

    handle {
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com/auth/
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }

        # Add your new route
        handle_path /myapp/* {
            reverse_proxy myservice:8080
        }

        # ... existing routes ...
    }
}
```

**Route Options**:
- `handle_path /myapp/*` - Strips `/myapp/` prefix before proxying
- `handle /myapp*` - Keeps full path, you must use `uri strip_prefix /myapp`
- `reverse_proxy myservice:PORT` - Use container name and internal port

#### 1.4 Deploy

```bash
cd /opt/authelia-stack

# Pull/build images
sudo docker compose pull myservice
# OR if using build:
sudo docker compose build myservice

# Start the new service
sudo docker compose up -d myservice

# Restart Caddy to load new routes
sudo docker compose restart caddy

# Check status
sudo docker compose ps myservice
sudo docker compose logs -f myservice
```

#### 1.5 Test Access

```bash
# From browser:
https://run.nycapphouse.com/myapp/

# From command line:
curl -I https://run.nycapphouse.com/myapp/
```

---

## 2. Adding a New Static Page

### 2.1 Create HTML File

```bash
sudo nano /opt/authelia-stack/dashboard/mypage.html
```

Use this template:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My Page - NYC App House</title>
    <style>
      body {
        font-family: system-ui, sans-serif;
        margin: 0;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
      }
      .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        padding: 2.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      }
      .back-link {
        text-decoration: none;
        color: #667eea;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border: 2px solid #667eea;
        border-radius: 6px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <a href="/" class="back-link">← Back to Dashboard</a>
      <h1>My Page</h1>
      <p>Content goes here...</p>
    </div>
  </body>
</html>
```

### 2.2 Access the Page

No deployment needed! Caddy automatically serves files from `/srv`:

```
https://run.nycapphouse.com/mypage.html
```

### 2.3 Add to Dashboard

See [Section 5: Adding a Dashboard Card](#5-adding-a-dashboard-card)

---

## 3. Adding a New Domain/Subdomain

### 3.1 Configure DNS

Point your subdomain to your server IP:

```
A Record: myapp.nycapphouse.com → YOUR_SERVER_IP
```

### 3.2 Add Caddyfile Block

```bash
sudo nano /opt/authelia-stack/Caddyfile
```

Add a new site block:

```caddyfile
myapp.nycapphouse.com {
    encode gzip

    forward_auth authelia:9091 {
        uri /api/verify?rd=https://run.nycapphouse.com/auth/
        copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    }

    reverse_proxy myservice:8080
}
```

### 3.3 Reload Caddy

```bash
cd /opt/authelia-stack
sudo docker compose restart caddy
```

### 3.4 Wait for SSL Certificate

Caddy automatically requests a Let's Encrypt certificate. Check logs:

```bash
sudo docker compose logs -f caddy | grep -i acme
```

**SSL Troubleshooting**:
- DNS must be propagated: `dig myapp.nycapphouse.com +short`
- Port 80 must be open: `sudo ufw status`
- Rate limits: 5 failures per hour per domain

---

## 4. Adding a Custom Python API

### 4.1 Create Directory Structure

```bash
cd /opt/authelia-stack
sudo mkdir my-api
cd my-api
```

### 4.2 Create app.py

```bash
sudo nano app.py
```

```python
#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/hello', methods=['GET'])
def hello():
    # User context from Authelia
    user = request.headers.get('Remote-User', 'Unknown')
    groups = request.headers.get('Remote-Groups', '')

    return jsonify({
        'message': f'Hello {user}!',
        'groups': groups.split(',') if groups else []
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
```

### 4.3 Create requirements.txt

```bash
sudo nano requirements.txt
```

```
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
```

### 4.4 Create Dockerfile

```bash
sudo nano Dockerfile
```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5002

CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "4", "--timeout", "60", "app:app"]
```

### 4.5 Add to docker-compose.yml

```bash
sudo nano /opt/authelia-stack/docker-compose.yml
```

```yaml
  my-api:
    build: ./my-api
    container_name: my-api
    restart: unless-stopped
    networks:
      - internal
```

### 4.6 Add Caddy Route

```bash
sudo nano /opt/authelia-stack/Caddyfile
```

```caddyfile
# Inside run.nycapphouse.com handle block:
handle_path /api/myapi/* {
    reverse_proxy my-api:5002
}
```

### 4.7 Deploy

```bash
cd /opt/authelia-stack
sudo docker compose build my-api
sudo docker compose up -d my-api
sudo docker compose restart caddy

# Test
curl https://run.nycapphouse.com/api/myapi/health
```

---

## 5. Adding a Dashboard Card

### 5.1 Edit index.html

```bash
sudo nano /opt/authelia-stack/dashboard/index.html
```

Find the `.grid` section and add your card:

```html
<div class="grid">
  <!-- Existing cards... -->

  <a href="/myapp/" class="card">
    <div class="icon">🚀</div>
    <h3>My App</h3>
    <p>Description of what this app does</p>
  </a>
</div>
```

### 5.2 Card Icon Ideas

Common emoji icons:
- 🔍 Search/lookup tools
- 📊 Data/analytics
- 🛠️ Admin/settings
- 💻 Development tools
- 📝 Documentation
- 🔐 Security tools
- 📱 Apps
- 🎨 Design tools
- 🔄 Automation
- 📈 Monitoring

### 5.3 Card Styles

The CSS is already defined. Cards automatically:
- Display in responsive grid
- Show hover effects
- Scale on hover
- Use gradient purple theme

No additional CSS needed!

---

## 6. Configuring Authentication Rules

### 6.1 Bypass Authentication (Public Access)

To make a path accessible without login, add to the `@authelia` matcher:

```caddyfile
run.nycapphouse.com {
    encode gzip

    @authelia {
        path /auth*
        path /static/*
        path /api/verify*
        path /api/authz/*
        path /locales/*
        path /public-page*     # Add your public path
    }
    handle @authelia {
        reverse_proxy authelia:9091
    }

    # ... rest of config ...
}
```

**Warning**: Only use for truly public content. Most paths should require auth!

### 6.2 Admin-Only Access

The API must check the `Remote-Groups` header:

```python
@app.route('/admin-only', methods=['GET'])
def admin_only():
    groups = request.headers.get('Remote-Groups', '')

    if 'admins' not in groups.split(','):
        return jsonify({'error': 'Admin access required'}), 403

    return jsonify({'message': 'Admin data here'})
```

Backend services receive these headers automatically from Caddy:
- `Remote-User`: Username
- `Remote-Groups`: Comma-separated list (e.g., "admins,users")
- `Remote-Name`: Display name
- `Remote-Email`: Email address

### 6.3 Group-Based Access

Create custom groups in Authelia:

```bash
sudo nano /opt/authelia-stack/authelia/users_database.yml
```

```yaml
users:
  alice:
    displayname: "Alice Smith"
    password: "$argon2id$..."
    email: "alice@example.com"
    groups:
      - admins
      - developers

  bob:
    displayname: "Bob Jones"
    password: "$argon2id$..."
    email: "bob@example.com"
    groups:
      - users
      - viewers
```

Then in your API:

```python
groups = request.headers.get('Remote-Groups', '').split(',')

if 'developers' in groups:
    # Developer access
    pass
```

---

## 7. Common Troubleshooting

### 7.1 Service Not Starting

```bash
# Check container status
sudo docker compose ps

# View logs
sudo docker compose logs -f servicename

# Check for port conflicts
sudo docker compose logs servicename | grep -i "bind\|port\|address"
```

### 7.2 Cannot Access Service (502 Bad Gateway)

**Check 1**: Is the container running?
```bash
sudo docker compose ps servicename
```

**Check 2**: Is it on the internal network?
```bash
sudo docker inspect servicename | grep -A 5 Networks
```

**Check 3**: Test internal connectivity
```bash
sudo docker compose exec caddy wget -O- http://servicename:PORT/health
```

**Check 4**: Check Caddy logs
```bash
sudo docker compose logs caddy | grep -i error
```

### 7.3 Authentication Not Working

**Check 1**: Is forward_auth configured?
```bash
sudo cat /opt/authelia-stack/Caddyfile | grep -A 3 forward_auth
```

**Check 2**: Is Authelia running?
```bash
sudo docker compose ps authelia
sudo docker compose logs authelia | grep -i error
```

**Check 3**: Clear browser cookies
- Delete cookies for `.nycapphouse.com`
- Try incognito/private mode

**Check 4**: Check Authelia session domain
```bash
sudo cat /opt/authelia-stack/authelia/configuration.yml | grep -i "domain:"
```

Should be parent domain: `nycapphouse.com` (not `run.nycapphouse.com`)

### 7.4 SSL Certificate Issues

**Check DNS**:
```bash
dig yourdomain.nycapphouse.com +short
# Should return your server IP
```

**Check Caddy logs**:
```bash
sudo docker compose logs caddy | grep -i acme
```

**Check firewall**:
```bash
sudo ufw status
# Must show: 80/tcp ALLOW and 443/tcp ALLOW
```

**Manually trigger renewal**:
```bash
sudo docker compose restart caddy
```

### 7.5 Volume Permission Issues

If a container can't write to a volume:

```bash
# Check volume permissions
sudo ls -la /opt/authelia-stack/

# Fix ownership (if needed)
sudo chown -R $USER:$USER /opt/authelia-stack/dashboard/
```

For named volumes, check inside container:
```bash
sudo docker compose exec servicename ls -la /data
```

---

## 8. Quick Command Reference

### Container Management

```bash
# Navigate to stack directory
cd /opt/authelia-stack

# View all containers
sudo docker compose ps

# Start specific service
sudo docker compose up -d servicename

# Stop specific service
sudo docker compose stop servicename

# Restart service
sudo docker compose restart servicename

# Rebuild and restart
sudo docker compose build servicename
sudo docker compose up -d servicename

# Remove service (keeps volumes)
sudo docker compose down servicename

# View logs (live)
sudo docker compose logs -f servicename

# View last 50 lines
sudo docker compose logs --tail=50 servicename

# Execute command in container
sudo docker compose exec servicename bash
sudo docker compose exec servicename ls -la /app
```

### File Editing

```bash
# Edit Caddyfile
sudo nano /opt/authelia-stack/Caddyfile

# Edit docker-compose.yml
sudo nano /opt/authelia-stack/docker-compose.yml

# Edit dashboard page
sudo nano /opt/authelia-stack/dashboard/index.html

# Edit Authelia users
sudo nano /opt/authelia-stack/authelia/users_database.yml
```

### Apply Changes

```bash
# After Caddyfile changes
sudo docker compose restart caddy

# After docker-compose.yml changes
sudo docker compose up -d

# After Authelia config changes
sudo docker compose restart authelia

# After dashboard HTML changes
# No restart needed - just refresh browser
```

### Testing

```bash
# Test internal service connectivity
sudo docker compose exec caddy wget -O- http://servicename:PORT/

# Test external HTTPS
curl -I https://run.nycapphouse.com/myapp/

# Test with authentication
curl -H "Cookie: session=..." https://run.nycapphouse.com/api/myapi/

# Check DNS
dig myapp.nycapphouse.com +short

# Check firewall
sudo ufw status

# Check listening ports
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Logs & Debugging

```bash
# View all errors
sudo docker compose logs | grep -i error

# Search logs for specific text
sudo docker compose logs servicename | grep "search term"

# Follow logs with grep filter
sudo docker compose logs -f caddy | grep -i acme

# Export logs to file
sudo docker compose logs > /tmp/stack-logs.txt

# Check Docker daemon logs
sudo journalctl -u docker -n 50
```

---

## Common Patterns Cheat Sheet

### Pattern 1: Simple Web App (No Auth Required)

```yaml
# docker-compose.yml
  webapp:
    image: myapp:latest
    networks:
      - internal
```

```caddyfile
# Caddyfile - in @authelia matcher
path /public-app*
```

```caddyfile
# Caddyfile - bypass auth
handle /public-app* {
    reverse_proxy webapp:80
}
```

### Pattern 2: Protected Web App

```yaml
# docker-compose.yml
  webapp:
    image: myapp:latest
    networks:
      - internal
```

```caddyfile
# Caddyfile - inside authenticated handle block
handle_path /webapp/* {
    reverse_proxy webapp:80
}
```

### Pattern 3: Protected API (All Users)

```yaml
# docker-compose.yml
  myapi:
    build: ./myapi
    networks:
      - internal
```

```caddyfile
# Caddyfile - inside authenticated handle block
handle_path /api/myapi/* {
    reverse_proxy myapi:5000
}
```

### Pattern 4: Admin-Only API

```yaml
# docker-compose.yml
  adminapi:
    build: ./adminapi
    networks:
      - internal
```

```caddyfile
# Caddyfile - inside authenticated handle block
handle_path /api/admin/* {
    reverse_proxy adminapi:5000
}
```

```python
# In adminapi/app.py
groups = request.headers.get('Remote-Groups', '')
if 'admins' not in groups.split(','):
    return jsonify({'error': 'Forbidden'}), 403
```

### Pattern 5: Subdomain App

```yaml
# docker-compose.yml
  coolapp:
    image: coolapp:latest
    networks:
      - internal
```

```caddyfile
# Caddyfile - new site block
coolapp.nycapphouse.com {
    encode gzip
    forward_auth authelia:9091 {
        uri /api/verify?rd=https://run.nycapphouse.com/auth/
        copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    }
    reverse_proxy coolapp:8080
}
```

### Pattern 6: App with Persistent Data

```yaml
# docker-compose.yml
  dataapp:
    image: dataapp:latest
    volumes:
      - dataapp_data:/app/data
    networks:
      - internal

volumes:
  dataapp_data:
```

### Pattern 7: App with Config from Host

```yaml
# docker-compose.yml
  configapp:
    image: configapp:latest
    volumes:
      - ./configapp/config.yml:/app/config.yml:ro
    networks:
      - internal
```

```bash
# Create config directory
sudo mkdir /opt/authelia-stack/configapp
sudo nano /opt/authelia-stack/configapp/config.yml
```

---

## Template: Full New Service

Use this as a complete template when adding a new service:

### 1. Create service files (for custom build)

```bash
cd /opt/authelia-stack
sudo mkdir myservice
cd myservice
sudo nano Dockerfile
sudo nano app.py
sudo nano requirements.txt
```

### 2. Add to docker-compose.yml

```yaml
  myservice:
    build: ./myservice  # OR: image: org/myservice:latest
    container_name: myservice
    restart: unless-stopped
    environment:
      - VAR1=value1
    volumes:
      - myservice_data:/data
    networks:
      - internal

# At bottom:
volumes:
  myservice_data:
```

### 3. Add to Caddyfile

```caddyfile
run.nycapphouse.com {
    encode gzip

    # ... existing @authelia bypass rules ...

    handle {
        forward_auth authelia:9091 {
            uri /api/verify?rd=https://run.nycapphouse.com/auth/
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }

        # Your new service
        handle_path /myservice/* {
            reverse_proxy myservice:8080
        }

        # ... existing routes ...
    }
}
```

### 4. Add dashboard card

```bash
sudo nano /opt/authelia-stack/dashboard/index.html
```

```html
<a href="/myservice/" class="card">
  <div class="icon">🎯</div>
  <h3>My Service</h3>
  <p>Does awesome things</p>
</a>
```

### 5. Deploy

```bash
cd /opt/authelia-stack
sudo docker compose build myservice
sudo docker compose up -d myservice
sudo docker compose restart caddy
```

### 6. Test

```bash
sudo docker compose ps myservice
sudo docker compose logs -f myservice
curl -I https://run.nycapphouse.com/myservice/
```

---

## Safety Checklist

Before deploying to production:

- [ ] Service is on `internal` network (no published ports)
- [ ] Sensitive endpoints require authentication (via forward_auth)
- [ ] Admin endpoints check `Remote-Groups` header
- [ ] No hardcoded secrets (use environment variables)
- [ ] SSL certificate obtained (check Caddy logs)
- [ ] Service has `restart: unless-stopped`
- [ ] Logs show no errors: `sudo docker compose logs servicename`
- [ ] Health endpoint responds: `curl https://run.nycapphouse.com/service/health`
- [ ] Authentication tested (login required)
- [ ] Volume permissions correct (if using bind mounts)

---

## Related Documentation

- **Architecture Diagrams**: `/home/dust/walledgarden/walled-garden-architecture.mermaid.md`
- **DNS Tool Details**: `/home/dust/walledgarden/dns-tool-architecture.md`
- **Main Architecture**: `/home/dust/walledgarden/CLAUDE.md`
- **Original PDR**: `/home/dust/walledgarden/Authelia-Walled-Garden-PDR.md`

---

**Pro Tips:**

1. Always test in dev first if possible
2. Keep Caddy logs open when testing: `sudo docker compose logs -f caddy`
3. Use health endpoints for monitoring
4. Document your changes in comments
5. Backup before major changes: `sudo tar -czf backup.tar.gz /opt/authelia-stack/`
6. Use `docker compose config` to validate docker-compose.yml syntax
7. Test with curl before testing in browser
8. Check DNS propagation before expecting SSL to work

---

**Need Help?**

Common issues and their solutions are in [Section 7: Troubleshooting](#7-common-troubleshooting)

For architecture questions, refer to the Mermaid diagrams showing request flows and service dependencies.
