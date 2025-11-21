# Authelia Walled Garden - Modular Plugin Architecture

Production-ready reference architecture for deploying an Authelia-based authentication gateway with a **modular plugin system** for easy service management.

**Version**: 2.0.0
**Status**: Production-Ready with Plugin System
**License**: MIT

## 🚀 What's New in 2.0

The Walled Garden now features a **complete plugin architecture** that transforms how you manage services:

- **📦 Modular Plugins**: Add/remove services without editing core files
- **🔧 Plugin Manager CLI**: Simple commands to enable/disable services
- **🏗️ Automatic Configuration**: Generate Docker Compose, Caddyfile, and dashboard from plugins
- **🎨 Custom Plugins**: Easy framework for adding your own services
- **⚡ Zero Downtime**: Hot-reload services without full restart

## What This Is

This repository contains a **complete reference architecture** for deploying a secure, SSO-enabled service gateway using:
- **Authelia** - Authentication and authorization server
- **Caddy** - Reverse proxy with automatic HTTPS
- **Docker Compose** - Service orchestration
- **Plugin System** - Modular service management
- **Multiple backend services** - Pre-built plugin library

**This is NOT** a software package or turnkey solution. It's a comprehensive guide and example implementation designed to be cloned, studied, and customized for your specific needs.

**Perfect for**:
- System administrators deploying Authelia
- DevOps engineers building authenticated service platforms
- Security engineers implementing SSO
- Homelab enthusiasts protecting self-hosted services
- Teams needing flexible service management

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Plugin System](#plugin-system)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Available Plugins](#available-plugins)
- [Creating Custom Plugins](#creating-custom-plugins)
- [Screenshots](#screenshots)
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

### Modular Plugin System
- **Plug-and-Play Services**: Enable/disable services with one command
- **Auto-Configuration**: Generates all config files from plugin manifests
- **Plugin Types**: Docker, API, Static, External, Hybrid
- **Plugin Manager CLI**: Simple interface for plugin management
- **Custom Plugins**: Easy framework for adding your own services
- **Version Management**: Each plugin independently versioned
- **Dependency Resolution**: Automatic handling of plugin dependencies

### Production-Ready Components
- **Reverse Proxy**: Caddy with automatic certificate management
- **Authentication Gateway**: Authelia with file-based or LDAP backends
- **User Management**: Web-based admin interface (core plugin)
- **DNS Tools**: Network diagnostic utilities (core plugin)
- **Service Discovery**: Dynamic routing configuration
- **Health Monitoring**: Container health checks
- **Backup & Recovery**: Documented procedures

## Architecture

### Plugin-Based Architecture

```
┌─────────────────────────────────────────┐
│           Plugin System                 │
├─────────────────────────────────────────┤
│  Core Plugins (Always Enabled)          │
│  ├─ DNS Tools                           │
│  └─ User Admin                          │
├─────────────────────────────────────────┤
│  Available Plugins (Optional)           │
│  ├─ Excalidraw                          │
│  ├─ Portainer                           │
│  ├─ n8n Automation                      │
│  ├─ IT Tools                            │
│  └─ ... (20+ more)                      │
├─────────────────────────────────────────┤
│  Custom Plugins (User Created)          │
│  └─ Your Services Here                  │
└─────────────────────────────────────────┘
              ↓
         Build System
              ↓
    ┌──────────────────┐
    │ Generated Files  │
    ├──────────────────┤
    │ • index.html     │
    │ • docker-compose │
    │ • Caddyfile      │
    │ • .env template  │
    └──────────────────┘
```

### Authentication Flow

1. User requests `https://example.com/service/`
2. Caddy performs `forward_auth` check to Authelia
3. Authelia validates session
4. Authenticated → Forward to service
5. Not authenticated → Redirect to login

## Plugin System

### How It Works

1. **Plugin Manifests**: Each service has a `plugin.json` describing its configuration
2. **Plugin Config**: `plugins-config.json` lists enabled plugins
3. **Build System**: Python scripts generate all configuration from plugins
4. **Deployment**: Standard `docker-compose up` with generated files

### Plugin Structure

```
plugins/
├── core/                  # Essential plugins
│   ├── dns-tools/
│   │   ├── plugin.json   # Plugin manifest
│   │   └── ui/           # UI files
│   └── user-admin/
├── available/             # Optional plugins
│   ├── excalidraw/
│   ├── portainer/
│   └── ... (20+ more)
└── custom/               # Your plugins
```

### Managing Plugins

```bash
# List all plugins
./scripts/plugin-manager.py list

# Enable a plugin
./scripts/plugin-manager.py enable available/n8n

# Disable a plugin
./scripts/plugin-manager.py disable available/portainer

# Get plugin info
./scripts/plugin-manager.py info available/excalidraw

# Validate configuration
./scripts/plugin-manager.py validate
```

### Building Configuration

```bash
# Generate all configuration files
./scripts/build.py

# This creates:
# - output/index.html          (dashboard)
# - output/docker-compose.yml  (services)
# - output/Caddyfile          (routing)
# - output/.env.template      (variables)
# - output/dashboard/         (UI files from plugins)
```

### Dashboard Architecture

The dashboard is dynamically generated from your enabled plugins:

1. **Plugin UI Files**: Each plugin can provide HTML interfaces (stored in `plugins/[name]/ui/`)
2. **Shared Assets**: Common CSS and resources (stored in `dashboard/`)
3. **Generated Dashboard**: Main page built from plugin manifests showing enabled services
4. **Build Process**: Combines everything into `output/dashboard/` for deployment

Core plugins provide essential interfaces:
- **DNS Tools** (`/dns.html`): Network diagnostic utilities
- **User Admin** (`/admin.html`): Authelia user management

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Domain name with DNS pointing to your server
- Python 3.7+ (for build scripts)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/walledgarden.git
cd walledgarden

# 2. Configure your domain
edit plugins-config.json  # Set your domain

# 3. Choose your plugins
./scripts/plugin-manager.py list
./scripts/plugin-manager.py enable available/YOUR_CHOICE

# 4. Build configuration
./scripts/build.py

# 5. Generate secrets
cd output
../scripts/generate-secrets.sh > .env

# 6. Configure Authelia
cp ../examples/authelia-config.yml authelia/configuration.yml
# Edit with your settings

# 7. Deploy
docker-compose up -d

# 8. Access your services
# https://yourdomain.com
```

## Documentation

### Core Documentation

- [Plugin Schema Documentation](plugins/PLUGIN_SCHEMA.md) - Complete plugin manifest reference
- [Plugin Development Guide](PLUGIN_DEVELOPMENT.md) - Create your own plugins
- [Architecture Overview](docs/ARCHITECTURE.md) - System design details
- [Deployment Guide](docs/PDR.md) - Production deployment reference
- [How to Add Services](docs/HOWTO-ADD-SERVICES.md) - Service integration guide

### Plugin Documentation

- [Available Plugins Catalog](plugins/available/README.md) - List of pre-built plugins
- [Core Plugins Guide](plugins/core/README.md) - Essential plugin documentation
- [Custom Plugin Examples](plugins/custom/README.md) - Example custom plugins

## Available Plugins

### Core Plugins (Always Enabled)

| Plugin | Description | Icon |
|--------|-------------|------|
| DNS Tools | Network diagnostic utilities | 🔍 |
| User Admin | Authelia user management interface | 👤 |

### Popular Available Plugins

| Plugin | Description | Category | Icon |
|--------|-------------|----------|------|
| Excalidraw | Collaborative whiteboard | Productivity | ✏️ |
| Portainer | Docker container management | Development | 🐳 |
| n8n | Workflow automation platform | Productivity | 🔄 |
| IT Tools | Developer utilities collection | Utilities | 🔧 |
| Open WebUI | LLM chat interface | Productivity | 🤖 |
| Cockpit | Server administration | Monitoring | 🖥️ |
| Homepage | Customizable dashboard | Utilities | 🏠 |
| Uptime Kuma | Service monitoring | Monitoring | 📊 |
| Filebrowser | Web file manager | Utilities | 📁 |
| Netdata | Real-time monitoring | Monitoring | 📈 |

[View all 20+ available plugins →](plugins/available/)

## Creating Custom Plugins

### Quick Example

Create a simple notes plugin:

```json
// plugins/custom/my-notes/plugin.json
{
  "id": "my-notes",
  "name": "My Notes",
  "version": "1.0.0",
  "description": "Personal note-taking app",
  "icon": "📝",
  "category": "productivity",
  "type": "docker",

  "docker": {
    "enabled": true,
    "image": "standardnotes/web",
    "internalPort": 3000
  },

  "routing": {
    "type": "path",
    "path": "/notes"
  },

  "authentication": {
    "required": true,
    "policy": "one_factor"
  }
}
```

Enable and deploy:

```bash
./scripts/plugin-manager.py enable custom/my-notes
./scripts/build.py
cd output && docker-compose up -d
```

Your app is now available at `https://yourdomain.com/notes`!

[Full Plugin Development Guide →](PLUGIN_DEVELOPMENT.md)

## Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Modular dashboard generated from enabled plugins*

### Plugin Manager
![Plugin Manager](screenshots/plugin-manager.png)
*CLI tool for managing plugins*

### DNS Tools
![DNS Tools](screenshots/dns-tools.png)
*Built-in network diagnostic utilities*

### User Admin
![User Admin](screenshots/user-admin.png)
*Web-based Authelia user management*

## Migration from v1.x

If you're using the previous version without plugins:

1. **Backup your configuration** (especially Authelia config and users)
2. **Install the plugin system** (clone new version)
3. **Enable equivalent plugins** for your existing services
4. **Run build system** to generate new configuration
5. **Compare configurations** and migrate custom settings
6. **Deploy with new configuration**

[Detailed Migration Guide →](docs/MIGRATION.md)

## Contributing

### Ways to Contribute

1. **Create Plugins**: Develop and share new service plugins
2. **Improve Documentation**: Fix typos, add examples, clarify instructions
3. **Report Issues**: Found a bug? Let us know!
4. **Share Configurations**: Submit your working configurations as examples

### Plugin Contribution

To submit a new plugin:

1. Create plugin in `plugins/available/YOUR_PLUGIN/`
2. Follow the [Plugin Development Guide](PLUGIN_DEVELOPMENT.md)
3. Test thoroughly
4. Submit pull request with:
   - Plugin files
   - Documentation
   - Example configuration

### Guidelines

- Keep security as top priority
- Follow existing code style
- Test before submitting
- Document your changes
- One feature per pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/walledgarden/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/walledgarden/discussions)
- **Documentation**: [Full Documentation](docs/)
- **Examples**: [Example Configurations](examples/)

## Roadmap

### Coming Soon

- [ ] Plugin marketplace/registry
- [ ] Web-based plugin manager UI
- [ ] Automatic plugin updates
- [ ] Plugin templates generator
- [ ] Integration testing framework
- [ ] Multi-instance plugin support
- [ ] Plugin resource monitoring
- [ ] Backup/restore for plugin data

## Related Projects

- [Authelia](https://www.authelia.com/) - The authentication server
- [Caddy](https://caddyserver.com/) - The reverse proxy
- [authelia-file-admin](https://github.com/yourusername/authelia-file-admin) - User management interface

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Authelia team for the excellent authentication server
- Caddy team for the fantastic reverse proxy
- All plugin contributors
- The self-hosting community

---

**Ready to secure your services with a modular architecture?** 🚀

Start with `./scripts/build.py` and have your walled garden running in minutes!