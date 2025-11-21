#!/usr/bin/env python3
"""
Main build orchestrator for the Walled Garden plugin system.

This script coordinates the generation of all configuration files from
the plugin manifests and configuration.
"""

import json
import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, List

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
    UNDERLINE = '\033[4m'

def print_header(message: str):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_status(message: str, status: str = "info"):
    """Print a status message with color."""
    if status == "success":
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    elif status == "info":
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
    else:
        print(f"   {message}")

def check_prerequisites() -> bool:
    """Check if all prerequisites are met."""
    print_header("Checking Prerequisites")

    all_good = True

    # Check Python version
    if sys.version_info < (3, 7):
        print_status("Python 3.7+ is required", "error")
        all_good = False
    else:
        print_status(f"Python {sys.version_info.major}.{sys.version_info.minor} detected", "success")

    # Check for required modules
    required_modules = ["json", "yaml"]
    for module in required_modules:
        try:
            __import__(module)
            print_status(f"Module '{module}' is available", "success")
        except ImportError:
            print_status(f"Module '{module}' is missing. Install with: pip install pyyaml", "error")
            all_good = False

    # Check for plugin configuration
    if not os.path.exists("plugins-config.json"):
        print_status("plugins-config.json not found. Creating from template...", "warning")
        create_default_config()
        print_status("Default configuration created. Please review and customize.", "info")

    # Check for plugins directory
    if not os.path.exists("plugins"):
        print_status("Plugins directory not found", "error")
        all_good = False
    else:
        print_status("Plugins directory found", "success")

    return all_good

def create_default_config():
    """Create a default plugins configuration file."""
    default_config = {
        "enabled": [
            "core/dns-tools",
            "core/user-admin",
            "available/excalidraw",
            "available/portainer",
            "available/n8n"
        ],
        "settings": {
            "domain": "example.com",
            "timezone": "UTC",
            "dashboard": {
                "title": "Application Launcher",
                "subtitle": "Secure access to all your applications",
                "theme": "default"
            }
        }
    }

    with open("plugins-config.json", 'w') as f:
        json.dump(default_config, f, indent=2)

def validate_plugin_manifests(config: Dict[str, Any]) -> bool:
    """Validate all enabled plugin manifests."""
    print_header("Validating Plugin Manifests")

    all_valid = True
    enabled_plugins = config.get("enabled", [])

    for plugin_path in enabled_plugins:
        manifest_path = os.path.join("plugins", plugin_path, "plugin.json")

        if not os.path.exists(manifest_path):
            print_status(f"Plugin manifest not found: {plugin_path}", "error")
            all_valid = False
            continue

        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            # Basic validation
            required_fields = ["id", "name", "version", "type"]
            missing_fields = [field for field in required_fields if field not in manifest]

            if missing_fields:
                print_status(f"{plugin_path}: Missing fields: {', '.join(missing_fields)}", "error")
                all_valid = False
            else:
                print_status(f"{plugin_path}: Valid", "success")

        except json.JSONDecodeError as e:
            print_status(f"{plugin_path}: Invalid JSON: {e}", "error")
            all_valid = False

    return all_valid

def run_build_script(script_name: str, config_file: str, output_file: str) -> bool:
    """Run a build script and capture its output."""
    script_path = os.path.join("scripts", script_name)

    if not os.path.exists(script_path):
        print_status(f"Build script not found: {script_name}", "error")
        return False

    try:
        # Make script executable
        os.chmod(script_path, 0o755)

        # Run the script
        result = subprocess.run(
            [sys.executable, script_path, config_file, output_file],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # Parse output for status
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print_status(f"Script failed: {result.stderr}", "error")
            return False

    except Exception as e:
        print_status(f"Error running script: {e}", "error")
        return False

def build_all(config: Dict[str, Any], output_dir: str = "output") -> bool:
    """Run all build scripts to generate configuration files."""
    print_header("Building Configuration Files")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Build tasks
    build_tasks = [
        ("build-dashboard.py", "plugins-config.json", os.path.join(output_dir, "index.html")),
        ("build-docker-compose.py", "plugins-config.json", os.path.join(output_dir, "docker-compose.yml")),
        ("build-caddy-routes.py", "plugins-config.json", os.path.join(output_dir, "Caddyfile"))
    ]

    all_success = True
    for script, config_file, output_file in build_tasks:
        print(f"\n{Colors.BOLD}Running {script}...{Colors.ENDC}")
        if run_build_script(script, config_file, output_file):
            print_status(f"Generated: {output_file}", "success")
        else:
            print_status(f"Failed to generate: {output_file}", "error")
            all_success = False

    return all_success

def copy_plugin_files(config: Dict[str, Any], output_dir: str):
    """Copy necessary plugin files to the output directory."""
    print_header("Copying Plugin Files")

    dashboard_dir = os.path.join(output_dir, "dashboard")
    os.makedirs(dashboard_dir, exist_ok=True)

    # Copy shared dashboard assets (CSS, etc.)
    if os.path.exists("dashboard"):
        print_status("Copying shared dashboard assets...", "info")
        # Copy CSS directory if it exists
        css_src = os.path.join("dashboard", "css")
        if os.path.exists(css_src):
            css_dst = os.path.join(dashboard_dir, "css")
            os.makedirs(css_dst, exist_ok=True)
            for file in os.listdir(css_src):
                src = os.path.join(css_src, file)
                dst = os.path.join(css_dst, file)
                shutil.copy2(src, dst)
                print_status(f"Copied: dashboard/css/{file}", "success")

    enabled_plugins = config.get("enabled", [])
    for plugin_path in enabled_plugins:
        plugin_dir = os.path.join("plugins", plugin_path)

        # Copy UI files
        ui_dir = os.path.join(plugin_dir, "ui")
        if os.path.exists(ui_dir):
            for file in os.listdir(ui_dir):
                src = os.path.join(ui_dir, file)
                dst = os.path.join(dashboard_dir, file)
                shutil.copy2(src, dst)
                print_status(f"Copied: {plugin_path}/ui/{file}", "success")

def generate_deployment_instructions(config: Dict[str, Any], output_dir: str):
    """Generate deployment instructions based on the configuration."""
    print_header("Generating Deployment Instructions")

    domain = config.get("settings", {}).get("domain", "example.com")

    instructions = f"""# Walled Garden Deployment Instructions

## Generated Configuration

Your plugin-based walled garden configuration has been generated in the `{output_dir}` directory.

## Files Generated

1. **index.html** - Main dashboard with enabled plugins
2. **docker-compose.yml** - Docker service definitions
3. **Caddyfile** - Reverse proxy routing configuration
4. **dashboard/** - Plugin UI files

## Deployment Steps

1. **Update Domain Settings**
   - Edit `plugins-config.json` and set your actual domain
   - Current domain: {domain}

2. **Generate Secrets**
   Run the following to generate required secrets:
   ```bash
   ./scripts/generate-secrets.sh > .env
   ```

3. **Configure Authelia**
   - Copy authelia configuration template
   - Update with your domain and secrets
   - Place in `./authelia/configuration.yml`

4. **Deploy Services**
   ```bash
   cd {output_dir}
   docker-compose up -d
   ```

5. **Verify Deployment**
   - Check services: `docker-compose ps`
   - View logs: `docker-compose logs -f`
   - Access dashboard: https://{domain}

## Enabled Plugins

The following plugins are enabled in your configuration:
"""

    # List enabled plugins
    for plugin_path in config.get("enabled", []):
        manifest_path = os.path.join("plugins", plugin_path, "plugin.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            instructions += f"\n- **{manifest['name']}** ({manifest['version']}) - {manifest['description']}"

    instructions += """

## Managing Plugins

To add or remove plugins:
1. Edit `plugins-config.json`
2. Run `./scripts/build.py` to regenerate configurations
3. Restart services: `docker-compose restart`

## Security Notes

- All services are on an internal Docker network
- No ports are exposed except Caddy (80/443)
- All traffic goes through Authelia authentication
- Remember to generate strong secrets for production

## Troubleshooting

- Check logs: `docker-compose logs [service-name]`
- Validate Caddyfile: `caddy validate --config Caddyfile`
- Test authentication: Access https://auth.{domain}

For more information, see the plugin development documentation.
"""

    # Write instructions
    instructions_file = os.path.join(output_dir, "DEPLOYMENT.md")
    with open(instructions_file, 'w') as f:
        f.write(instructions)

    print_status(f"Deployment instructions written to {instructions_file}", "success")

def main():
    """Main build orchestration function."""
    print_header("Walled Garden Plugin Build System")

    # Check prerequisites
    if not check_prerequisites():
        print_status("Prerequisites check failed. Please fix the issues above.", "error")
        sys.exit(1)

    # Load configuration
    with open("plugins-config.json", 'r') as f:
        config = json.load(f)

    # Validate plugin manifests
    if not validate_plugin_manifests(config):
        print_status("Plugin validation failed. Please fix the issues above.", "error")
        sys.exit(1)

    # Determine output directory
    output_dir = "output"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]

    # Build all configurations
    if not build_all(config, output_dir):
        print_status("Build failed. Please check the errors above.", "error")
        sys.exit(1)

    # Copy plugin files
    copy_plugin_files(config, output_dir)

    # Generate deployment instructions
    generate_deployment_instructions(config, output_dir)

    # Final summary
    print_header("Build Complete!")
    print_status(f"All configuration files have been generated in '{output_dir}'", "success")
    print_status("Review DEPLOYMENT.md for next steps", "info")
    print()
    print(f"{Colors.OKGREEN}Ready to deploy your walled garden! 🚀{Colors.ENDC}")

if __name__ == "__main__":
    main()