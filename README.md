# OCP PySide6 CAD Viewer

A Python project integrating OpenCascade (via OCP bindings) with PySide6 to create interactive 3D CAD visualization widgets.

## Features

- **3D Viewer Widget**: Custom PySide6 widget for displaying OpenCascade 3D shapes
- **Smooth Interactive Navigation**: 
  - Left mouse button: Rotate view (smooth, no flickering)
  - Middle mouse button: Pan view (smooth, no flickering)
  - Mouse wheel: Zoom in/out (smooth, no flickering)
- **Optimized Rendering**: Immediate rendering mode for flicker-free interactions
- **Shape Display**: Support for displaying various 3D primitives (boxes, spheres, cylinders, cones, torus)
- **Customization**: Configurable colors and transparency for shapes
- **View Controls**: Multiple predefined views (ISO, Top, Front, etc.)
- **Display Modes**: Shaded, wireframe, or both combined
- **Projection Types**: Perspective and orthographic views
- **Modular Architecture**: Reusable ViewToolbar component with signal-based communication
- **Platform Support**: Works on Windows, Linux (X11), and macOS

## Requirements

- Python 3.8 or higher
- PySide6
- cadquery-ocp (OpenCascade Python bindings)
- numpy

## Installation

1. Clone or download this repository:
```bash
cd /home/gustavo/OpenSource/cad_widgets
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Test

Run the simple test to verify the installation works:

```bash
python simple_test.py
```

This will display a single red box in the viewer - a quick way to test that everything is working correctly.

### Running the Examples

**Basic Example** - Simple inline controls:
```bash
python example.py
```

**Modular Example** - Using reusable ViewToolbar component:
```bash
python example_modular.py
```

The examples display several 3D shapes:
- Red box (50x50x50)
- Green sphere (radius 30)
- Blue cylinder (radius 20, height 60)
- Yellow cone
- Purple torus
- Cyan transparent box

**Projection Demo** - Focus on projection and display modes:
```bash
python projection_demo.py
```

### Using the Widget in Your Own Application

#### Basic Usage

Here's a simple example of how to use the `OCPWidget` in your own PySide6 application:

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from ocp_widget import OCPWidget
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

app = QApplication([])
window = QMainWindow()

# Create the viewer widget
viewer = OCPWidget()
window.setCentralWidget(viewer)

# Create and display a shape
box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()
viewer.display_shape(box, color=(0.8, 0.2, 0.2))

# Fit the view
viewer.fit_all()

window.show()
app.exec()
```

#### Modular Usage with ViewToolbar

For a more modular approach with reusable components:

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt
from ocp_widget import OCPWidget
from view_toolbar import ViewToolbar
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

app = QApplication([])
window = QMainWindow()

# Create main widget with splitter layout
main_widget = QWidget()
splitter = QSplitter(Qt.Horizontal)

# Create the viewer and toolbar
viewer = OCPWidget()
toolbar = ViewToolbar()

# Add to splitter
splitter.addWidget(viewer)
splitter.addWidget(toolbar)
splitter.setSizes([900, 300])

# Connect signals
toolbar.projection_changed.connect(viewer.set_projection)
toolbar.projection_type_changed.connect(viewer.set_projection_type)
toolbar.display_mode_changed.connect(viewer.set_display_mode)
toolbar.fit_all_requested.connect(viewer.fit_all)
toolbar.clear_requested.connect(viewer.erase_all)

# Setup layout
layout = QVBoxLayout(main_widget)
layout.addWidget(splitter)
window.setCentralWidget(main_widget)

# Create and display a shape
box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()
viewer.display_shape(box, color=(0.8, 0.2, 0.2))
viewer.fit_all()

window.show()
app.exec()
```


## Widget API

### OCPWidget Class

#### Methods

- `display_shape(shape, color=None, transparency=0.0, update=True)`
  - Display an OCP shape in the viewer
  - **shape**: OCP TopoDS_Shape object
  - **color**: RGB tuple (0-1) or None for default
  - **transparency**: Float 0-1
  - **update**: Whether to update the display
  - Returns: AIS_Shape object

- `erase_all()`
  - Remove all shapes from the display

- `fit_all()`
  - Fit all displayed objects in the view

- `update_display()`
  - Refresh the display

- `set_projection(direction)`
  - Set view direction
  - **direction**: 'top', 'bottom', 'left', 'right', 'front', 'back', or 'iso'

- `set_projection_type(projection_type)`
  - Set camera projection type
  - **projection_type**: 'perspective' or 'orthographic'

- `set_display_mode(mode)`
  - Set shape display mode
  - **mode**: 'shaded', 'wireframe', or 'both'

- `get_context()`
  - Get the AIS interactive context

- `get_view()`
  - Get the V3d view

- `get_viewer()`
  - Get the V3d viewer

### ViewToolbar Class

#### Signals

- `projection_changed(str)` - Emitted when standard view changes (e.g., 'front', 'top', 'iso')
- `projection_type_changed(str)` - Emitted when projection type changes ('perspective', 'orthographic')
- `display_mode_changed(str)` - Emitted when display mode changes ('shaded', 'wireframe', 'both')
- `fit_all_requested()` - Emitted when fit all button is clicked
- `clear_requested()` - Emitted when clear button is clicked

#### Methods

- `set_projection(direction)`
  - Programmatically change the standard view selection
  - **direction**: 'top', 'bottom', 'left', 'right', 'front', 'back', or 'iso'

- `set_projection_type(projection_type)`
  - Programmatically change the projection type
  - **projection_type**: 'perspective' or 'orthographic'

- `set_display_mode(mode)`
  - Programmatically change the display mode
  - **mode**: 'shaded', 'wireframe', or 'both'


## Project Structure

```
cad_widgets/
├── ocp_widget.py              # Main OCP widget class
├── view_toolbar.py            # Reusable view toolbar component
├── example.py                 # Basic example with inline controls
├── example_modular.py         # Modular example using ViewToolbar
├── projection_demo.py         # Projection and display mode demo
├── simple_test.py             # Simple test with a single box
├── requirements.txt           # Python dependencies
├── __init__.py                # Package initialization
├── README.md                  # This file
├── QUICKSTART.md              # Quick start guide
└── MODULAR_ARCHITECTURE.md    # Architecture documentation
```

## Architecture

The project follows a modular design with separated concerns:

### Core Components

- **OCPWidget** ([ocp_widget.py](ocp_widget.py))
  - Core 3D viewer widget integrating OpenCascade with PySide6
  - Platform-specific window integration (Linux/X11, Windows, macOS)
  - Immediate rendering for flicker-free interaction
  - Shape display and management

- **ViewToolbar** ([view_toolbar.py](view_toolbar.py))
  - Reusable toolbar component for view controls
  - Signal-based communication with viewers
  - Controls for:
    - Standard views (front, back, left, right, top, bottom, isometric)
    - Projection types (perspective, orthographic)
    - Display modes (shaded, wireframe, both)
    - Fit all and clear operations

### Examples

- **example.py** - Basic example with inline controls
- **example_modular.py** - Demonstrates modular architecture using ViewToolbar
- **projection_demo.py** - Focus on projection and display mode features

For detailed architecture documentation, see [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md).


## Creating Different Shapes

The OCP library provides various shape creation primitives:

```python
from OCP.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeTorus,
)
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir

# Box
box = BRepPrimAPI_MakeBox(width, height, depth).Shape()

# Sphere
sphere = BRepPrimAPI_MakeSphere(radius).Shape()

# Cylinder (requires axis)
axis = gp_Ax2(gp_Pnt(x, y, z), gp_Dir(dx, dy, dz))
cylinder = BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()

# Cone
cone = BRepPrimAPI_MakeCone(axis, radius1, radius2, height).Shape()

# Torus
torus = BRepPrimAPI_MakeTorus(axis, major_radius, minor_radius).Shape()
```

## Troubleshooting

### Common Issues

1. **ImportError for OCP modules**
   - Make sure `cadquery-ocp` is installed: `pip install cadquery-ocp`

2. **Qt DBus warnings on Linux** (harmless)
   - You may see warnings like `qt.qpa.theme.gnome: dbus reply error`
   - These are harmless and related to Gnome theme settings
   - To suppress them, set environment variable before running:
     ```bash
     export QT_LOGGING_RULES='qt.qpa.theme.gnome=false'
     python example.py
     ```
   - Or add this in your Python code before creating QApplication:
     ```python
     import os
     os.environ['QT_LOGGING_RULES'] = 'qt.qpa.theme.gnome=false'
     ```

3. **Qt platform plugin error**
   - Ensure your system has the necessary Qt platform plugins
   - On Linux: May need to install `libxcb-xinerama0` or similar libraries

4. **Display not showing**
   - The viewer initialization is platform-dependent
   - Check console for error messages
   - Some OpenGL drivers may have compatibility issues

### Rendering Performance

The widget uses **immediate rendering mode** for interactive operations (rotation, panning, zooming), which provides:
- **Flicker-free** smooth interactions
- **No screen tearing** during movement
- **Concurrent rendering protection** to prevent visual artifacts
- **Optimized paint events** that only redraw when necessary

This is achieved through a rendering lock mechanism and direct OpenCascade rendering that bypasses Qt's standard paint queue for interactive operations.

### Platform-Specific Notes

- **Linux**: May require X11 libraries
- **Windows**: Should work out of the box with standard Python installation
- **macOS**: May require specific Qt configuration

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is provided as-is for educational and development purposes.

## Resources

- [OCP Documentation](https://github.com/CadQuery/OCP)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [OpenCascade Documentation](https://dev.opencascade.org/)

## Author

Created as a demonstration of integrating OpenCascade with PySide6 for 3D CAD visualization.
