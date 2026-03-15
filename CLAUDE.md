# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses `uv` for package management and `invoke` as a task runner.

```bash
# Setup
uv sync
source .venv/bin/activate

# Run all checks (lint → typecheck → test)
invoke check

# Individual checks
invoke lint          # ruff linter
invoke format        # ruff formatter
invoke typecheck     # mypy
invoke test          # pytest
invoke test_cov      # pytest with coverage report

# Run a single test
pytest tests/test_geometry_manager.py::test_create_box_shape -v

# Run tests excluding Windows-only tests
pytest tests/ --ignore=tests/test_windows_window.py
```

Tests require a display (use `xvfb-run` on headless Linux).

## Architecture

Four-layer architecture with signal-based loose coupling:

```
Widget Layer → Manager Layer → Service Layer → Models Layer
                    ↓
              Qt signals (loose coupling between layers)
```

**Models** (`src/cad_widgets/models/`) — Dataclasses for shape properties (`BoxProperties`, `SphereProperties`, etc.), each with `Translation(x,y,z)` and `Rotation(x,y,z)` fields. Support `to_dict()`/`from_dict()` serialization.

**Services** (`src/cad_widgets/services/`) — Business logic with no Qt widget dependencies:
- `GeometryService` — shape creation (box, sphere, cylinder, cone, torus), boolean ops (fuse/cut), file I/O (STEP/IGES). Implements `GeometryServiceProtocol` for DI in tests.
- `ViewService` — camera, display modes, shape rendering, shape registry.
- `SelectionService` — selection modes and entity picking.

**Managers** (`src/cad_widgets/managers/`) — Orchestration layer. `GeometryManager` maintains a shape registry of `ManagedShape` dataclasses and emits Qt signals (`shape_created`, `shape_updated`, `shape_removed`, `all_cleared`) when state changes.

**Widgets** (`src/cad_widgets/widgets/`) — PySide6 UI components:
- `OCPWidget` — core 3D viewer integrating OpenCascade (OCP) with Qt. Handles platform-specific window embedding (X11/Windows/macOS) and mouse interactions.
- `GeometryTreeWidget` — tree view for shape management with visibility controls.
- `PropertyEditorWidget` — editable shape property panel.
- `ViewToolbar` / `SelectionToolbar` — emit signals consumed by services.

## Key Design Decisions

- Widgets communicate via Qt signals only — no direct widget-to-widget dependencies.
- `GeometryServiceProtocol` (in `services/`) enables mock injection in unit tests without a display.
- `ManagedShape` tracks shape type, color, properties, and parent/child relationships for boolean operations.
- Enums (`src/cad_widgets/enums.py`) define `ViewDirection`, `ProjectionType`, `DisplayMode`, `SelectionMode`, and `ShapeType`.