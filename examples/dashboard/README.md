# Legacy Dashboard Files (Reference Only)

⚠️ **Note**: These are static example dashboard files from v1.x. The Walled Garden now uses a **plugin-based dashboard system** that generates the dashboard dynamically.

## Migration to Plugin System

As of v2.0, the Walled Garden uses a modular plugin architecture:

- **Dashboard Generation**: Run `./scripts/build.py` to generate dashboard from enabled plugins
- **Plugin UI Files**: Stored in `plugins/[plugin-name]/ui/`
- **Shared Assets**: Stored in `dashboard/` directory
- **Dynamic Configuration**: Use `plugins-config.json` to enable/disable services

## Files in This Directory

These files are kept for reference and backward compatibility:

### index.html
- Original static dashboard with hardcoded service cards
- **New System**: Generated dynamically by `scripts/build-dashboard.py`
- Cards are created from plugin manifests

### dns.html
- DNS diagnostic tools interface
- **New Location**: `plugins/core/dns-tools/ui/dns.html`
- Automatically copied during build process

### admin.html
- Authelia user management interface
- **New Location**: `plugins/core/user-admin/ui/admin.html`
- Automatically copied during build process

## How to Migrate

If you're using these static files:

1. **Enable equivalent plugins**:
   ```bash
   ./scripts/plugin-manager.py enable core/dns-tools
   ./scripts/plugin-manager.py enable core/user-admin
   ```

2. **Add your custom services as plugins**:
   - Create plugin manifests in `plugins/custom/`
   - See [Plugin Development Guide](../../PLUGIN_DEVELOPMENT.md)

3. **Build the new dashboard**:
   ```bash
   ./scripts/build.py
   ```

4. **Deploy**:
   ```bash
   cd output
   docker-compose up -d
   ```

## Why Keep These Files?

1. **Reference Implementation**: Shows the original dashboard design
2. **Backward Compatibility**: Users can still use static files if preferred
3. **Quick Start**: Can be used directly without the build system
4. **Template**: Useful as templates for custom plugin UI files

## Using Static Files (Not Recommended)

If you prefer the simple static approach:

1. Copy these files to your deployment directory
2. Mount in Caddy/Nginx as static files
3. Manually edit index.html to add/remove services

However, you'll miss out on:
- Automatic service management
- Plugin versioning
- Easy enable/disable of services
- Consistent configuration management

## Recommended Approach

Use the plugin system for better maintainability:

```bash
# List available plugins
./scripts/plugin-manager.py list

# Enable plugins you want
./scripts/plugin-manager.py enable available/[plugin-name]

# Build configuration
./scripts/build.py

# Deploy
cd output && docker-compose up -d
```

For more information, see the [main documentation](../../README.md).