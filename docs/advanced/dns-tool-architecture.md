# DNS Tool Box Architecture

## Overview

The DNS Tool Box is a web-based interface for running DNS queries using the `dig` command. It consists of a static frontend (HTML/JavaScript) and a Python Flask backend running in a Docker container.

## Two-Part System

### 1. Frontend (dns.html) - Served from Host via Caddy

**Location**: `/opt/authelia-stack/dashboard/dns.html` (on host filesystem)

**How it's served**:
- Caddy container mounts the dashboard directory as a volume:
  ```yaml
  volumes:
    - ./dashboard:/srv
  ```

**Caddy routing** (Caddyfile lines 110-114):
```caddyfile
handle {
    root * /srv
    try_files {path} /index.html
    file_server
}
```

**Access**:
- **URL**: https://example.com/dns.html
- **Authentication**: Protected by Authelia forward_auth
- **Available to**: All authenticated users

### 2. Backend (Python API) - Running in Docker Container

**Container Details**:
- **Name**: `dns-tools`
- **Image**: Built from `/opt/authelia-stack/dns-tools/`
- **Runtime**: Gunicorn with 4 workers
- **Port**: 5001 (internal only)
- **Network**: Internal Docker bridge network (no published ports)

**Files**:
```
/opt/authelia-stack/dns-tools/
├── app.py              # Flask application with dig wrapper
├── Dockerfile          # Container build instructions
└── requirements.txt    # Python dependencies
```

**Caddy routing** (Caddyfile lines 86-88):
```caddyfile
handle_path /api/dns/* {
    reverse_proxy dns-tools:5001
}
```

**API Endpoint**: https://example.com/api/dns/dig

## Request Flow

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTPS GET
         ▼
https://example.com/dns.html
         │
         ▼
┌─────────────────────────┐
│   Caddy Container       │
│   (ports 80/443)        │
└────────┬────────────────┘
         │ forward_auth check
         ▼
┌─────────────────────────┐
│  Authelia Container     │
│  (authentication)       │
└────────┬────────────────┘
         │ if authenticated ✓
         ▼
┌─────────────────────────┐
│   Caddy serves          │
│   /srv/dns.html         │
│   (from host volume)    │
└─────────────────────────┘
         │
         │ User fills form, clicks "Run Query"
         │ JavaScript POST request
         ▼
https://example.com/api/dns/dig
         │
         ▼
┌─────────────────────────┐
│   Caddy Container       │
│   reverse_proxy         │
└────────┬────────────────┘
         │ → dns-tools:5001
         ▼
┌─────────────────────────┐
│  dns-tools Container    │
│  Gunicorn + Flask       │
└────────┬────────────────┘
         │ subprocess.run()
         ▼
┌─────────────────────────┐
│   dig command           │
│   (bind9-dnsutils)      │
└────────┬────────────────┘
         │ DNS query results
         ▼
         JSON response
         │
         ▼
    Browser displays in
    terminal history window
```

## Security Model

### Network Isolation
- Backend container on isolated internal Docker network
- No direct internet access to port 5001
- All traffic flows through Caddy reverse proxy

### Authentication
- All requests authenticated via Authelia forward_auth
- Only `/auth*` and `/api/verify*` paths bypass authentication
- User context headers passed to backend: `Remote-User`, `Remote-Groups`, `Remote-Name`, `Remote-Email`

### Command Injection Protection
- **Whitelisted parameters only**: Record types, DNS servers, flags
- **Domain/IP validation**: Regex patterns prevent malicious input
- **No shell execution**: Uses `subprocess.run()` with array arguments (not shell=True)
- **Timeout protection**: 30-second hard limit on queries
- **Parameter validation**: Buffer sizes, timeouts, retries all range-checked

Example of secure command building (app.py):
```python
cmd = ['dig']  # Array, not shell string
if server != 'default' and server in ALLOWED_DNS_SERVERS:
    cmd.append(f'@{ALLOWED_DNS_SERVERS[server]}')
# ... build command safely
result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
```

## File Locations

### Frontend
```
/opt/authelia-stack/dashboard/
├── index.html          # Main dashboard with app cards
└── dns.html           # DNS Tool Box interface
```

### Backend
```
/opt/authelia-stack/dns-tools/
├── app.py             # Flask API with secure dig wrapper
├── Dockerfile         # Python 3.11-slim + bind9-dnsutils + Gunicorn
└── requirements.txt   # flask, flask-cors, gunicorn
```

### Configuration
```
/opt/authelia-stack/
├── docker-compose.yml  # Service orchestration (lines 39-44: dns-tools)
└── Caddyfile          # Routing rules (lines 86-88: DNS API proxy)
```

## Features Implemented

### Frontend (dns.html)
- **Tab-based UI**: Basic | Debug | Advanced
- **Multi-record selection**: Query multiple record types simultaneously (A + MX + TXT)
- **Preset buttons**: Common queries (A record, MX, trace, reverse, NS, TXT)
- **Advanced controls**: EDNS buffer size, timeout, retries
- **Terminal history**: Scrollable command history with timestamps
- **Output options**: Short, stats, answer-only, authority section
- **Query options**: Trace, TCP, no recursion, DNSSEC, reverse lookup

### Backend (app.py)
Supports all standard dig options:
- Record types: A, AAAA, MX, CNAME, TXT, NS, SOA, PTR, ANY, AXFR
- DNS servers: System default, Google (8.8.8.8), Cloudflare (1.1.1.1), Quad9 (9.9.9.9), OpenDNS
- Flags: +short, +trace, +tcp, +norecurse, +stats, +dnssec
- Section filters: +noall +answer, +authority, +additional
- Performance: +bufsize, +time, +tries
- Special modes: -x (reverse lookup)

## Making Changes

### Frontend Updates (No Container Rebuild)
```bash
# Edit the HTML file directly
sudo nano /opt/authelia-stack/dashboard/dns.html

# Changes are immediately available - just refresh browser
# (Caddy serves from mounted volume)
```

### Backend Updates (Requires Container Rebuild)
```bash
# Edit backend code
sudo nano /opt/authelia-stack/dns-tools/app.py

# Rebuild and restart container
cd /opt/authelia-stack
sudo docker compose build dns-tools
sudo docker compose up -d dns-tools

# Verify it's running
sudo docker compose ps dns-tools
sudo docker compose logs dns-tools
```

### Add New Dependencies
```bash
# Update requirements.txt
echo "new-package==1.0.0" | sudo tee -a /opt/authelia-stack/dns-tools/requirements.txt

# Rebuild container (will install new packages)
cd /opt/authelia-stack
sudo docker compose build dns-tools
sudo docker compose up -d dns-tools
```

## Why This Design?

### Advantages

1. **Easy frontend updates**: HTML/CSS/JS changes don't require Docker rebuilds
2. **Security**: Backend isolated on internal network, no direct access
3. **Dependency isolation**: dig and Python packages contained in Docker
4. **Scalability**: Gunicorn with 4 workers handles concurrent requests
5. **Single authentication point**: All traffic authenticated by Authelia
6. **No command injection**: Whitelisted parameters prevent shell attacks

### Trade-offs

1. **Frontend on host**: Must have sudo/root access to edit files in /opt/
2. **Backend changes slower**: Requires container rebuild (~30 seconds)
3. **Debugging**: Backend errors require checking container logs

## Monitoring & Troubleshooting

### Check Container Status
```bash
cd /opt/authelia-stack
sudo docker compose ps dns-tools
```

### View Logs
```bash
# Last 20 lines
sudo docker compose logs --tail=20 dns-tools

# Follow logs in real-time
sudo docker compose logs -f dns-tools

# Search for errors
sudo docker compose logs dns-tools | grep -i error
```

### Test Backend Directly
```bash
# Execute command inside container
docker compose exec dns-tools dig google.com +short

# Check Gunicorn is running
docker compose exec dns-tools ps aux | grep gunicorn
```

### Test API Endpoint
```bash
# From another container on same network
docker compose exec caddy curl http://dns-tools:5001/health

# Should return: {"status": "healthy"}
```

## Production Deployment Details

**Web Server**: Gunicorn 21.2.0
- 4 worker processes (sync workers)
- 60-second timeout per request
- Binds to 0.0.0.0:5001 (container internal)

**Dockerfile CMD**:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "60", "app:app"]
```

**Restart Policy**: `unless-stopped` (survives reboots)

## Related Documentation

- Main architecture: `/home/dust/walledgarden/CLAUDE.md`
- Feature planning: `/home/dust/walledgarden/dig-card.md`
- Authelia stack: `/opt/authelia-stack/`

---

**Last Updated**: 2025-11-18
**Version**: 2.0 (with Gunicorn, tabs, history, multi-select)
