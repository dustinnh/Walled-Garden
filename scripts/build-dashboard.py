#!/usr/bin/env python3
"""
Build Dashboard HTML from enabled plugins.

This script reads the plugin configuration and generates a dashboard HTML file
with cards for all enabled plugins that should be visible on the dashboard.
"""

import json
import os
import sys
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

def generate_card_html(plugin: Dict[str, Any], settings: Dict[str, Any]) -> str:
    """Generate HTML for a single plugin card."""
    domain = settings.get("domain", "example.com")

    # Determine the URL based on routing configuration
    url = "/"
    if plugin.get("routing", {}).get("type") == "subdomain":
        subdomain = plugin["routing"].get("subdomain", plugin["id"])
        url = f"https://{subdomain}.{domain}/"
    elif plugin.get("routing", {}).get("type") == "path":
        path = plugin["routing"].get("path", f"/{plugin['id']}")
        url = f"https://{domain}{path}"
    elif plugin.get("routing", {}).get("type") == "both":
        # Prefer subdomain for dashboard link
        if plugin["routing"].get("subdomain"):
            subdomain = plugin["routing"]["subdomain"]
            url = f"https://{subdomain}.{domain}/"
        else:
            path = plugin["routing"].get("path", f"/{plugin['id']}")
            url = f"https://{domain}{path}"

    # Handle special cases for core plugins
    if plugin["id"] == "dns-tools":
        url = "/dns.html"
    elif plugin["id"] == "user-admin":
        url = "/admin.html"

    # Check if admin-only
    admin_class = "admin-only" if plugin.get("ui", {}).get("dashboard", {}).get("requiresAdmin", False) else ""

    return f'''
            <li class="app-card {admin_class}">
                <a href="{url}" class="app-link">
                    <div class="app-icon">{plugin.get("icon", "📦")}</div>
                    <div class="app-details">
                        <div class="app-name">{plugin.get("name", plugin["id"])}</div>
                        <div class="app-desc">{plugin.get("description", "")}</div>
                    </div>
                </a>
            </li>'''

def generate_dashboard_html(plugins: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
    """Generate the complete dashboard HTML."""

    # Sort plugins by order
    plugins.sort(key=lambda p: p.get("ui", {}).get("dashboard", {}).get("order", 999))

    # Generate cards
    cards_html = ""
    for plugin in plugins:
        if plugin.get("ui", {}).get("dashboard", {}).get("visible", True):
            cards_html += generate_card_html(plugin, settings)

    # Generate the complete HTML
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            width: 100%;
            max-width: 1200px;
        }}

        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
            text-align: center;
        }}

        .subtitle {{
            color: #666;
            text-align: center;
            margin-bottom: 40px;
            font-size: 16px;
        }}

        .app-grid {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            padding: 0;
        }}

        .app-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            overflow: hidden;
            display: flex;
        }}

        .app-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        }}

        .app-link {{
            text-decoration: none;
            color: inherit;
            display: flex;
            padding: 20px;
            width: 100%;
        }}

        .app-icon {{
            font-size: 40px;
            margin-right: 15px;
            display: flex;
            align-items: center;
        }}

        .app-details {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .app-name {{
            font-weight: 600;
            font-size: 18px;
            color: #333;
            margin-bottom: 5px;
        }}

        .app-desc {{
            color: #666;
            font-size: 14px;
            line-height: 1.4;
        }}

        .admin-only {{
            border-left: 4px solid #e74c3c;
        }}

        .admin-only.hidden {{
            display: none;
        }}

        .special-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #e0e0e0;
        }}

        .special-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .special-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            h1 {{
                font-size: 24px;
            }}

            .app-grid {{
                grid-template-columns: 1fr;
            }}

            .special-links {{
                flex-direction: column;
            }}

            .special-link {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">{subtitle}</p>

        <ul class="app-grid">
{cards}
        </ul>

        <div class="special-links">
            <a href="/auth/logout" class="special-link">
                <span>🚪</span>
                <span>Logout</span>
            </a>
        </div>
    </div>

    <script>
        // Check if user has admin access by attempting to access an admin endpoint
        async function checkAdminAccess() {{
            try {{
                const response = await fetch('/api/admin/users', {{
                    method: 'GET',
                    credentials: 'include'
                }});

                if (response.ok) {{
                    // User has admin access, show admin-only cards
                    console.log('Admin access confirmed');
                }} else {{
                    // User doesn't have admin access, hide admin-only cards
                    document.querySelectorAll('.admin-only').forEach(card => {{
                        card.classList.add('hidden');
                    }});
                }}
            }} catch (error) {{
                // Error checking, hide admin cards to be safe
                console.error('Error checking admin access:', error);
                document.querySelectorAll('.admin-only').forEach(card => {{
                    card.classList.add('hidden');
                }});
            }}
        }}

        // Check admin access on page load
        document.addEventListener('DOMContentLoaded', checkAdminAccess);
    </script>
</body>
</html>'''

    # Format the HTML with our values
    html = html_template.format(
        title=settings.get("dashboard", {}).get("title", "Application Launcher"),
        subtitle=settings.get("dashboard", {}).get("subtitle", "Secure access to all your applications"),
        cards=cards_html
    )

    return html

def main():
    """Main function to build the dashboard."""
    # Parse command line arguments
    config_file = "plugins-config.json"
    output_file = "index.html"

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

    # Generate dashboard HTML
    html = generate_dashboard_html(plugins, settings)

    # Write output file
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✅ Dashboard generated: {output_file}")
    print(f"   - Loaded {len(plugins)} plugins")
    print(f"   - {sum(1 for p in plugins if p.get('ui', {}).get('dashboard', {}).get('visible', True))} visible on dashboard")

if __name__ == "__main__":
    main()