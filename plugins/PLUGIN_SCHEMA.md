# Plugin Schema Documentation

This document describes the structure and options available in the `plugin.json` manifest file for walled garden plugins.

## Schema Overview

Each plugin must have a `plugin.json` file in its root directory that describes the plugin's metadata, requirements, and configuration.

## Complete Schema Reference

```json
{
  "id": "string",
  "name": "string",
  "version": "string",
  "description": "string",
  "author": "string",
  "icon": "string",
  "category": "string",
  "type": "string",
  "tags": ["array"],

  "ui": {
    "dashboard": {
      "visible": "boolean",
      "requiresAdmin": "boolean",
      "order": "number",
      "customCard": "boolean",
      "cardTemplate": "string"
    },
    "customPages": [
      {
        "path": "string",
        "file": "string",
        "requiresAdmin": "boolean"
      }
    ]
  },

  "routing": {
    "type": "string",
    "subdomain": "string",
    "path": "string",
    "paths": ["array"],
    "stripPath": "boolean",
    "targetPort": "number",
    "additionalDomains": ["array"],
    "headers": {
      "key": "value"
    }
  },

  "docker": {
    "enabled": "boolean",
    "image": "string",
    "tag": "string",
    "containerName": "string",
    "internalPort": "number",
    "environment": {
      "KEY": "value"
    },
    "environmentFiles": ["array"],
    "volumes": [
      {
        "type": "string",
        "source": "string",
        "target": "string",
        "readOnly": "boolean"
      }
    ],
    "networks": ["array"],
    "dependencies": ["array"],
    "healthcheck": {
      "test": "string",
      "interval": "string",
      "timeout": "string",
      "retries": "number"
    },
    "resources": {
      "limits": {
        "memory": "string",
        "cpus": "string"
      }
    }
  },

  "authentication": {
    "required": "boolean",
    "policy": "string",
    "requiredGroups": ["array"],
    "excludedGroups": ["array"],
    "bypassPaths": ["array"],
    "customRules": [
      {
        "path": "string",
        "policy": "string",
        "groups": ["array"]
      }
    ]
  },

  "api": {
    "enabled": "boolean",
    "endpoints": [
      {
        "path": "string",
        "file": "string",
        "methods": ["array"],
        "requiresAdmin": "boolean"
      }
    ]
  },

  "storage": {
    "persistent": "boolean",
    "volumes": [
      {
        "name": "string",
        "path": "string",
        "size": "string"
      }
    ]
  },

  "configuration": {
    "settings": [
      {
        "key": "string",
        "label": "string",
        "type": "string",
        "default": "any",
        "required": "boolean",
        "description": "string",
        "validation": "string"
      }
    ]
  },

  "requirements": {
    "minVersion": "string",
    "plugins": ["array"],
    "services": ["array"]
  },

  "links": {
    "documentation": "string",
    "homepage": "string",
    "repository": "string",
    "issues": "string"
  }
}
```

## Field Descriptions

### Root Fields

- **id** (required): Unique identifier for the plugin (lowercase, no spaces, hyphens allowed)
- **name** (required): Display name for the plugin
- **version** (required): Semantic version (e.g., "1.0.0")
- **description** (required): Brief description of what the plugin does
- **author** (optional): Plugin author name or organization
- **icon** (required): Emoji or icon identifier for dashboard display
- **category** (required): One of: "productivity", "development", "monitoring", "security", "media", "utilities", "custom"
- **type** (required): One of: "docker", "api", "static", "external", "hybrid"
- **tags** (optional): Array of tags for searchability

### UI Section

Controls how the plugin appears in the dashboard and custom pages.

- **dashboard.visible**: Whether to show on main dashboard (default: true)
- **dashboard.requiresAdmin**: Only show to admin users (default: false)
- **dashboard.order**: Display order (lower numbers first, default: 999)
- **dashboard.customCard**: Use custom HTML template (default: false)
- **dashboard.cardTemplate**: Path to custom card HTML template
- **customPages**: Array of custom UI pages the plugin provides

### Routing Section

Defines how the plugin is accessed via the reverse proxy.

- **type**: One of: "subdomain", "path", "both", "none"
- **subdomain**: Subdomain to use (e.g., "wiki" for wiki.example.com)
- **path**: URL path (e.g., "/wiki" for example.com/wiki)
- **paths**: Array of paths if multiple needed
- **stripPath**: Remove path prefix when proxying (default: true)
- **targetPort**: Port to proxy to (defaults to docker.internalPort)
- **additionalDomains**: Extra subdomains needed (for multi-domain apps)
- **headers**: Additional headers to set when proxying

### Docker Section

Configuration for Docker container deployment.

- **enabled**: Whether this plugin uses Docker (default: true for type "docker")
- **image**: Docker image name (without tag)
- **tag**: Image tag (default: "latest")
- **containerName**: Custom container name (default: plugin id)
- **internalPort**: Port the container listens on
- **environment**: Environment variables as key-value pairs
- **environmentFiles**: Array of .env files to load
- **volumes**: Volume mount configurations
- **networks**: Additional networks (default includes "internal")
- **dependencies**: Other plugins that must be running
- **healthcheck**: Docker healthcheck configuration
- **resources**: Resource limits for the container

### Authentication Section

Authelia integration and access control.

- **required**: Whether authentication is required (default: true)
- **policy**: Default policy: "bypass", "one_factor", "two_factor" (default: "one_factor")
- **requiredGroups**: Groups that can access this plugin
- **excludedGroups**: Groups that cannot access this plugin
- **bypassPaths**: Paths that don't require authentication
- **customRules**: Advanced per-path access control rules

### API Section

For plugins that provide backend API endpoints.

- **enabled**: Whether this plugin provides API endpoints
- **endpoints**: Array of API endpoint configurations

### Storage Section

Persistent storage configuration.

- **persistent**: Whether plugin needs persistent storage
- **volumes**: Named volume configurations

### Configuration Section

User-configurable settings for the plugin.

- **settings**: Array of setting definitions that users can configure

### Requirements Section

Dependencies and compatibility requirements.

- **minVersion**: Minimum walled garden version required
- **plugins**: Other plugins that must be installed
- **services**: System services required (e.g., "redis", "postgres")

### Links Section

External resources and documentation.

- **documentation**: URL to documentation
- **homepage**: Plugin homepage
- **repository**: Source code repository
- **issues**: Issue tracker URL

## Plugin Types

### 1. Docker Service Plugin

Standard containerized application.

```json
{
  "type": "docker",
  "docker": {
    "enabled": true,
    "image": "linuxserver/wikijs",
    "internalPort": 3000
  }
}
```

### 2. API Service Plugin

Backend API with custom endpoints.

```json
{
  "type": "api",
  "api": {
    "enabled": true,
    "endpoints": [
      {
        "path": "/api/dns/*",
        "file": "api/dns-handler.py",
        "methods": ["GET", "POST"]
      }
    ]
  }
}
```

### 3. Static Plugin

Static HTML/CSS/JS files only.

```json
{
  "type": "static",
  "routing": {
    "type": "path",
    "path": "/tools"
  }
}
```

### 4. External Plugin

Links to external services.

```json
{
  "type": "external",
  "routing": {
    "type": "none"
  },
  "ui": {
    "dashboard": {
      "visible": true
    }
  }
}
```

### 5. Hybrid Plugin

Combination of multiple types.

```json
{
  "type": "hybrid",
  "docker": {
    "enabled": true
  },
  "api": {
    "enabled": true
  },
  "ui": {
    "customPages": [
      {
        "path": "/admin",
        "file": "ui/admin.html"
      }
    ]
  }
}
```

## Example Plugins

### Minimal Plugin

```json
{
  "id": "hello-world",
  "name": "Hello World",
  "version": "1.0.0",
  "description": "A simple hello world plugin",
  "icon": "👋",
  "category": "utilities",
  "type": "static",
  "routing": {
    "type": "path",
    "path": "/hello"
  }
}
```

### Complex Docker Plugin

```json
{
  "id": "nextcloud",
  "name": "Nextcloud",
  "version": "1.0.0",
  "description": "Self-hosted file sync and share",
  "icon": "☁️",
  "category": "productivity",
  "type": "docker",

  "docker": {
    "image": "nextcloud",
    "tag": "stable",
    "internalPort": 80,
    "environment": {
      "NEXTCLOUD_ADMIN_USER": "${NEXTCLOUD_ADMIN}",
      "NEXTCLOUD_ADMIN_PASSWORD": "${NEXTCLOUD_PASSWORD}",
      "NEXTCLOUD_TRUSTED_DOMAINS": "${DOMAIN}"
    },
    "volumes": [
      {
        "type": "named",
        "source": "nextcloud_data",
        "target": "/var/www/html"
      }
    ],
    "healthcheck": {
      "test": "curl -f http://localhost/status.php || exit 1",
      "interval": "30s",
      "timeout": "10s",
      "retries": 3
    }
  },

  "routing": {
    "type": "subdomain",
    "subdomain": "cloud",
    "additionalDomains": ["files", "drive"]
  },

  "authentication": {
    "policy": "two_factor",
    "bypassPaths": ["/status.php", "/remote.php/dav"]
  },

  "storage": {
    "persistent": true,
    "volumes": [
      {
        "name": "nextcloud_data",
        "path": "/var/www/html",
        "size": "10Gi"
      }
    ]
  },

  "configuration": {
    "settings": [
      {
        "key": "NEXTCLOUD_ADMIN",
        "label": "Admin Username",
        "type": "string",
        "default": "admin",
        "required": true
      },
      {
        "key": "NEXTCLOUD_PASSWORD",
        "label": "Admin Password",
        "type": "password",
        "required": true
      }
    ]
  }
}
```

## Validation Rules

1. **id** must be unique across all plugins
2. **version** must follow semantic versioning
3. **type** must be one of the defined types
4. **docker.image** is required if type is "docker" or "hybrid"
5. **routing.type** must match available routing patterns
6. **authentication.policy** must be valid Authelia policy
7. **category** must be from predefined list
8. All paths must start with "/"
9. Environment variable references use ${VAR_NAME} format
10. File paths are relative to plugin directory

## Best Practices

1. Keep plugin IDs short and descriptive
2. Use semantic versioning for version numbers
3. Provide clear, concise descriptions
4. Choose appropriate categories for discoverability
5. Document all configuration settings
6. Include healthchecks for Docker containers
7. Set reasonable resource limits
8. Use named volumes for persistent data
9. Follow least-privilege for authentication
10. Include links to documentation