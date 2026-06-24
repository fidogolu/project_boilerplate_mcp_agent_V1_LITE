# Code Documentation

This directory contains technical documentation for the Secure Agent Boilerplate.

## Architecture Diagrams

- [`architecture.mermaid`](docs/architecture.mermaid) — Main architecture flow
- [`flux-certificats.mermaid`](docs/flux-certificats.mermaid) — Certificate flow (legacy)
- [`sequence_certificats.mermaid`](docs/sequence_certificats.mermaid) — Certificate sequence (legacy)

## Network Architecture

- [`ARCHITECTURE_RESEAU_AUTH.md`](docs/ARCHITECTURE_RESEAU_AUTH.md) — Network authentication (legacy)

## How to View Mermaid Diagrams

```bash
# Install MMD CLI
npm install -g @mermaid-js/mermaid-cli

# Render to PNG
mmdc -i docs/architecture.mermaid -o docs/architecture.png

# Render to SVG
mmdc -i docs/architecture.mermaid -o docs/architecture.svg
```

Or view directly in GitHub with the [Mermaid Live Editor](https://mermaid.live).
