# CAD Widgets

A Python library for building 3D CAD features with PySide6 and OpenCascade (OCP). Features a clean, modular architecture with reusable components and signal-based communication.

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🎨 **Modular Architecture** - Layered design with widgets, services, managers, and models
- 🖱️ **Mouse Interactions** - Rotation, panning, and zooming
- 🎯 **Multiple View Modes** - Perspective/orthographic projections, standard views
- 🎨 **Display Modes** - Shaded, wireframe, or combination rendering
- 🌳 **Geometry Management** - Tree view with visibility controls and property editing
- ✂️ **Boolean Operations** - Union and subtraction operations
- 🎯 **Advanced Selection** - Volume, surface, edge, and vertex selection modes
- 🔧 **Shape Creation** - Clean API for boxes, spheres, cylinders, cones, and tori
- 📁 **Import/Export** - STEP and IGES file format support
- 🧪 **Well Tested** - Comprehensive test suite with >70% coverage
- 📚 **Documented** - Extensive documentation and examples
- 🖥️ **Cross-Platform** - Works on Linux (X11) and Windows

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd cad_widgets

# Install dependencies using uv (recommended)
uv sync
source .venv/bin/activate

# Or using pip
pip install -e .
```

### Simple Example

```python
from PySide6.QtWidgets import QApplication
from cad_widgets import OCPWidget, GeometryService, DisplayMode

app = QApplication([])

viewer = OCPWidget()
viewer.resize(800, 600)

geo = GeometryService()
box = geo.create_box(100, 100, 100)
viewer.set_display_mode(DisplayMode.SHADED)
viewer.display_shape(box, 'box_id', color=(0.8, 0.2, 0.2))
viewer.fit_all()

viewer.show()
app.exec()
```

### Running Examples

```bash
# Full-featured modular example with all widgets
python examples/full_featured_example.py
```

## Architecture

CAD Widgets follows a clean, layered architecture with clear separation of concerns:

- **Widget Layer** - UI components (OCPWidget, toolbars, tree view, property editor)
- **Manager Layer** - High-level orchestration (GeometryManager)
- **Service Layer** - Business logic (GeometryService, ViewService, SelectionService)
- **Models Layer** - Data structures (ShapeProperties, Translation, Rotation)

Components communicate through Qt signals for loose coupling and reusability. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architectural documentation including patterns, component details, and extension points.

## Mouse Controls

- **Left Click + Drag**: Rotate view
- **Middle Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out

## API Reference

For a complete API reference including all widget methods, signals, service methods, and enums, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#api-reference).

## Key Features

### Import/Export

Support for standard CAD file formats:
- **STEP** (`.step`, `.stp`) - ISO 10303 standard
- **IGES** (`.iges`, `.igs`) - Initial Graphics Exchange Specification

```python
from cad_widgets import GeometryService, GeometryManager

# Export shapes
geo = GeometryService()
box = geo.create_box(100, 100, 100)
GeometryService.export_step(box, "output.step")
GeometryService.export_iges(box, "output.iges")

# Import shapes (automatically detects STEP or IGES based on extension)
# Option 1: Using GeometryService directly
imported_shape = GeometryService.import_file("input.step")

# Option 2: Using GeometryManager (recommended for full integration)
manager = GeometryManager()
# Name will be auto-generated as "IMPORTED_1", "IMPORTED_2", etc.
manager.import_shape(filename="input.step", color=(0.5, 0.5, 0.8))
```

## Dependencies

- **PySide6** ≥ 6.6.0 - Qt for Python GUI framework
- **cadquery-ocp** ≥ 7.7.0 - OpenCascade Python bindings
- **numpy** ≥ 1.24.0 - Numerical operations

## Development

### Quick Start

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=cad_widgets

# Type check
mypy src/cad_widgets

# Lint and format
ruff check src tests examples
ruff format src tests examples

# Run all checks
uv run invoke check
```

For detailed development guidelines, testing strategies, and contributing instructions, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#testing).

## Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed architecture documentation
- **Examples** - See `examples/` directory for complete applications

## Contributing

Contributions are welcome! Please:

1. Follow the existing architecture patterns
2. Use signals for component communication
3. Add tests for new features
4. Update documentation
5. Run `ruff check --fix` before committing

## License

This project is provided as-is for educational and development purposes.

## Resources

- [OCP Documentation](https://github.com/CadQuery/OCP)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [OpenCascade Documentation](https://dev.opencascade.org/)

## Acknowledgments

Built with:
- [OpenCascade](https://www.opencascade.com/) - 3D modeling kernel
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt for Python
- [CadQuery OCP](https://github.com/CadQuery/OCP) - Python bindings for OpenCascade
