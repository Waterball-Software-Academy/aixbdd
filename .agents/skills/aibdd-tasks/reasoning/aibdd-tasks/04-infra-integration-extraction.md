# 04 — Infra and Integration Extraction

## Goal

Extract the opening `Infra setup` phase and the closing `Integration` phase from plan artifacts.

## Infra Heuristics

Treat an item as infra when it is:

- shared by multiple feature phases
- foundational plumbing
- runner / skeleton / repository-base / shared DTO / common setup work

## Integration Heuristics

Treat an item as integration when it is:

- cross-feature stitching
- end-to-end verification
- final regression
- cross-slice cleanup or handoff

## No-Work Policy

If no meaningful infra or integration item exists, return the explicit no-work sentence rather than an empty section.
