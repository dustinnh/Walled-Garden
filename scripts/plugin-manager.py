#!/usr/bin/env python3
"""
Plugin Manager CLI for Walled Garden.

A command-line tool for managing plugins - listing, enabling, disabling,
and getting information about available plugins.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import textwrap

# ANSI color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def load_config(config_path: str = "plugins-config.json") -> Dict[str, Any]:
    """Load the plugin configuration file."""
    if not os.path.exists(config_path):
        return {
            "enabled": [],
            "settings": {
                "domain": "example.com",
                "dashboard": {
                    "title": "Application Launcher"
                }
            }
        }

    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config: Dict[str, Any], config_path: str = "plugins-config.json"):
    """Save the plugin configuration file."""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def discover_plugins(plugins_dir: str = "plugins") -> List[str]:
    """Discover all available plugins."""
    plugins = []

    for category in ["core", "available", "custom"]:
        category_dir = os.path.join(plugins_dir, category)
        if os.path.exists(category_dir):
            for plugin_name in os.listdir(category_dir):
                plugin_path = os.path.join(category_dir, plugin_name)
                manifest_path = os.path.join(plugin_path, "plugin.json")
                if os.path.isdir(plugin_path) and os.path.exists(manifest_path):
                    plugins.append(f"{category}/{plugin_name}")

    return sorted(plugins)

def load_plugin_manifest(plugin_path: str) -> Optional[Dict[str, Any]]:
    """Load a plugin manifest file."""
    manifest_path = os.path.join("plugins", plugin_path, "plugin.json")
    if not os.path.exists(manifest_path):
        return None

    try:
        with open(manifest_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def list_plugins(args):
    """List all available plugins."""
    config = load_config()
    enabled_plugins = config.get("enabled", [])
    all_plugins = discover_plugins()

    if args.enabled:
        # Show only enabled plugins
        plugins_to_show = enabled_plugins
        print(f"\n{Colors.BOLD}Enabled Plugins:{Colors.ENDC}")
    elif args.disabled:
        # Show only disabled plugins
        plugins_to_show = [p for p in all_plugins if p not in enabled_plugins]
        print(f"\n{Colors.BOLD}Disabled Plugins:{Colors.ENDC}")
    else:
        # Show all plugins
        plugins_to_show = all_plugins
        print(f"\n{Colors.BOLD}All Plugins:{Colors.ENDC}")

    if not plugins_to_show:
        print(f"{Colors.DIM}  No plugins found{Colors.ENDC}")
        return

    # Group by category
    categories = {}
    for plugin_path in plugins_to_show:
        category = plugin_path.split('/')[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(plugin_path)

    # Display plugins
    for category in ["core", "available", "custom"]:
        if category in categories:
            print(f"\n{Colors.OKCYAN}  {category.upper()}:{Colors.ENDC}")
            for plugin_path in categories[category]:
                manifest = load_plugin_manifest(plugin_path)
                if manifest:
                    status = f"{Colors.OKGREEN}[enabled]{Colors.ENDC}" if plugin_path in enabled_plugins else f"{Colors.DIM}[disabled]{Colors.ENDC}"
                    print(f"    {manifest.get('icon', '📦')} {Colors.BOLD}{manifest['name']}{Colors.ENDC} ({manifest['version']}) {status}")
                    if args.verbose:
                        print(f"       {Colors.DIM}{manifest.get('description', 'No description')}{Colors.ENDC}")
                        print(f"       Path: {plugin_path}")
                        print(f"       Type: {manifest.get('type', 'unknown')}")

def show_plugin_info(args):
    """Show detailed information about a specific plugin."""
    manifest = load_plugin_manifest(args.plugin)
    if not manifest:
        print(f"{Colors.FAIL}Error: Plugin '{args.plugin}' not found{Colors.ENDC}")
        sys.exit(1)

    config = load_config()
    enabled = args.plugin in config.get("enabled", [])

    print(f"\n{Colors.BOLD}Plugin Information{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 50}{Colors.ENDC}")

    print(f"Name:        {manifest.get('icon', '📦')} {Colors.BOLD}{manifest['name']}{Colors.ENDC}")
    print(f"ID:          {manifest['id']}")
    print(f"Version:     {manifest['version']}")
    print(f"Status:      {Colors.OKGREEN}Enabled{Colors.ENDC if enabled else Colors.DIM}Disabled{Colors.ENDC}")
    print(f"Type:        {manifest.get('type', 'unknown')}")
    print(f"Category:    {manifest.get('category', 'uncategorized')}")

    if manifest.get('author'):
        print(f"Author:      {manifest['author']}")

    if manifest.get('description'):
        print(f"\nDescription:")
        wrapped = textwrap.fill(manifest['description'], width=60, initial_indent="  ", subsequent_indent="  ")
        print(wrapped)

    # Routing information
    if manifest.get('routing'):
        routing = manifest['routing']
        print(f"\n{Colors.BOLD}Routing:{Colors.ENDC}")
        print(f"  Type:      {routing.get('type', 'none')}")
        if routing.get('subdomain'):
            print(f"  Subdomain: {routing['subdomain']}.example.com")
        if routing.get('path'):
            print(f"  Path:      {routing['path']}")

    # Docker information
    if manifest.get('docker', {}).get('enabled'):
        docker = manifest['docker']
        print(f"\n{Colors.BOLD}Docker:{Colors.ENDC}")
        print(f"  Image:     {docker['image']}:{docker.get('tag', 'latest')}")
        print(f"  Port:      {docker.get('internalPort', 'N/A')}")
        if docker.get('volumes'):
            print(f"  Volumes:   {len(docker['volumes'])}")

    # Authentication
    if manifest.get('authentication'):
        auth = manifest['authentication']
        print(f"\n{Colors.BOLD}Authentication:{Colors.ENDC}")
        print(f"  Required:  {'Yes' if auth.get('required', True) else 'No'}")
        print(f"  Policy:    {auth.get('policy', 'one_factor')}")
        if auth.get('requiredGroups'):
            print(f"  Groups:    {', '.join(auth['requiredGroups'])}")

    # Configuration settings
    if manifest.get('configuration', {}).get('settings'):
        settings = manifest['configuration']['settings']
        print(f"\n{Colors.BOLD}Configuration ({len(settings)} settings):{Colors.ENDC}")
        for setting in settings[:3]:  # Show first 3 settings
            required = " (required)" if setting.get('required') else ""
            print(f"  - {setting['label']}{required}")
        if len(settings) > 3:
            print(f"  ... and {len(settings) - 3} more")

    # Links
    if manifest.get('links'):
        links = manifest['links']
        print(f"\n{Colors.BOLD}Links:{Colors.ENDC}")
        if links.get('documentation'):
            print(f"  Docs:      {links['documentation']}")
        if links.get('repository'):
            print(f"  Repo:      {links['repository']}")
        if links.get('homepage'):
            print(f"  Homepage:  {links['homepage']}")

def enable_plugin(args):
    """Enable a plugin."""
    config = load_config()
    enabled = config.get("enabled", [])

    # Check if plugin exists
    manifest = load_plugin_manifest(args.plugin)
    if not manifest:
        print(f"{Colors.FAIL}Error: Plugin '{args.plugin}' not found{Colors.ENDC}")
        print(f"Available plugins: {', '.join(discover_plugins())}")
        sys.exit(1)

    # Check if already enabled
    if args.plugin in enabled:
        print(f"{Colors.WARNING}Plugin '{manifest['name']}' is already enabled{Colors.ENDC}")
        return

    # Check dependencies
    if manifest.get('requirements', {}).get('plugins'):
        missing_deps = []
        for dep in manifest['requirements']['plugins']:
            if dep not in enabled:
                missing_deps.append(dep)

        if missing_deps:
            print(f"{Colors.WARNING}Warning: This plugin requires the following plugins:{Colors.ENDC}")
            for dep in missing_deps:
                print(f"  - {dep}")
            if not args.force:
                print(f"\nUse --force to enable anyway, or enable dependencies first")
                sys.exit(1)

    # Enable the plugin
    enabled.append(args.plugin)
    config["enabled"] = enabled
    save_config(config)

    print(f"{Colors.OKGREEN}✅ Enabled plugin: {manifest['name']}{Colors.ENDC}")
    print(f"\nRun {Colors.BOLD}./scripts/build.py{Colors.ENDC} to regenerate configuration files")

def disable_plugin(args):
    """Disable a plugin."""
    config = load_config()
    enabled = config.get("enabled", [])

    # Check if plugin is enabled
    if args.plugin not in enabled:
        print(f"{Colors.WARNING}Plugin '{args.plugin}' is not enabled{Colors.ENDC}")
        return

    # Load manifest for display name
    manifest = load_plugin_manifest(args.plugin)
    plugin_name = manifest['name'] if manifest else args.plugin

    # Check if it's a core plugin
    if args.plugin.startswith("core/") and not args.force:
        print(f"{Colors.WARNING}Warning: '{plugin_name}' is a core plugin!{Colors.ENDC}")
        print("Disabling core plugins may break essential functionality.")
        print("Use --force to disable anyway")
        sys.exit(1)

    # Check for dependent plugins
    dependent_plugins = []
    for other_plugin in enabled:
        if other_plugin == args.plugin:
            continue
        other_manifest = load_plugin_manifest(other_plugin)
        if other_manifest and args.plugin in other_manifest.get('requirements', {}).get('plugins', []):
            dependent_plugins.append(other_manifest['name'])

    if dependent_plugins and not args.force:
        print(f"{Colors.WARNING}Warning: The following plugins depend on '{plugin_name}':{Colors.ENDC}")
        for dep in dependent_plugins:
            print(f"  - {dep}")
        print("\nUse --force to disable anyway")
        sys.exit(1)

    # Disable the plugin
    enabled.remove(args.plugin)
    config["enabled"] = enabled
    save_config(config)

    print(f"{Colors.OKGREEN}✅ Disabled plugin: {plugin_name}{Colors.ENDC}")
    print(f"\nRun {Colors.BOLD}./scripts/build.py{Colors.ENDC} to regenerate configuration files")

def validate_plugins(args):
    """Validate all enabled plugins."""
    config = load_config()
    enabled = config.get("enabled", [])

    print(f"\n{Colors.BOLD}Validating Enabled Plugins{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 50}{Colors.ENDC}\n")

    errors = []
    warnings = []

    for plugin_path in enabled:
        manifest = load_plugin_manifest(plugin_path)

        if not manifest:
            errors.append(f"Plugin '{plugin_path}' not found or has invalid manifest")
            continue

        print(f"Checking {Colors.BOLD}{manifest['name']}{Colors.ENDC}...")

        # Check required fields
        required_fields = ["id", "name", "version", "type"]
        for field in required_fields:
            if field not in manifest:
                errors.append(f"  {plugin_path}: Missing required field '{field}'")

        # Check dependencies
        if manifest.get('requirements', {}).get('plugins'):
            for dep in manifest['requirements']['plugins']:
                if dep not in enabled:
                    warnings.append(f"  {plugin_path}: Dependency '{dep}' is not enabled")

        # Check for UI files if specified
        if manifest.get('ui', {}).get('customPages'):
            for page in manifest['ui']['customPages']:
                ui_file = os.path.join("plugins", plugin_path, page['file'])
                if not os.path.exists(ui_file):
                    warnings.append(f"  {plugin_path}: UI file '{page['file']}' not found")

    # Display results
    print()
    if errors:
        print(f"{Colors.FAIL}Errors found:{Colors.ENDC}")
        for error in errors:
            print(f"  ❌ {error}")

    if warnings:
        print(f"\n{Colors.WARNING}Warnings:{Colors.ENDC}")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    if not errors and not warnings:
        print(f"{Colors.OKGREEN}✅ All plugins validated successfully!{Colors.ENDC}")

    sys.exit(1 if errors else 0)

def main():
    """Main entry point for the plugin manager."""
    parser = argparse.ArgumentParser(
        description="Walled Garden Plugin Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              plugin-manager.py list
              plugin-manager.py list --enabled
              plugin-manager.py info available/excalidraw
              plugin-manager.py enable available/n8n
              plugin-manager.py disable available/portainer
              plugin-manager.py validate
        """)
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List plugins')
    list_parser.add_argument('-e', '--enabled', action='store_true', help='Show only enabled plugins')
    list_parser.add_argument('-d', '--disabled', action='store_true', help='Show only disabled plugins')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    list_parser.set_defaults(func=list_plugins)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show detailed plugin information')
    info_parser.add_argument('plugin', help='Plugin path (e.g., available/excalidraw)')
    info_parser.set_defaults(func=show_plugin_info)

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a plugin')
    enable_parser.add_argument('plugin', help='Plugin path to enable')
    enable_parser.add_argument('-f', '--force', action='store_true', help='Force enable even with missing dependencies')
    enable_parser.set_defaults(func=enable_plugin)

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a plugin')
    disable_parser.add_argument('plugin', help='Plugin path to disable')
    disable_parser.add_argument('-f', '--force', action='store_true', help='Force disable even if other plugins depend on it')
    disable_parser.set_defaults(func=disable_plugin)

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate enabled plugins')
    validate_parser.set_defaults(func=validate_plugins)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()