# CAD Widgets

A Python library for building 3D CAD viewers with PySide6 and OpenCascade (OCP). Features a clean, modular architecture with reusable components and signal-based communication.

![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 🎨 **Modular Architecture** - Reusable components with clean separation of concerns
- 🖱️ **Smooth Interaction** - Flicker-free rotation, panning, and zooming
- 🎯 **Multiple View Modes** - Perspective/orthographic projections, standard views
- 🎨 **Display Modes** - Shaded, wireframe, or combination rendering
- 🔧 **Utility Functions** - Helper functions for common shape operations
- 🧪 **Well Tested** - Comprehensive test suite
- 📚 **Documented** - Extensive documentation and examples
- 🖥️ **Cross-Platform** - Works on Linux (X11), Windows, and macOS

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
from cad_widgets import OCPWidget, GeometryService

app = QApplication([])

viewer = OCPWidget()
viewer.resize(800, 600)

geo = GeometryService()
box = geo.create_box(100, 100, 100)
viewer.display_shape(box, color=(0.8, 0.2, 0.2))
viewer.fit_all()

viewer.show()
app.exec()
```

### Running Examples

```bash
# Simple box example
python examples/simple_example.py

# Full modular example with toolbar
python examples/example_modular.py
```

## Project Structure

```
cad_widgets/
├── src/
│   └── cad_widgets/              # Main package
│       ├── widgets/              # Widget components
│       │   ├── ocp_widget.py     # Core 3D viewer
│       │   └── view_toolbar.py   # View controls toolbar
│       └── utils/                # Utilities
│           └── shapes.py         # Shape creation helpers
├── examples/                     # Example applications
├── tests/                        # Test suite
├── docs/                         # Documentation
└── pyproject.toml               # Project configuration
```

## Architecture

### Core Components

#### OCPWidget

The main 3D viewer widget integrating OpenCascade with PySide6.

```python
from cad_widgets import OCPWidget

viewer = OCPWidget()
viewer.display_shape(shape, color=(1, 0, 0), transparency=0.5)
viewer.set_projection('front')
viewer.set_projection_type('orthographic')
viewer.set_display_mode('wireframe')
viewer.fit_all()
```

**Key Features**:
- Platform-specific window integration
- Immediate rendering for smooth interaction
- Multiple projection types and display modes
- Standard view presets (front, top, iso, etc.)

#### ViewToolbar

Reusable toolbar component with signal-based communication.

```python
from cad_widgets import OCPWidget, ViewToolbar

viewer = OCPWidget()
toolbar = ViewToolbar(orientation='vertical')

# Connect signals
toolbar.projection_changed.connect(viewer.set_projection)
toolbar.projection_type_changed.connect(viewer.set_projection_type)
toolbar.display_mode_changed.connect(viewer.set_display_mode)
toolbar.fit_all_requested.connect(viewer.fit_all)
toolbar.clear_requested.connect(viewer.erase_all)
```

**Features**:
- Standard view controls
- Projection type selection
- Display mode selection
- Fit all and clear actions
- Qt signals for loose coupling

#### Shape Utilities

Helper service for creating and manipulating shapes.

```python
from cad_widgets import GeometryService

geo = GeometryService()

# Create shapes with simple parameters
box = geo.create_box(100, 50, 75)
sphere = geo.create_sphere(30)

# Create shapes with custom position using tuples
sphere_moved = geo.create_sphere(30, center=(100, 0, 0))
box_positioned = geo.create_box(50, 50, 50, position=(50, 0, 0))

# Create shapes with custom direction using tuples
cylinder = geo.create_cylinder(20, 60, position=(0, 0, 0), direction=(0, 0, 1))

# Transform shapes
translated = geo.translate_shape(box, 100, 0, 0)
```

## Mouse Controls

- **Left Click + Drag**: Rotate view
- **Middle Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out

## API Reference

### OCPWidget Methods

- `display_shape(shape, color=None, transparency=0.0, update=True)` - Display a shape
- `erase_all()` - Clear all shapes
- `fit_all()` - Fit all objects in view
- `update_display()` - Refresh the display
- `set_projection(direction)` - Set view ('top', 'front', 'iso', etc.)
- `set_projection_type(type)` - Set 'perspective' or 'orthographic'
- `set_display_mode(mode)` - Set 'shaded', 'wireframe', or 'both'
- `get_context()` - Get AIS_InteractiveContext
- `get_view()` - Get V3d_View
- `get_viewer()` - Get V3d_Viewer

### ViewToolbar Signals

- `projection_changed(str)` - Standard view changed
- `projection_type_changed(str)` - Projection type changed
- `display_mode_changed(str)` - Display mode changed
- `fit_all_requested()` - Fit all requested
- `clear_requested()` - Clear requested

## Dependencies

- **PySide6** ≥ 6.6.0 - Qt for Python GUI framework
- **cadquery-ocp** ≥ 7.7.0 - OpenCascade Python bindings
- **numpy** ≥ 1.24.0 - Numerical operations

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=cad_widgets

# Run specific test
pytest tests/test_widget.py -v
```

### Type Checking

Type checking with mypy is configured and enabled:

```bash
# Run type checker
mypy src/cad_widgets

# Or using invoke
uv run invoke typecheck
```

The project uses PEP 561 typing and includes a `py.typed` marker. Configuration is in `pyproject.toml`.

### Code Formatting and Linting

```bash
# Check code with ruff
ruff check src tests examples

# Auto-fix issues
ruff check --fix src tests examples

# Format code
ruff format src tests examples

# Or using invoke
uv run invoke lint
uv run invoke format
```

### Development Tasks

The project includes invoke tasks for common operations:

```bash
# Run all checks (lint, typecheck, test)
uv run invoke check

# Individual tasks
uv run invoke test           # Run tests
uv run invoke test --verbose # Run tests with verbose output
uv run invoke test-cov       # Run tests with coverage
uv run invoke typecheck      # Run mypy
uv run invoke lint           # Run ruff linting
uv run invoke format         # Format code
uv run invoke clean          # Clean generated files
```

## Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed architecture documentation
- **Examples** - See `examples/` directory for complete applications

## Troubleshooting

### Qt DBus Warnings (Linux)

Suppress harmless DBus warnings:

```bash
export QT_LOGGING_RULES='qt.qpa.theme.gnome=false'
python examples/example_modular.py
```

Or in code:

```python
import os
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.theme.gnome=false'
```

### Import Errors

Ensure dependencies are installed:

```bash
uv sync  # or pip install -e .
```

### Display Issues

- Verify OpenGL support is available on your system
- Check console for error messages
- Try different Qt platform plugins if available

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
