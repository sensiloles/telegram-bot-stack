# Documentation

Complete documentation for `telegram-bot-stack` framework.

> **Note:** This directory contains **user-facing documentation** for framework users.
>
> For **contributor documentation** (GitHub workflows, automation, development process), see [`.github/docs/`](../.github/docs/).

## Quick Navigation

### Getting Started

New to the framework? Start here:

- **[Installation Guide](installation.md)** - Install the framework
- **[Quick Start Guide](quickstart.md)** - Build your first bot in minutes
- **[Windows Setup Guide](windows-setup.md)** - Complete Windows developer guide

### Guides

In-depth guides for specific topics:

- **[Deployment Guide](deployment_guide.md)** - Deploy bots to VPS in one command
- **[Storage Guide](storage_guide.md)** - Storage backends and data persistence
- **[Migration Guide](migration_guide.md)** - Upgrade between versions
- **[Private Installation](private_installation.md)** - Install from private sources

### Reference

Technical reference documentation:

- **[API Reference](api_reference.md)** - Complete API documentation
- **[Architecture](architecture.md)** - System design and patterns
- **[CLI Specification](cli-specification.md)** - Command-line tool specification

## Documentation Structure

```
docs/
├── README.md                    # This file - navigation hub
├── installation.md             # Getting Started
├── quickstart.md               # Getting Started
├── windows-setup.md            # Getting Started - Windows
├── deployment_guide.md         # Guides - VPS deployment
├── storage_guide.md            # Guides
├── migration_guide.md          # Guides
├── private_installation.md     # Guides
├── api_reference.md            # Reference
├── architecture.md             # Reference
└── cli-specification.md       # Reference
```

## Documentation Groups

### Getting Started (Critical)

Essential documentation for new users:

- **Installation** - Setup instructions
- **Quick Start** - First bot tutorial
- **Windows Setup** - Complete Windows developer guide

### Guides (High Priority)

Detailed guides for specific use cases:

- **Deployment Guide** - Deploy bots to production (VPS, Docker, Systemd)
- **Storage Guide** - Choose and use storage backends
- **Migration Guide** - Upgrade your bot
- **Private Installation** - Install from private repositories

### Reference (High Priority)

Technical documentation:

- **API Reference** - Complete API documentation
- **Architecture** - Design decisions and patterns
- **CLI Specification** - Command-line tool reference

## Documentation Relationships

### Quick Start Flow

```
installation.md → quickstart.md → deployment_guide.md → api_reference.md
                              → architecture.md
```

### Storage Flow

```
storage_guide.md → api_reference.md
migration_guide.md → storage_guide.md
```

### Architecture Flow

```
architecture.md → api_reference.md
               → storage_guide.md
```

## For Contributors

When updating documentation:

1. **API Changes** → Update `api_reference.md`
2. **New Features** → Update relevant guide or create new one
3. **Breaking Changes** → Update `migration_guide.md`
4. **Architecture Changes** → Update `architecture.md`
5. **Installation Changes** → Update `installation.md` and `private_installation.md`

## See Also

- [Main README](../README.md) - Project overview
- [Project Status](../.github/PROJECT_STATUS.md) - Current phase and progress
- [Examples](../examples/) - Example bots
- [GitHub Automation](../.github/workflows/scripts/README.md) - Automation scripts

---

**Last Updated:** November 2025
