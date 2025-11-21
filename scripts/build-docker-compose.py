#!/usr/bin/env python3
"""
Build Docker Compose configuration from enabled plugins.

This script reads the plugin configuration and generates a docker-compose.yml file
with service definitions for all enabled plugins that use Docker containers.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_plugin_config(config_path: str = "plugins-config.json") -> Dict[str, Any]:
    """Load the plugin configuration file."""
    if not os.path.exists(config_path):
        print(f"Error: Plugin config file '{config_path}' not found.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)

def load_plugin_manifest(plugin_path: str) -> Dict[str, Any]:
    """Load a plugin manifest file."""
    manifest_path = os.path.join("plugins", plugin_path, "plugin.json")
    if not os.path.exists(manifest_path):
        print(f"Warning: Plugin manifest not found: {manifest_path}")
        return None

    with open(manifest_path, 'r') as f:
        return json.load(f)

def generate_service_definition(plugin: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Docker Compose service definition for a plugin."""
    docker_config = plugin.get("docker", {})

    if not docker_config.get("enabled", False):
        return None

    # Base service definition
    service = {
        "image": f"{docker_config['image']}:{docker_config.get('tag', 'latest')}",
        "container_name": docker_config.get("containerName", plugin["id"]),
        "restart": "unless-stopped",
        "networks": docker_config.get("networks", ["internal"])
    }

    # Add environment variables
    if docker_config.get("environment"):
        service["environment"] = docker_config["environment"]

    # Add environment files
    if docker_config.get("environmentFiles"):
        service["env_file"] = docker_config["environmentFiles"]

    # Add volumes
    if docker_config.get("volumes"):
        volumes = []
        for vol in docker_config["volumes"]:
            if vol["type"] == "named":
                volumes.append(f"{vol['source']}:{vol['target']}")
            elif vol["type"] == "bind":
                volumes.append(f"{vol['source']}:{vol['target']}" + (":ro" if vol.get("readOnly", False) else ""))
        if volumes:
            service["volumes"] = volumes

    # Add healthcheck
    if docker_config.get("healthcheck"):
        healthcheck = docker_config["healthcheck"]
        service["healthcheck"] = {
            "test": healthcheck["test"],
            "interval": healthcheck.get("interval", "30s"),
            "timeout": healthcheck.get("timeout", "10s"),
            "retries": healthcheck.get("retries", 3)
        }

    # Add resource limits
    if docker_config.get("resources", {}).get("limits"):
        limits = docker_config["resources"]["limits"]
        service["deploy"] = {
            "resources": {
                "limits": {}
            }
        }
        if limits.get("memory"):
            service["deploy"]["resources"]["limits"]["memory"] = limits["memory"]
        if limits.get("cpus"):
            service["deploy"]["resources"]["limits"]["cpus"] = limits["cpus"]

    # Add dependencies
    if docker_config.get("dependencies"):
        service["depends_on"] = docker_config["dependencies"]

    # Never expose ports directly (security requirement)
    # All traffic goes through reverse proxy

    return service

def generate_docker_compose(plugins: List[Dict[str, Any]], settings: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete Docker Compose configuration."""

    compose = {
        "version": "3.9",
        "services": {},
        "networks": {
            "internal": {
                "driver": "bridge",
                "internal": True
            }
        },
        "volumes": {}
    }

    # Add core services (Caddy and Authelia)
    compose["services"]["caddy"] = {
        "image": "caddy:latest",
        "container_name": "caddy",
        "restart": "unless-stopped",
        "ports": [
            "80:80",
            "443:443"
        ],
        "volumes": [
            "./Caddyfile:/etc/caddy/Caddyfile",
            "caddy_data:/data",
            "caddy_config:/config",
            "./dashboard:/srv/dashboard"
        ],
        "networks": ["internal"],
        "environment": {
            "DOMAIN": settings.get("domain", "example.com")
        }
    }

    compose["services"]["authelia"] = {
        "image": "authelia/authelia:latest",
        "container_name": "authelia",
        "restart": "unless-stopped",
        "volumes": [
            "./authelia:/config"
        ],
        "networks": ["internal"],
        "environment": {
            "TZ": settings.get("timezone", "UTC"),
            "AUTHELIA_JWT_SECRET_FILE": "/config/secrets/jwt_secret",
            "AUTHELIA_SESSION_SECRET_FILE": "/config/secrets/session_secret",
            "AUTHELIA_STORAGE_ENCRYPTION_KEY_FILE": "/config/secrets/storage_encryption_key"
        }
    }

    # Add plugin services
    for plugin in plugins:
        service_def = generate_service_definition(plugin)
        if service_def:
            compose["services"][plugin["id"]] = service_def

            # Collect named volumes
            if plugin.get("storage", {}).get("persistent"):
                for vol in plugin.get("storage", {}).get("volumes", []):
                    compose["volumes"][vol["name"]] = {
                        "driver": "local"
                    }

            # Also check docker volumes for named volumes
            if plugin.get("docker", {}).get("volumes"):
                for vol in plugin["docker"]["volumes"]:
                    if vol.get("type") == "named":
                        compose["volumes"][vol["source"]] = {
                            "driver": "local"
                        }

    # Add standard volumes
    compose["volumes"]["caddy_data"] = {"driver": "local"}
    compose["volumes"]["caddy_config"] = {"driver": "local"}

    return compose

def main():
    """Main function to build Docker Compose configuration."""
    # Parse command line arguments
    config_file = "plugins-config.json"
    output_file = "docker-compose.yml"

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Load configuration
    config = load_plugin_config(config_file)
    enabled_plugins = config.get("enabled", [])
    settings = config.get("settings", {})

    # Load all enabled plugins
    plugins = []
    for plugin_path in enabled_plugins:
        manifest = load_plugin_manifest(plugin_path)
        if manifest:
            plugins.append(manifest)

    # Generate Docker Compose configuration
    compose_config = generate_docker_compose(plugins, settings)

    # Write output file with nice formatting
    with open(output_file, 'w') as f:
        yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False, indent=2)

    print(f"✅ Docker Compose configuration generated: {output_file}")
    print(f"   - Core services: 2 (caddy, authelia)")
    print(f"   - Plugin services: {sum(1 for p in plugins if p.get('docker', {}).get('enabled', False))}")
    print(f"   - Named volumes: {len(compose_config.get('volumes', {}))}")

    # Generate .env template if it doesn't exist
    env_template_file = ".env.template"
    if not os.path.exists(env_template_file):
        generate_env_template(plugins, settings, env_template_file)

def generate_env_template(plugins: List[Dict[str, Any]], settings: Dict[str, Any], output_file: str):
    """Generate environment variable template file."""
    env_vars = []

    # Core settings
    env_vars.append("# Core Settings")
    env_vars.append("DOMAIN=example.com")
    env_vars.append("TIMEZONE=UTC")
    env_vars.append("")

    # Collect all required environment variables from plugins
    for plugin in plugins:
        plugin_vars = []

        # Check docker environment variables for placeholders
        if plugin.get("docker", {}).get("environment"):
            for key, value in plugin["docker"]["environment"].items():
                if "${" in str(value):
                    # Extract variable name
                    var_name = value.replace("${", "").replace("}", "")
                    if var_name not in ["DOMAIN", "TIMEZONE"]:  # Skip already added
                        plugin_vars.append(var_name)

        # Check configuration settings
        if plugin.get("configuration", {}).get("settings"):
            for setting in plugin["configuration"]["settings"]:
                if setting.get("required", False):
                    plugin_vars.append(setting["key"])

        if plugin_vars:
            env_vars.append(f"# {plugin['name']} Plugin")
            for var in set(plugin_vars):  # Remove duplicates
                # Find description from configuration
                desc = ""
                for setting in plugin.get("configuration", {}).get("settings", []):
                    if setting["key"] == var:
                        desc = f" # {setting.get('description', '')}"
                        break
                env_vars.append(f"{var}={desc}")
            env_vars.append("")

    # Write environment template
    with open(output_file, 'w') as f:
        f.write("\n".join(env_vars))

    print(f"✅ Environment template generated: {output_file}")

if __name__ == "__main__":
    main()