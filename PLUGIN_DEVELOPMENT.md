# Plugin Development Guide

This guide will walk you through creating custom plugins for the Walled Garden system.

## Table of Contents

1. [Overview](#overview)
2. [Plugin Types](#plugin-types)
3. [Creating Your First Plugin](#creating-your-first-plugin)
4. [Plugin Manifest Structure](#plugin-manifest-structure)
5. [Routing Configuration](#routing-configuration)
6. [Authentication Integration](#authentication-integration)
7. [Testing Your Plugin](#testing-your-plugin)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

## Overview

The Walled Garden plugin system allows you to easily add new services to your deployment without modifying core files. Plugins are self-contained packages that include:

- A manifest file (`plugin.json`) describing the plugin
- Optional UI files (HTML, CSS, JavaScript)
- Optional API handlers
- Configuration templates

## Plugin Types

### 1. Docker Service Plugin

Most common type - deploys a containerized application.

**Use for:** Web applications, databases, monitoring tools

**Example:** Nextcloud, GitLab, Grafana

### 2. API Service Plugin

Provides backend API endpoints without a full container.

**Use for:** Custom APIs, webhooks, integrations

**Example:** Custom authentication handlers, webhook receivers

### 3. Static Plugin

Serves static HTML/CSS/JS files.

**Use for:** Documentation sites, single-page applications

**Example:** Documentation wikis, status pages

### 4. External Plugin

Links to external services without local deployment.

**Use for:** SaaS services, external tools

**Example:** GitHub, Google Workspace, external APIs

### 5. Hybrid Plugin

Combines multiple types (Docker + API + custom UI).

**Use for:** Complex applications with multiple components

**Example:** DNS tools, User admin interface

## Creating Your First Plugin

Let's create a simple note-taking application plugin.

### Step 1: Create Plugin Directory

```bash
mkdir -p plugins/custom/my-notes
cd plugins/custom/my-notes
```

### Step 2: Create Plugin Manifest

Create `plugin.json`:

```json
{
  "id": "my-notes",
  "name": "My Notes",
  "version": "1.0.0",
  "description": "Simple note-taking application",
  "author": "Your Name",
  "icon": "📝",
  "category": "productivity",
  "type": "docker",

  "ui": {
    "dashboard": {
      "visible": true,
      "requiresAdmin": false,
      "order": 100
    }
  },

  "routing": {
    "type": "path",
    "path": "/notes",
    "stripPath": false
  },

  "docker": {
    "enabled": true,
    "image": "standardnotes/web",
    "tag": "latest",
    "containerName": "my-notes",
    "internalPort": 3000,
    "environment": {
      "PORT": "3000"
    },
    "volumes": [
      {
        "type": "named",
        "source": "notes_data",
        "target": "/var/lib/notes"
      }
    ],
    "networks": ["internal"]
  },

  "authentication": {
    "required": true,
    "policy": "one_factor"
  },

  "storage": {
    "persistent": true,
    "volumes": [
      {
        "name": "notes_data",
        "path": "/var/lib/notes"
      }
    ]
  }
}
```

### Step 3: Enable the Plugin

```bash
# Add to plugins-config.json
./scripts/plugin-manager.py enable custom/my-notes

# Or manually edit plugins-config.json and add:
"custom/my-notes" to the "enabled" array
```

### Step 4: Build Configuration

```bash
./scripts/build.py
```

This generates:
- `output/index.html` - Dashboard with your plugin
- `output/docker-compose.yml` - Docker service definition
- `output/Caddyfile` - Routing configuration

### Step 5: Deploy

```bash
cd output
docker-compose up -d
```

Your plugin is now accessible at `https://example.com/notes`!

## Plugin Manifest Structure

### Essential Fields

```json
{
  "id": "unique-identifier",        // Required: Unique plugin ID
  "name": "Display Name",            // Required: Human-readable name
  "version": "1.0.0",                // Required: Semantic version
  "type": "docker",                  // Required: Plugin type
  "description": "What it does",     // Required: Brief description
  "icon": "🎯",                      // Required: Emoji or icon
  "category": "productivity"         // Required: Category for organization
}
```

### UI Configuration

```json
"ui": {
  "dashboard": {
    "visible": true,               // Show on dashboard
    "requiresAdmin": false,        // Only visible to admins
    "order": 10                    // Display order (lower = earlier)
  },
  "customPages": [
    {
      "path": "/custom",           // URL path
      "file": "ui/custom.html",    // File to serve
      "requiresAdmin": true        // Access control
    }
  ]
}
```

### Docker Configuration

```json
"docker": {
  "enabled": true,
  "image": "nginx",                // Docker image
  "tag": "latest",                 // Image tag
  "containerName": "my-nginx",    // Container name
  "internalPort": 80,             // Port inside container
  "environment": {                 // Environment variables
    "KEY": "value"
  },
  "volumes": [                     // Volume mounts
    {
      "type": "named",             // "named" or "bind"
      "source": "data",            // Volume/path name
      "target": "/data"            // Mount point in container
    }
  ],
  "healthcheck": {                 // Health check configuration
    "test": "curl -f http://localhost/health",
    "interval": "30s",
    "timeout": "10s",
    "retries": 3
  }
}
```

## Routing Configuration

### Path-Based Routing

Traffic goes to `example.com/path`:

```json
"routing": {
  "type": "path",
  "path": "/myapp",
  "stripPath": true    // Remove /myapp before proxying
}
```

### Subdomain Routing

Traffic goes to `subdomain.example.com`:

```json
"routing": {
  "type": "subdomain",
  "subdomain": "myapp",
  "additionalDomains": ["myapp-api", "myapp-cdn"]
}
```

### Both Path and Subdomain

Accessible via both methods:

```json
"routing": {
  "type": "both",
  "subdomain": "myapp",
  "path": "/myapp"
}
```

### Custom Headers

Add headers to proxied requests:

```json
"routing": {
  "type": "path",
  "path": "/api",
  "headers": {
    "X-Custom-Header": "value",
    "X-API-Version": "v2"
  }
}
```

## Authentication Integration

### Basic Authentication

All requests require authentication:

```json
"authentication": {
  "required": true,
  "policy": "one_factor"    // or "two_factor" for 2FA
}
```

### Group-Based Access

Restrict to specific groups:

```json
"authentication": {
  "required": true,
  "policy": "one_factor",
  "requiredGroups": ["admins", "developers"]
}
```

### Bypass Paths

Some paths don't require auth:

```json
"authentication": {
  "required": true,
  "policy": "one_factor",
  "bypassPaths": ["/webhook", "/api/public"]
}
```

### Custom Rules

Advanced per-path rules:

```json
"authentication": {
  "required": true,
  "customRules": [
    {
      "path": "/admin",
      "policy": "two_factor",
      "groups": ["admins"]
    },
    {
      "path": "/api",
      "policy": "one_factor"
    }
  ]
}
```

## Testing Your Plugin

### 1. Validate Manifest

```bash
# Check JSON syntax
python -m json.tool plugin.json

# Validate with plugin manager
./scripts/plugin-manager.py validate
```

### 2. Test Locally

```bash
# Build configurations
./scripts/build.py

# Check generated files
cat output/docker-compose.yml | grep my-plugin
cat output/Caddyfile | grep my-plugin
```

### 3. Deploy in Test Environment

```bash
# Start only your plugin
docker-compose up my-plugin

# Check logs
docker-compose logs -f my-plugin

# Test routing
curl -H "Remote-User: testuser" http://localhost:8080
```

### 4. Integration Testing

```bash
# Full stack test
docker-compose up -d

# Access via browser
open https://example.com/my-plugin
```

## Best Practices

### 1. Security

- **Never expose ports directly** - Always use internal networks
- **Require authentication** - Default to `required: true`
- **Use least privilege** - Only request necessary permissions
- **Validate inputs** - Sanitize all user inputs
- **Keep secrets secure** - Use environment variables

### 2. Performance

- **Set resource limits** - Prevent resource exhaustion
- **Use health checks** - Ensure service availability
- **Optimize images** - Use alpine/slim variants
- **Cache static assets** - Reduce load times

### 3. Maintainability

- **Use semantic versioning** - Track changes properly
- **Document configuration** - Explain all settings
- **Provide examples** - Include sample configurations
- **Test thoroughly** - Validate before release
- **Handle errors gracefully** - Provide useful error messages

### 4. User Experience

- **Choose clear names** - Make purpose obvious
- **Write helpful descriptions** - Explain what the plugin does
- **Use appropriate icons** - Visual recognition helps
- **Order logically** - Group related plugins
- **Provide documentation** - Link to guides

## Examples

### Example 1: Wiki Plugin

```json
{
  "id": "wiki",
  "name": "Wiki.js",
  "version": "1.0.0",
  "description": "Modern wiki platform",
  "icon": "📚",
  "category": "productivity",
  "type": "docker",

  "docker": {
    "enabled": true,
    "image": "requarks/wiki",
    "tag": "2",
    "internalPort": 3000,
    "environment": {
      "DB_TYPE": "sqlite"
    },
    "volumes": [
      {
        "type": "named",
        "source": "wiki_data",
        "target": "/wiki/data"
      }
    ]
  },

  "routing": {
    "type": "subdomain",
    "subdomain": "wiki"
  },

  "authentication": {
    "required": true,
    "policy": "one_factor"
  }
}
```

### Example 2: Monitoring Stack

```json
{
  "id": "monitoring",
  "name": "Prometheus + Grafana",
  "version": "1.0.0",
  "description": "Full monitoring stack",
  "icon": "📊",
  "category": "monitoring",
  "type": "hybrid",

  "docker": {
    "enabled": true,
    "image": "prom/prometheus",
    "tag": "latest",
    "internalPort": 9090,
    "volumes": [
      {
        "type": "bind",
        "source": "./prometheus.yml",
        "target": "/etc/prometheus/prometheus.yml"
      }
    ]
  },

  "routing": {
    "type": "both",
    "subdomain": "metrics",
    "path": "/metrics",
    "additionalDomains": ["grafana"]
  },

  "authentication": {
    "required": true,
    "policy": "two_factor",
    "requiredGroups": ["admins"]
  }
}
```

### Example 3: Static Documentation

```json
{
  "id": "docs",
  "name": "Documentation",
  "version": "1.0.0",
  "description": "Project documentation",
  "icon": "📖",
  "category": "utilities",
  "type": "static",

  "routing": {
    "type": "path",
    "path": "/docs"
  },

  "ui": {
    "customPages": [
      {
        "path": "/docs",
        "file": "ui/index.html",
        "requiresAdmin": false
      }
    ]
  },

  "authentication": {
    "required": false
  }
}
```

## Troubleshooting

### Plugin Not Showing on Dashboard

1. Check if enabled in `plugins-config.json`
2. Verify `ui.dashboard.visible` is true
3. Check admin requirements if `requiresAdmin` is true
4. Rebuild with `./scripts/build.py`

### Container Won't Start

1. Check Docker logs: `docker-compose logs my-plugin`
2. Verify image exists: `docker pull image:tag`
3. Check port conflicts
4. Validate environment variables

### Routing Not Working

1. Check Caddyfile was regenerated
2. Verify routing type matches configuration
3. Check authentication headers
4. Test with curl: `curl -v https://example.com/path`

### Authentication Issues

1. Verify Authelia is running
2. Check forward_auth configuration
3. Validate required groups exist
4. Test with bypass paths first

## Getting Help

- Check existing plugins in `plugins/available/` for examples
- Review the [Plugin Schema Documentation](plugins/PLUGIN_SCHEMA.md)
- Test with the plugin validator: `./scripts/plugin-manager.py validate`
- Enable verbose logging in Docker Compose

## Contributing Plugins

To share your plugin with the community:

1. Ensure it follows best practices
2. Include comprehensive documentation
3. Test thoroughly in different environments
4. Submit a pull request to add to `plugins/available/`

Happy plugin development! 🚀