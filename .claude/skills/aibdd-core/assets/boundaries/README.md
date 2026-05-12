# Boundary Preset Assets

This directory is the AIBDD core SSOT for reusable boundary preset assets.

## Layout

```text
assets/boundaries/
  web-backend/
    handler-routing.yml
    shared-dsl-template.yml
    handlers/
    variants/
  schemas/
```

## Rules

- `L4.preset.name` resolves directly to a same-named folder under this directory.
- `web-backend` is the folder name and preset name; there is no `backend` alias.
- Consumers must fail-stop when a preset name, handler, or variant cannot be resolved here.
- Project-owned runtime instructions do not live in this directory.
