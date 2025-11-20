# Documentation

Comprehensive guides for deploying and managing the Authelia Walled Garden.

## Core Documentation

### [ARCHITECTURE.md](ARCHITECTURE.md)
System design and architecture overview. Includes detailed Mermaid diagrams showing network topology, authentication flow, and component interactions.

**Topics Covered**:
- Network architecture and security model
- Authentication flow diagrams
- Component interactions
- Docker networking setup

### [PDR.md](PDR.md) - Project Design Record
The complete deployment guide (1,955 lines). This is your primary reference for understanding and deploying the entire system.

**Topics Covered**:
- Complete system requirements
- Step-by-step deployment instructions
- Configuration explanations
- Troubleshooting common issues
- Production best practices

### [HOWTO-ADD-SERVICES.md](HOWTO-ADD-SERVICES.md)
Practical step-by-step guide for adding new services to your walled garden.

**Topics Covered**:
- Adding Docker containers
- Configuring Caddy routes
- Setting up Authelia access control
- Adding dashboard cards
- Testing and troubleshooting

### [NEXTERM-INSTALLATION.md](NEXTERM-INSTALLATION.md)
Specific guide for integrating Nexterm web terminal.

**Topics Covered**:
- Nexterm deployment
- Configuration requirements
- Security considerations

## Advanced Topics

### [advanced/dns-tool-architecture.md](advanced/dns-tool-architecture.md)
Deep dive into the custom DNS troubleshooting tools.

### [advanced/dig-card.md](advanced/dig-card.md)
Documentation for the DNS dig tool interface.

### [advanced/walled-garden-architecture.mermaid.md](advanced/walled-garden-architecture.mermaid.md)
Complete Mermaid diagram source files for the system architecture.

## Quick Links

- **Getting Started**: Start with [PDR.md](PDR.md) for complete deployment guide
- **Architecture Overview**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- **Adding Services**: Follow [HOWTO-ADD-SERVICES.md](HOWTO-ADD-SERVICES.md) for integration
- **Configuration Examples**: See [../examples/](../examples/) directory

## Documentation Structure

```
docs/
├── README.md (this file)
├── ARCHITECTURE.md          - System design and diagrams
├── PDR.md                   - Complete deployment guide
├── HOWTO-ADD-SERVICES.md   - Integration tutorials
├── NEXTERM-INSTALLATION.md - Nexterm setup guide
└── advanced/                - Deep-dive topics
    ├── dns-tool-architecture.md
    ├── dig-card.md
    └── walled-garden-architecture.mermaid.md
```

## Contributing

Found an error or want to improve the documentation? See [../CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
