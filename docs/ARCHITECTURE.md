# Modular Architecture

CAD Widgets follows a clean, modular architecture that separates concerns and promotes reusability.

## Project Structure

```
cad_widgets/
├── src/
│   └── cad_widgets/              # Main package
│       ├── __init__.py           # Package exports
│       ├── widgets/              # Widget components
│       │   ├── __init__.py
│       │   ├── ocp_widget.py     # Core 3D viewer widget
│       │   └── view_toolbar.py   # Reusable view controls
│       └── utils/                # Utility modules
│           ├── __init__.py
│           └── shapes.py         # Shape creation helpers
├── examples/                     # Example applications
│   ├── simple_example.py         # Minimal usage
│   └── example_modular.py        # Full modular app
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_widget.py
├── docs/                         # Documentation
│   └── ARCHITECTURE.md
├── pyproject.toml                # Project configuration
└── README.md
```

## Core Components

### OCPWidget

**Location**: `src/cad_widgets/widgets/ocp_widget.py`

The main 3D viewer widget that integrates OpenCascade with PySide6.

**Responsibilities**:
- Platform-specific window integration (Linux/X11, Windows, macOS)
- OpenCascade viewer initialization and management
- Shape display and manipulation
- Camera control (projection, viewing angles)
- Display mode management (shaded, wireframe, both)
- Mouse interaction handling (rotation, pan, zoom)
- Immediate rendering for flicker-free interaction

**Key Methods**:
- `display_shape(shape, color, transparency, update)` - Display a 3D shape
- `erase_all()` - Clear all shapes
- `fit_all()` - Fit all objects in view
- `set_projection(direction)` - Set standard view (top, front, iso, etc.)
- `set_projection_type(type)` - Set perspective or orthographic
- `set_display_mode(mode)` - Set shaded, wireframe, or both
- `get_context()`, `get_view()`, `get_viewer()` - Access OCC objects

**Usage**:
```python
from cad_widgets import OCPWidget

viewer = OCPWidget()
viewer.display_shape(shape, color=(1, 0, 0))
viewer.fit_all()
```

### ViewToolbar

**Location**: `src/cad_widgets/widgets/view_toolbar.py`

A reusable toolbar component providing view controls through Qt signals.

**Responsibilities**:
- Standard view selection (front, back, left, right, top, bottom, iso)
- Projection type control (perspective/orthographic)
- Display mode control (shaded/wireframe/both)
- Action buttons (fit all, clear)
- Signal emission for decoupled communication

**Qt Signals**:
- `projection_changed(str)` - Standard view changed
- `projection_type_changed(str)` - Projection type changed
- `display_mode_changed(str)` - Display mode changed
- `fit_all_requested()` - Fit all requested
- `clear_requested()` - Clear requested

**Usage**:
```python
from cad_widgets import OCPWidget, ViewToolbar

viewer = OCPWidget()
toolbar = ViewToolbar(orientation='vertical')

# Connect signals
toolbar.projection_changed.connect(viewer.set_projection)
toolbar.projection_type_changed.connect(viewer.set_projection_type)
toolbar.display_mode_changed.connect(viewer.set_display_mode)
```

### Shape Utilities

**Location**: `src/cad_widgets/utils/shapes.py`

Helper functions for creating and manipulating OpenCascade shapes.

**Functions**:
- `create_box(width, height, depth, position)` - Create box
- `create_sphere(radius, center)` - Create sphere
- `create_cylinder(radius, height, axis)` - Create cylinder
- `create_cone(radius1, radius2, height, axis)` - Create cone
- `create_torus(major_radius, minor_radius, position, direction)` - Create torus
- `translate_shape(shape, dx, dy, dz)` - Translate shape

**Usage**:
```python
from cad_widgets import GeometryService

geo = GeometryService()

# Create shapes with default position
box = geo.create_box(100, 50, 75)
sphere = geo.create_sphere(30)

# Transform shapes
sphere_moved = geo.translate_shape(sphere, 100, 0, 0)

# Create shapes with custom position and direction using tuples
cylinder = geo.create_cylinder(20, 60, position=(0, 0, 0), direction=(1, 0, 0))
```

## Architecture Patterns

### Signal-Based Communication

The ViewToolbar uses Qt signals to communicate with viewers, enabling loose coupling:

```python
# Toolbar emits signal
self.projection_changed.emit('front')

# Viewer responds to signal
toolbar.projection_changed.connect(viewer.set_projection)
```

**Benefits**:
- Decoupled components
- Easy to test independently
- Reusable in different contexts
- Multiple viewers can connect to one toolbar

### Immediate Rendering

The OCPWidget uses immediate rendering for smooth, flicker-free interaction:

```python
def _redraw_immediate(self):
    if self._view and not self._is_rendering:
        self._is_rendering = True
        self._view.Redraw()
        self._is_rendering = False
```

**Benefits**:
- No flickering during mouse interaction
- Smooth rotation, pan, and zoom
- Rendering lock prevents concurrent redraws

### Platform Abstraction

Platform-specific window creation is abstracted in OCPWidget:

```python
if sys.platform == "win32":
    from OCP.WNT import WNT_Window
    window = WNT_Window(self.winId())
elif sys.platform == "darwin":
    from OCP.Cocoa import Cocoa_Window
    window = Cocoa_Window(self.winId())
else:
    from OCP.Xw import Xw_Window
    window = Xw_Window(display_connection, self.winId())
```

## Extension Points

### Custom Toolbars

Create custom toolbars by extending or composing with ViewToolbar:

```python
class MyCustomToolbar(ViewToolbar):
    # Add custom features
    custom_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._add_custom_controls()
```

### Custom Viewers

Extend OCPWidget for specialized viewers:

```python
class CADAnalysisViewer(OCPWidget):
    def __init__(self):
        super().__init__()
        self._setup_analysis_tools()
    
    def analyze_shape(self, shape):
        # Custom analysis logic
        pass
```

### Shape Utilities

Add custom shape creation functions:

```python
# In your code or contribute to shapes.py
def create_custom_shape(params):
    # Use OCP primitives
    shape = ...
    return shape
```

## Testing

Tests are organized in the `tests/` directory:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_widget.py -v

# Run with coverage
pytest tests/ --cov=cad_widgets
```

## Best Practices

### 1. Use GeometryService

Prefer GeometryService over direct OCP calls for shape creation:

```python
# Good - Clean Python API with tuples
from cad_widgets import GeometryService
geo = GeometryService()
box = geo.create_box(100, 100, 100)
cylinder = geo.create_cylinder(20, 60, position=(0, 0, 0), direction=(0, 0, 1))

# Works but less readable and requires OCP knowledge
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
box = BRepPrimAPI_MakeBox(100, 100, 100).Shape()
axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
```

### 2. Connect Signals for Modular Design

Use signals for component communication:

```python
# Good - decoupled
toolbar.projection_changed.connect(viewer.set_projection)

# Avoid - tight coupling
def on_button_click():
    viewer.set_projection('front')
```

### 3. Batch Shape Updates

Use `update=False` when displaying multiple shapes:

```python
# Good - single update
viewer.display_shape(shape1, update=False)
viewer.display_shape(shape2, update=False)
viewer.fit_all()  # Triggers update

# Avoid - multiple updates
viewer.display_shape(shape1)  # Redraws
viewer.display_shape(shape2)  # Redraws again
```

### 4. Handle Platform Differences

The library handles platform differences internally, but be aware of edge cases in your applications.

## Migration Guide

### From Inline Controls to Modular Architecture

**Before**:
```python
# All controls in main window
class MyWindow(QMainWindow):
    def __init__(self):
        self.viewer = OCPWidget()
        # Create buttons, connect directly
        btn = QPushButton("Front")
        btn.clicked.connect(lambda: self.viewer.set_projection('front'))
```

**After**:
```python
# Using ViewToolbar
class MyWindow(QMainWindow):
    def __init__(self):
        self.viewer = OCPWidget()
        self.toolbar = ViewToolbar()
        self.toolbar.projection_changed.connect(self.viewer.set_projection)
```

**Benefits**:
- Less boilerplate code
- Reusable toolbar component
- Cleaner separation of concerns
- Easier to test

## Performance Considerations

### Rendering

- Immediate rendering is used for interactive operations
- Use `update=False` when adding multiple shapes
- Call `fit_all()` once after batch operations

### Memory

- Clear unused shapes with `erase_all()`
- Cache commonly used shapes when appropriate

### Threading

- Qt widgets must be used from the main thread
- OpenCascade operations are generally thread-safe
- Consider using QThread for heavy computations

## Future Extensions

Potential areas for extension:

1. **Additional Widgets**: Measurement tools, sectioning planes, etc.
2. **File I/O**: STEP, IGES, STL import/export
3. **Analysis Tools**: Volume, surface area, center of mass
4. **Annotations**: Dimensions, labels, callouts
5. **Selection**: Advanced shape selection and highlighting
6. **Rendering**: Custom materials, lighting, shadows

## Contributing

When contributing to the architecture:

1. Maintain separation of concerns
2. Use signals for inter-component communication
3. Add utilities to the `utils/` package
4. Write tests for new features
5. Update documentation
6. Follow existing code style (use `ruff` for formatting)
