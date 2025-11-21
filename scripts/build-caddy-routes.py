#!/usr/bin/env python3
"""
Build Caddyfile routes from enabled plugins.

This script reads the plugin configuration and generates Caddyfile configuration
with routing rules for all enabled plugins.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

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

def generate_forward_auth_block(plugin: Dict[str, Any], domain: str) -> str:
    """Generate Authelia forward auth configuration for a route."""
    auth_config = plugin.get("authentication", {})

    if not auth_config.get("required", True):
        return ""

    policy = auth_config.get("policy", "one_factor")
    groups = auth_config.get("requiredGroups", [])

    # Build the forward_auth block
    auth_block = f"""        forward_auth authelia:9091 {{
            uri /api/verify?rd=https://{domain}/auth/
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }}"""

    return auth_block

def generate_path_routes(plugin: Dict[str, Any], domain: str) -> List[str]:
    """Generate path-based routes for a plugin."""
    routes = []
    routing = plugin.get("routing", {})

    if routing.get("type") not in ["path", "both"]:
        return routes

    paths = routing.get("paths", [routing.get("path", f"/{plugin['id']}")])
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        # Special handling for core plugins
        if plugin["id"] == "dns-tools":
            routes.append(f"""
    # DNS Diagnostic Tools
    handle_path /dns.html {{
        root * /srv/dashboard
        file_server
    }}

    handle_path /api/dns/* {{
{generate_forward_auth_block(plugin, domain)}
        # DNS API endpoints would be handled here
        # In production, these would proxy to a backend service
    }}""")

        elif plugin["id"] == "user-admin":
            routes.append(f"""
    # Authelia User Admin
    handle_path /admin.html {{
        root * /srv/dashboard
        file_server
    }}

    handle_path /api/admin/* {{
{generate_forward_auth_block(plugin, domain)}
        reverse_proxy authelia-file-admin:5000
    }}""")

        else:
            # Regular plugin with Docker backend
            strip_path = routing.get("stripPath", True)
            target_port = routing.get("targetPort", plugin.get("docker", {}).get("internalPort", 80))

            if strip_path:
                handle_directive = "handle_path"
            else:
                handle_directive = "handle"

            route = f"""
    # {plugin.get('name', plugin['id'])}
    {handle_directive} {path}* {{
{generate_forward_auth_block(plugin, domain)}
        reverse_proxy {plugin['id']}:{target_port}"""

            # Add custom headers if specified
            if routing.get("headers"):
                for key, value in routing["headers"].items():
                    route += f"\n        header {key} \"{value}\""

            route += "\n    }"
            routes.append(route)

    return routes

def generate_subdomain_routes(plugin: Dict[str, Any], domain: str) -> List[str]:
    """Generate subdomain-based routes for a plugin."""
    routes = []
    routing = plugin.get("routing", {})

    if routing.get("type") not in ["subdomain", "both"]:
        return routes

    # Main subdomain
    subdomain = routing.get("subdomain", plugin["id"])
    target_port = routing.get("targetPort", plugin.get("docker", {}).get("internalPort", 80))

    # Build route for main subdomain
    route = f"""{subdomain}.{domain} {{
    log {{
        output stdout
        level INFO
    }}

{generate_forward_auth_block(plugin, domain)}

    # {plugin.get('name', plugin['id'])}
    reverse_proxy {plugin['id']}:{target_port}"""

    # Add custom headers if specified
    if routing.get("headers"):
        for key, value in routing["headers"].items():
            route += f"\n    header {key} \"{value}\""

    route += "\n}"
    routes.append(route)

    # Additional subdomains
    if routing.get("additionalDomains"):
        for additional_domain in routing["additionalDomains"]:
            route = f"""{additional_domain}.{domain} {{
    log {{
        output stdout
        level INFO
    }}

{generate_forward_auth_block(plugin, domain)}

    # {plugin.get('name', plugin['id'])} - Additional domain
    reverse_proxy {plugin['id']}:{target_port}
}}"""
            routes.append(route)

    return routes

def generate_caddyfile(plugins: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
    """Generate complete Caddyfile configuration."""
    domain = settings.get("domain", "example.com")

    # Collect all routes
    subdomain_routes = []
    path_routes = []

    for plugin in plugins:
        # Skip plugins with no routing
        if plugin.get("routing", {}).get("type") == "none":
            continue

        # Generate subdomain routes
        subdomain_routes.extend(generate_subdomain_routes(plugin, domain))

        # Generate path routes
        path_routes.extend(generate_path_routes(plugin, domain))

    # Build the complete Caddyfile
    caddyfile = f"""# Walled Garden Caddyfile
# Generated by plugin build system
# Domain: {domain}

# Global options
{{
    admin off
    email admin@{domain}
}}

# Main domain with path-based routing
{domain} {{
    log {{
        output stdout
        level INFO
    }}

    # Main dashboard
    handle / {{
        forward_auth authelia:9091 {{
            uri /api/verify?rd=https://{domain}/auth/
            copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
        }}
        root * /srv/dashboard
        file_server
    }}

    # Path-based routes for plugins
{"".join(path_routes)}

    # Fallback
    handle {{
        respond "Not Found" 404
    }}
}}

# Authentication subdomain (Authelia)
auth.{domain} {{
    log {{
        output stdout
        level INFO
    }}

    reverse_proxy authelia:9091
}}

# Subdomain-based routes for plugins
{"".join(subdomain_routes)}

# Wildcard redirect to main domain
*.{domain} {{
    log {{
        output stdout
        level INFO
    }}

    redir https://{domain} permanent
}}"""

    return caddyfile

def main():
    """Main function to build Caddyfile configuration."""
    # Parse command line arguments
    config_file = "plugins-config.json"
    output_file = "Caddyfile"

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

    # Generate Caddyfile
    caddyfile = generate_caddyfile(plugins, settings)

    # Write output file
    with open(output_file, 'w') as f:
        f.write(caddyfile)

    print(f"✅ Caddyfile generated: {output_file}")
    print(f"   - Main domain: {settings.get('domain', 'example.com')}")
    print(f"   - Path routes: {sum(1 for p in plugins if p.get('routing', {}).get('type') in ['path', 'both'])}")
    print(f"   - Subdomain routes: {sum(1 for p in plugins if p.get('routing', {}).get('type') in ['subdomain', 'both'])}")

    # Validate Caddyfile if Caddy is available
    if os.system("which caddy > /dev/null 2>&1") == 0:
        print("\n🔍 Validating Caddyfile...")
        result = os.system(f"caddy validate --config {output_file} 2>/dev/null")
        if result == 0:
            print("✅ Caddyfile is valid")
        else:
            print("⚠️  Caddyfile validation failed - please review the configuration")

if __name__ == "__main__":
    main()