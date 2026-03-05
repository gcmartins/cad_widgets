# Architecture Documentation

CAD Widgets follows a clean, layered architecture that separates UI components, business logic, and data access.

## Project Structure

```
cad_widgets/
├── src/
│   └── cad_widgets/                     # Main package
│       ├── __init__.py                  # Package exports
│       ├── enums.py                     # Enums (ViewDirection, DisplayMode, etc.)
│       ├── py.typed                     # PEP 561 typing marker
│       ├── widgets/                     # UI Widget Layer
│       │   ├── __init__.py
│       │   ├── ocp_widget.py            # Core 3D viewer widget
│       │   ├── view_toolbar.py          # View controls toolbar
│       │   ├── selection_toolbar.py     # Selection mode controls
│       │   ├── geometry_tree.py         # Geometry tree view
│       │   └── property_editor.py       # Shape property editor
│       ├── services/                    # Service Layer
│       │   ├── __init__.py
│       │   ├── geometry_service.py      # Shape creation/manipulation
│       │   ├── view_service.py          # View and display management
│       │   └── selection_service.py     # Selection handling
│       ├── managers/                    # Business Logic Layer
│       │   ├── __init__.py
│       │   └── geometry_manager.py      # Geometry lifecycle management
│       └── models/                      # Data Models
│           ├── __init__.py
│           └── shape_properties.py      # Property classes
├── examples/                            # Example applications
│   └── example_modular.py               # Full-featured demo app
├── tests/                               # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_widget.py
│   ├── test_geometry_manager.py
│   └── ...
├── docs/                                # Documentation
│   └── ARCHITECTURE.md                  # This file
├── pyproject.toml                       # Project configuration
└── README.md
```

## Architectural Layers

### 1. Widget Layer (`widgets/`)

UI components built on PySide6 that provide visual interfaces and user interactions.

- **OCPWidget**: Core 3D viewer widget
- **ViewToolbar**: View control toolbar
- **SelectionToolbar**: Selection mode toolbar
- **GeometryTreeWidget**: Tree view for managing shapes
- **PropertyEditorWidget**: Property editing panel

### 2. Service Layer (`services/`)

Business logic services that handle specific domains without UI concerns.

- **GeometryService**: Shape creation, geometric operations, and file I/O
- **ViewService**: Camera, display, and rendering management
- **SelectionService**: Entity selection and highlighting

**File Format Support**:
- **STEP** (`.step`, `.stp`) - ISO 10303 standard for CAD data exchange
- **IGES** (`.iges`, `.igs`) - Initial Graphics Exchange Specification

### 3. Manager Layer (`managers/`)

High-level orchestration and state management.

- **GeometryManager**: Manages geometry lifecycle, properties, and state

### 4. Models Layer (`models/`)

Data classes representing domain entities.

- **ShapeProperties**: Base and specialized property classes
- **Translation/Rotation**: Transform data classes

## Core Components

### Widget Layer

#### OCPWidget

**Location**: `src/cad_widgets/widgets/ocp_widget.py`

The main 3D viewer widget that integrates OpenCascade with PySide6.

**Responsibilities**:
- Platform-specific window integration (Linux/X11, Windows, macOS)
- OpenCascade viewer initialization and management
- Delegates shape operations to ViewService
- Delegates selection to SelectionService
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

#### ViewToolbar

**Location**: `src/cad_widgets/widgets/view_toolbar.py`

Reusable toolbar providing view controls through Qt signals.

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
toolbar.fit_all_requested.connect(viewer.fit_all)
toolbar.clear_requested.connect(viewer.erase_all)
```

#### SelectionToolbar

**Location**: `src/cad_widgets/widgets/selection_toolbar.py`

Toolbar for controlling selection modes (volumes, surfaces, edges, vertices).

**Responsibilities**:
- Selection mode control through combo box
- Signal-based communication with OCPWidget

**Qt Signals**:
- `selection_mode_changed(str)` - Selection mode changed

**Usage**:
```python
from cad_widgets import OCPWidget, SelectionToolbar

viewer = OCPWidget()
selection_toolbar = SelectionToolbar()
selection_toolbar.selection_mode_changed.connect(viewer.set_selection_mode)
```

#### GeometryTreeWidget

**Location**: `src/cad_widgets/widgets/geometry_tree.py`

Tree view widget for managing geometry in a hierarchical structure.

**Responsibilities**:
- Display shapes in tree structure
- Show/hide shapes via checkboxes
- Shape selection synchronization
- Context menu for operations (delete, union, subtract)
- Create new shapes menu

**Qt Signals**:
- `shape_visibility_changed(str, bool)` - Shape visibility toggled
- `shape_selected(str)` - Shape selected in tree
- `shape_deleted(str)` - Shape deletion requested
- `clear_all_requested()` - Clear all requested
- `shape_creation_requested(ShapeType)` - New shape requested
- `shapes_union_requested(list)` - Boolean union requested
- `shapes_subtract_requested(list)` - Boolean subtraction requested
- `export_step_requested(str)` - Export shape to STEP file
- `export_iges_requested(str)` - Export shape to IGES file
- `import_step_requested()` - Import STEP file
- `import_iges_requested()` - Import IGES file

**Usage**:
```python
from cad_widgets import GeometryTreeWidget

tree = GeometryTreeWidget()
tree.shape_visibility_changed.connect(handle_visibility)
tree.shape_selected.connect(handle_selection)
tree.add_shape("shape_1", "Box", "Box", visible=True)
```

#### PropertyEditorWidget

**Location**: `src/cad_widgets/widgets/property_editor.py`

Widget for editing shape properties including dimensions, position, and rotation.

**Responsibilities**:
- Display and edit shape size parameters (width, height, radius, etc.)
- Edit translation (x, y, z)
- Edit rotation (x, y, z angles in degrees)
- Emit signals when properties change

**Qt Signals**:
- `properties_changed(str, dict)` - Properties modified

**Usage**:
```python
from cad_widgets import PropertyEditorWidget, BoxProperties

editor = PropertyEditorWidget()
editor.properties_changed.connect(handle_property_change)

# Set properties for editing
properties = BoxProperties(width=100, height=50, depth=75)
editor.set_shape("shape_1", "Box", properties)
```

### Service Layer

#### GeometryService

**Location**: `src/cad_widgets/services/geometry_service.py`

Service for creating and manipulating 3D shapes using OpenCascade.

**Responsibilities**:
- Shape creation (boxes, spheres, cylinders, cones, tori)
- Shape transformations (translation, rotation)
- Boolean operations (union, subtraction, intersection)
- Provides clean Python API over OpenCascade

**Key Methods**:
- `create_box(width, height, depth, position)` - Create box
- `create_sphere(radius, center)` - Create sphere
- `create_cylinder(radius, height, position, direction)` - Create cylinder
- `create_cone(radius1, radius2, height, position, direction)` - Create cone
- `create_torus(major_radius, minor_radius, position, direction)` - Create torus
- `translate_shape(shape, dx, dy, dz)` - Translate shape
- `rotate_shape(shape, angle_x, angle_y, angle_z, center)` - Rotate shape
- `create_union(shape1, shape2)` - Boolean union
- `create_subtraction(shape1, shape2)` - Boolean subtraction
- `create_intersection(shape1, shape2)` - Boolean intersection
- `export_step(shape, filename)` - Export shape to STEP file
- `import_step(filename)` - Import shape from STEP file
- `export_iges(shape, filename)` - Export shape to IGES file
- `import_iges(filename)` - Import shape from IGES file

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

# Boolean operations
union = geo.create_union(box, sphere)

# Import/Export
GeometryService.export_step(box, "box.step")
imported = GeometryService.import_step("model.step")
```

#### ViewService

**Location**: `src/cad_widgets/services/view_service.py`

Service handling view operations and shape display in OpenCascade viewer.

**Responsibilities**:
- View setup and configuration
- Shape display and removal
- Shape registry management (ShapeInfo tracking)
- Camera control (projection, standard views)
- Display mode management (shaded, wireframe)
- Trihedron (axis indicator) setup

**Key Methods**:
- `setup_initial_view()` - Initialize view settings
- `display_shape(shape, shape_id, color, transparency, update)` - Display shape
- `remove_shape(shape_id)` - Remove specific shape
- `erase_all()` - Clear all shapes
- `set_projection(direction)` - Set standard view
- `set_projection_type(type)` - Set perspective/orthographic
- `set_display_mode(mode)` - Set display mode
- `fit_all()` - Fit all shapes in view

**Usage**:
```python
# Used internally by OCPWidget
view_service = ViewService(view, viewer, context)
view_service.setup_initial_view()
view_service.display_shape(shape, "shape_1", (1, 0, 0), 0.0)
```

#### SelectionService

**Location**: `src/cad_widgets/services/selection_service.py`

Service managing entity selection in the 3D viewer.

**Responsibilities**:
- Selection mode management (volume, surface, edge, vertex)
- Selection color configuration
- Highlight configuration
- Enable/disable selection

**Key Methods**:
- `set_mode(mode)` - Set selection mode (SelectionMode enum)
- `enable()` - Enable selection
- `disable()` - Disable selection
- `get_selected_shapes()` - Get currently selected shapes

**Usage**:
```python
# Used internally by OCPWidget
selection_service = SelectionService(context)
selection_service.set_mode(SelectionMode.SURFACE)
selection_service.enable()
```

### Manager Layer

#### GeometryManager

**Location**: `src/cad_widgets/managers/geometry_manager.py`

High-level manager for geometry lifecycle and property management.

**Responsibilities**:
- Create shapes from property objects
- Update shape properties and regenerate geometry
- Manage shape registry (ManagedShape objects)
- Emit signals for shape lifecycle events
- Convert between properties and shapes

**Qt Signals**:
- `shape_created(str, ManagedShape)` - Shape created
- `shape_updated(str, ManagedShape)` - Shape updated
- `shape_removed(str)` - Shape removed
- `all_cleared()` - All shapes cleared

**Key Methods**:
- `create_shape(shape_id, shape_type, name, color, properties)` - Create managed shape
- `update_shape(shape_id, properties)` - Update shape properties
- `get_shape(shape_id)` - Get managed shape
- `remove_shape(shape_id)` - Remove shape
- `clear_all()` - Clear all shapes
- `get_all_shapes()` - Get all managed shapes

**Usage**:
```python
from cad_widgets import GeometryManager, BoxProperties, ShapeType, Translation

manager = GeometryManager()

# Create shape with properties
properties = BoxProperties(width=100, height=50, depth=75)
properties.translation = Translation(x=50, y=0, z=0)

shape = manager.create_shape(
    shape_id="box_1",
    shape_type=ShapeType.BOX,
    name="My Box",
    color=(0.8, 0.2, 0.2),
    properties=properties
)

# Update properties
properties.width = 150
manager.update_shape("box_1", properties)
```

### Models Layer

#### Shape Properties

**Location**: `src/cad_widgets/models/shape_properties.py`

Data classes representing shape properties.

**Classes**:
- `Translation` - 3D position (x, y, z)
- `Rotation` - 3D rotation in degrees (x, y, z)
- `ShapeProperties` - Base properties (translation, rotation)
- `BoxProperties` - Box dimensions (width, height, depth)
- `SphereProperties` - Sphere dimensions (radius)
- `CylinderProperties` - Cylinder dimensions (radius, height)
- `ConeProperties` - Cone dimensions (radius1, radius2, height)
- `TorusProperties` - Torus dimensions (major_radius, minor_radius)
- `ImportedProperties` - Properties for imported shapes (STEP, IGES)

**Usage**:
```python
from cad_widgets import BoxProperties, Translation, Rotation

properties = BoxProperties(
    width=100,
    height=50,
    depth=75
)
properties.translation = Translation(x=50, y=0, z=0)
properties.rotation = Rotation(x=0, y=0, z=45)

# Convert to/from dict for serialization
data = properties.to_dict()
restored = BoxProperties.from_dict(data)
```

## Architecture Patterns

### Layered Architecture

The project follows a clear separation of concerns through distinct layers:

```
┌─────────────────────────────────────┐
│      Widget Layer (UI)              │  PySide6 widgets, user interaction
│  OCPWidget, Toolbars, Tree, Editor  │
├─────────────────────────────────────┤
│      Manager Layer                  │  High-level orchestration
│  GeometryManager                    │
├─────────────────────────────────────┤
│      Service Layer                  │  Business logic, operations
│  GeometryService, ViewService,      │
│  SelectionService                   │
├─────────────────────────────────────┤
│      Models Layer                   │  Data structures
│  ShapeProperties, Translation, etc. │
└─────────────────────────────────────┘
```

**Benefits**:
- Clear separation of concerns
- Testable components
- Reusable services
- Maintainable codebase

### Signal-Based Communication

Widgets use Qt signals for loose coupling:

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
- Multiple listeners possible
- Event-driven architecture

### Service Pattern

Services encapsulate domain logic without UI concerns:

```python
class GeometryService:
    """Pure geometry operations - no UI dependencies"""
    
    def create_box(self, width, height, depth, position):
        # OpenCascade operations
        return shape
```

**Benefits**:
- Testable without UI
- Reusable across different UIs
- Clean API over OpenCascade complexity
- Single responsibility

### Manager Pattern

Managers provide high-level orchestration:

```python
class GeometryManager(QObject):
    """Manages geometry lifecycle and state"""
    
    shape_created = Signal(str, object)
    
    def create_shape(self, shape_id, shape_type, name, color, properties):
        shape = self._create_from_properties(properties)
        managed = ManagedShape(shape, shape_type, name, color, properties)
        self._shapes[shape_id] = managed
        self.shape_created.emit(shape_id, managed)
```

**Benefits**:
- Centralized state management
- Event notification system
- Property-based shape management
- Clean separation from low-level operations

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

## API Reference

This section provides a comprehensive reference for all public APIs in the CAD Widgets library.

### Mouse Controls

User interaction controls in the 3D viewer:

- **Left Click + Drag**: Rotate view
- **Middle Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out

### OCPWidget Methods

Core 3D viewer widget methods:

- `display_shape(shape, color=None, transparency=0.0, update=True)` - Display a shape
- `erase_all()` - Clear all shapes
- `fit_all()` - Fit all objects in view
- `update_display()` - Refresh the display
- `set_projection(direction)` - Set view ('top', 'front', 'iso', etc.)
- `set_projection_type(type)` - Set 'perspective' or 'orthographic'
- `set_display_mode(mode)` - Set 'shaded', 'wireframe', or 'both'
- `set_selection_mode(mode)` - Set selection mode ('volume', 'surface', 'edge', 'vertex')
- `get_context()` - Get AIS_InteractiveContext
- `get_view()` - Get V3d_View
- `get_viewer()` - Get V3d_Viewer

### Widget Signals

#### ViewToolbar Signals

- `projection_changed(str)` - Standard view changed
- `projection_type_changed(str)` - Projection type changed
- `display_mode_changed(str)` - Display mode changed
- `fit_all_requested()` - Fit all requested
- `clear_requested()` - Clear requested

#### SelectionToolbar Signals

- `selection_mode_changed(str)` - Selection mode changed (volume/surface/edge/vertex)

#### GeometryTreeWidget Signals

- `shape_visibility_changed(str, bool)` - Shape visibility toggled
- `shape_selected(str)` - Shape selected in tree
- `shape_deleted(str)` - Shape deletion requested
- `clear_all_requested()` - Clear all shapes requested
- `shape_creation_requested(ShapeType)` - New shape creation requested
- `shapes_union_requested(list)` - Boolean union requested
- `shapes_subtract_requested(list)` - Boolean subtraction requested
- `export_step_requested(str)` - Export shape to STEP file
- `export_iges_requested(str)` - Export shape to IGES file
- `import_step_requested()` - Import STEP file
- `import_iges_requested()` - Import IGES file

#### PropertyEditorWidget Signals

- `properties_changed(str, dict)` - Shape properties modified

### GeometryService Methods

Shape creation and manipulation methods:

- `create_box(width, height, depth, position)` - Create box
- `create_sphere(radius, center)` - Create sphere
- `create_cylinder(radius, height, position, direction)` - Create cylinder
- `create_cone(radius1, radius2, height, position, direction)` - Create cone
- `create_torus(major_radius, minor_radius, position, direction)` - Create torus
- `translate_shape(shape, dx, dy, dz)` - Translate shape
- `rotate_shape(shape, angle_x, angle_y, angle_z, center)` - Rotate shape
- `create_union(shape1, shape2)` - Boolean union
- `create_subtraction(shape1, shape2)` - Boolean subtraction
- `create_intersection(shape1, shape2)` - Boolean intersection

### ViewService Methods

View and display management methods:

- `setup_initial_view()` - Initialize view settings
- `display_shape(shape, shape_id, color, transparency, update)` - Display shape
- `remove_shape(shape_id)` - Remove specific shape
- `erase_all()` - Clear all shapes
- `set_projection(direction)` - Set standard view
- `set_projection_type(type)` - Set perspective/orthographic
- `set_display_mode(mode)` - Set display mode
- `fit_all()` - Fit all shapes in view

### SelectionService Methods

Selection management methods:

- `set_mode(mode)` - Set selection mode (SelectionMode enum)
- `enable()` - Enable selection
- `disable()` - Disable selection
- `get_selected_shapes()` - Get currently selected shapes

### GeometryManager Methods

High-level geometry lifecycle management:

- `create_shape(shape_id, shape_type, name, color, properties)` - Create managed shape
- `update_shape(shape_id, properties)` - Update shape properties
- `get_shape(shape_id)` - Get managed shape
- `remove_shape(shape_id)` - Remove shape
- `clear_all()` - Clear all shapes
- `get_all_shapes()` - Get all managed shapes

### Enums

Available enumeration types:

- `ViewDirection` - TOP, BOTTOM, FRONT, BACK, LEFT, RIGHT, ISO
- `ProjectionType` - PERSPECTIVE, ORTHOGRAPHIC
- `DisplayMode` - SHADED, WIREFRAME, BOTH
- `SelectionMode` - VOLUME, SURFACE, EDGE, VERTEX
- `ShapeType` - BOX, SPHERE, CYLINDER, CONE, TORUS, UNION, SUBTRACTION, IMPORTED

## Extension Points

### Custom Widgets

Create custom widgets following the same patterns:

```python
class CustomToolbar(QWidget):
    """Custom toolbar with signal-based communication."""
    
    custom_action = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        # Build UI
        pass
```

### Custom Services

Add domain-specific services:

```python
class AnalysisService:
    """Service for shape analysis."""
    
    def __init__(self, geometry_service):
        self._geo = geometry_service
    
    def calculate_volume(self, shape):
        # Analysis logic
        return volume
    
    def calculate_center_of_mass(self, shape):
        # Analysis logic
        return center
```

### Custom Managers

Create managers for complex workflows:

```python
class AssemblyManager(QObject):
    """Manage assemblies of multiple shapes."""
    
    assembly_created = Signal(str, object)
    
    def __init__(self, geometry_manager):
        super().__init__()
        self._geo_manager = geometry_manager
        self._assemblies = {}
    
    def create_assembly(self, assembly_id, shape_ids):
        # Orchestrate assembly creation
        pass
```

### Custom Property Types

Define custom property classes:

```python
@dataclass
class CustomShapeProperties(ShapeProperties):
    """Properties for custom shapes."""
    
    custom_param1: float = 10.0
    custom_param2: float = 20.0
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "custom_param1": self.custom_param1,
            "custom_param2": self.custom_param2,
        })
        return result
```

## Testing

The project includes comprehensive tests for all layers:

### Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures
├── test_widget.py                   # OCPWidget tests
├── test_geometry_manager.py         # GeometryManager tests
├── test_geometry_manager_integration.py  # Integration tests
├── test_geometry_tree.py            # GeometryTreeWidget tests
├── test_property_editor.py          # PropertyEditorWidget tests
├── test_toolbar.py                  # Toolbar tests
├── test_shapes.py                   # GeometryService tests
└── test_integration.py              # End-to-end tests
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_widget.py -v

# Run with coverage
pytest tests/ --cov=cad_widgets

# Run specific test
pytest tests/test_widget.py::test_display_shape -v
```

### Test Categories

**Unit Tests**: Test individual components in isolation
- Services (no UI dependencies)
- Models and data classes
- Manager business logic

**Integration Tests**: Test component interactions
- Widget signal connections
- Manager-service coordination
- Property updates and shape regeneration

**Widget Tests**: Test UI components
- Signal emission
- User interaction handling
- State management

### Writing Tests

Follow the existing patterns:

```python
import pytest
from cad_widgets import GeometryService, BoxProperties

def test_geometry_service_create_box():
    """Test box creation."""
    geo = GeometryService()
    box = geo.create_box(100, 50, 75)
    assert box is not None

def test_box_properties():
    """Test box property serialization."""
    props = BoxProperties(width=100, height=50, depth=75)
    data = props.to_dict()
    restored = BoxProperties.from_dict(data)
    assert restored.width == props.width
```

## Best Practices

### 1. Use Services for Shape Operations

Prefer services over direct OCP calls:

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
```

### 2. Use GeometryManager for Stateful Shapes

When you need to track and update shapes, use GeometryManager:

```python
from cad_widgets import GeometryManager, BoxProperties, ShapeType

manager = GeometryManager()

# Create with properties
properties = BoxProperties(width=100, height=50, depth=75)
shape = manager.create_shape("box_1", ShapeType.BOX, "My Box", (0.8, 0.2, 0.2), properties)

# Update later
properties.width = 150
manager.update_shape("box_1", properties)  # Shape automatically regenerated
```

### 3. Connect Signals for Modular Design

Use signals for component communication:

```python
# Good - decoupled
toolbar.projection_changed.connect(viewer.set_projection)
tree.shape_selected.connect(editor.set_shape)

# Avoid - tight coupling
def on_button_click():
    viewer.set_projection('front')
    editor.clear()
```

### 4. Use Property Classes

Define shape parameters with property classes:

```python
# Good - structured, type-safe
properties = BoxProperties(width=100, height=50, depth=75)
properties.translation = Translation(x=50, y=0, z=0)

# Avoid - unstructured dicts
params = {"width": 100, "height": 50, "depth": 75, "x": 50}
```

### 5. Batch Shape Updates

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

### 6. Layer Responsibilities

Keep layer responsibilities clear:

```python
# Widgets: Handle UI and user interaction
class MyWidget(QWidget):
    action_requested = Signal(str)
    
    def _on_button_click(self):
        self.action_requested.emit(self._get_selected_id())

# Services: Handle domain logic
class MyService:
    def perform_operation(self, shape):
        # Pure business logic, no UI
        return result

# Managers: Orchestrate and manage state
class MyManager(QObject):
    def handle_action(self, action_id):
        result = self.service.perform_operation(self.shapes[action_id])
        self.update_state(result)
```

## Complete Example

Here's a full example showing how all components work together:

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter
from PySide6.QtCore import Qt

from cad_widgets import (
    OCPWidget,
    ViewToolbar,
    SelectionToolbar,
    GeometryTreeWidget,
    PropertyEditorWidget,
    GeometryManager,
    BoxProperties,
    ShapeType,
    Translation,
)


class CADViewerWindow(QMainWindow):
    """Complete CAD viewer with all widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD Viewer - Full Example")
        
        # Initialize manager
        self.geometry_manager = GeometryManager()
        
        # Create widgets
        self.viewer = OCPWidget()
        self.view_toolbar = ViewToolbar(orientation='vertical')
        self.selection_toolbar = SelectionToolbar(orientation='vertical')
        self.geometry_tree = GeometryTreeWidget()
        self.property_editor = PropertyEditorWidget()
        
        # Setup UI layout
        self._setup_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Create initial geometry
        self._create_initial_shapes()
    
    def _setup_ui(self):
        """Setup the user interface layout."""
        # Create splitters for layout
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (toolbars)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(self.view_toolbar)
        left_layout.addWidget(self.selection_toolbar)
        left_layout.addStretch()
        
        # Center (viewer)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.viewer)
        
        # Right panel (tree and properties)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.geometry_tree)
        right_layout.addWidget(self.property_editor)
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setStretchFactor(0, 0)  # Toolbars - no stretch
        main_splitter.setStretchFactor(1, 3)  # Viewer - largest
        main_splitter.setStretchFactor(2, 1)  # Side panel - medium
        
        self.setCentralWidget(main_splitter)
    
    def _connect_signals(self):
        """Connect all widget signals."""
        # View toolbar connections
        self.view_toolbar.projection_changed.connect(self.viewer.set_projection)
        self.view_toolbar.projection_type_changed.connect(self.viewer.set_projection_type)
        self.view_toolbar.display_mode_changed.connect(self.viewer.set_display_mode)
        self.view_toolbar.fit_all_requested.connect(self.viewer.fit_all)
        self.view_toolbar.clear_requested.connect(self._handle_clear_all)
        
        # Selection toolbar connections
        self.selection_toolbar.selection_mode_changed.connect(self.viewer.set_selection_mode)
        
        # Geometry manager connections
        self.geometry_manager.shape_created.connect(self._handle_shape_created)
        self.geometry_manager.shape_updated.connect(self._handle_shape_updated)
        self.geometry_manager.shape_removed.connect(self._handle_shape_removed)
        
        # Geometry tree connections
        self.geometry_tree.shape_visibility_changed.connect(self._handle_visibility_changed)
        self.geometry_tree.shape_selected.connect(self._handle_tree_selection)
        self.geometry_tree.shape_deleted.connect(self._handle_shape_deletion)
        self.geometry_tree.clear_all_requested.connect(self._handle_clear_all)
        self.geometry_tree.shape_creation_requested.connect(self._handle_shape_creation)
        
        # Property editor connections
        self.property_editor.properties_changed.connect(self._handle_properties_changed)
    
    def _create_initial_shapes(self):
        """Create some initial shapes to display."""
        # Create a box
        box_props = BoxProperties(width=100, height=50, depth=75)
        box_props.translation = Translation(x=-60, y=0, z=0)
        self.geometry_manager.create_shape(
            shape_id="box_1",
            shape_type=ShapeType.BOX,
            name="Box",
            color=(0.8, 0.2, 0.2),
            properties=box_props
        )
        
        # Add more shapes...
    
    def _handle_shape_created(self, shape_id, managed_shape):
        """Handle shape creation."""
        # Display in viewer
        self.viewer.display_shape(
            managed_shape.shape,
            color=managed_shape.color,
            update=True
        )
        
        # Add to tree
        self.geometry_tree.add_shape(
            shape_id=shape_id,
            name=managed_shape.name,
            shape_type=managed_shape.shape_type.value,
            visible=True
        )
    
    def _handle_properties_changed(self, shape_id, properties_dict):
        """Handle property changes from editor."""
        managed = self.geometry_manager.get_shape(shape_id)
        if managed:
            # Update properties from dict
            updated_props = type(managed.properties).from_dict(properties_dict)
            self.geometry_manager.update_shape(shape_id, updated_props)


if __name__ == "__main__":
    app = QApplication([])
    window = CADViewerWindow()
    window.show()
    app.exec()
```

This example demonstrates:
- **Layered architecture**: Widgets → Manager → Services
- **Signal-based communication**: Loose coupling between components
- **Property-based geometry**: Structured shape management
- **Complete UI**: All widgets working together
- **Event handling**: Comprehensive signal connection

## Import/Export Operations

CAD Widgets supports importing and exporting standard CAD file formats.

### Supported Formats

- **STEP** (`.step`, `.stp`) - ISO 10303 standard, widely used for CAD data exchange
- **IGES** (`.iges`, `.igs`) - Initial Graphics Exchange Specification, legacy format

### Exporting Shapes

Use `GeometryService` static methods to export shapes:

```python
from cad_widgets import GeometryService

geo = GeometryService()

# Create a shape
box = geo.create_box(100, 50, 75)

# Export to STEP format
success = GeometryService.export_step(box, "output.step")
if success:
    print("Successfully exported to STEP")

# Export to IGES format
success = GeometryService.export_iges(box, "output.iges")
if success:
    print("Successfully exported to IGES")
```

### Importing Shapes

Import shapes and add them to your scene:

```python
from cad_widgets import GeometryService, GeometryManager, ImportedProperties

# Import from file
imported_shape = GeometryService.import_step("model.step")

if imported_shape:
    # Create manager to handle the imported shape
    manager = GeometryManager()
    
    # Import into manager with properties
    properties = ImportedProperties()
    properties.translation = Translation(x=50, y=0, z=0)
    
    managed = manager.import_shape(
        shape=imported_shape,
        name="Imported Model",
        color=(0.5, 0.5, 0.8),
        properties=properties
    )
    
    # Display in viewer
    viewer.display_shape(managed.shape, color=managed.color)
```

### UI Integration

The `GeometryTreeWidget` provides built-in context menu actions for import/export:

```python
# Connect import/export signals
tree.export_step_requested.connect(handle_export_step)
tree.import_step_requested.connect(handle_import_step)

def handle_export_step(shape_id: str):
    """Handle STEP export from context menu."""
    managed = geometry_manager.get_shape(shape_id)
    if managed:
        filename = get_save_filename(f"{managed.name}.step")
        if filename:
            GeometryService.export_step(managed.shape, filename)

def handle_import_step():
    """Handle STEP import from context menu."""
    filename = get_open_filename()
    if filename:
        shape = GeometryService.import_step(filename)
        if shape:
            geometry_manager.import_shape(
                shape, "Imported", (0.7, 0.7, 0.7)
            )
```

### Best Practices

1. **Error Handling**: Import/export operations return `None` or `False` on failure
2. **File Validation**: Check file existence before importing
3. **Format Selection**: STEP is recommended for modern CAD workflows
4. **Transformation**: Use `ImportedProperties` to position imported shapes
5. **Batch Operations**: Export multiple shapes by creating assemblies first

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

### Enhanced Widgets
- **Measurement Tools**: Distance, angle, area measurement widgets
- **Sectioning Planes**: Interactive cross-section views
- **Material Editor**: Visual material and appearance editing
- **Animation Timeline**: Animate shape transformations

### File Operations
- **Import/Export Service**: ✅ STEP, IGES implemented; STL, OBJ planned
- **Project Serialization**: Save/load complete projects
- **Format Converters**: Between different CAD formats

### Analysis Features
- **AnalysisService**: Volume, surface area, mass properties
- **Collision Detection**: Check for shape intersections
- **Tolerance Analysis**: Engineering tolerance checking
- **FEA Integration**: Finite element analysis preparation

### Advanced Rendering
- **Lighting Service**: Custom lighting setups
- **Material System**: PBR materials and textures
- **Shadow Rendering**: Real-time shadows
- **Environment Maps**: Reflective environments

### Collaboration
- **Annotation System**: Comments and markup
- **Version Control**: Track design changes
- **Real-time Collaboration**: Multi-user editing

### Performance
- **Level of Detail**: LOD system for large assemblies
- **Streaming**: Progressive loading of large models
- **GPU Acceleration**: Leverage GPU for computations

## Contributing

When contributing to the architecture:

### Guidelines

1. **Follow Layered Architecture**
   - Keep widgets, services, managers, and models separated
   - No UI code in services
   - No OpenCascade code in widgets (use services)

2. **Use Signal-Based Communication**
   - Emit signals for events
   - Connect signals for component interaction
   - Avoid direct method calls between components

3. **Write Tests**
   - Unit tests for services and models
   - Integration tests for manager coordination
   - Widget tests for UI components

4. **Document Code**
   - Docstrings for all public methods
   - Type hints for parameters and return values
   - Update architecture docs for new patterns

5. **Follow Code Style**
   - Run `ruff format` before committing
   - Use `ruff check --fix` to fix linting issues
   - Run `mypy` for type checking

### Adding New Features

When adding new features:

1. **Identify the Layer**
   - Is it UI? → Widget layer
   - Is it business logic? → Service or Manager layer
   - Is it data? → Model layer

2. **Define Interfaces**
   - What signals will it emit?
   - What methods will it expose?
   - What data structures will it use?

3. **Implement with Tests**
   - Write tests first (TDD)
   - Implement the feature
   - Ensure tests pass

4. **Document**
   - Add docstrings
   - Update README if it's a major feature
   - Update ARCHITECTURE.md for architectural changes

5. **Example Usage**
   - Add an example to `examples/`
   - Update existing examples if needed

### Code Review Checklist

- [ ] Follows layered architecture
- [ ] Uses signals for communication
- [ ] Has unit tests
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Passes `ruff check`
- [ ] Passes `mypy`
- [ ] Example usage provided
- [ ] Documentation updated
