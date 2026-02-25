"""
Basic tests for OCPWidget
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from PySide6.QtWidgets import QApplication
from cad_widgets import OCPWidget
from cad_widgets.utils import create_box
from OCP.AIS import AIS_ListOfInteractive


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def get_displayed_count(ctx):
    """Helper to get the number of displayed objects in context."""
    obj_list = AIS_ListOfInteractive()
    ctx.DisplayedObjects(obj_list)
    return obj_list.Size()


def test_widget_creation(qapp):
    """Test that OCPWidget can be created."""
    widget = OCPWidget()
    assert widget is not None
    assert widget.width() > 0
    assert widget.height() > 0


def test_display_shape(qapp):
    """Test displaying a shape."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    
    ais_shape = widget.display_shape(box, color=(0.8, 0.2, 0.2))
    assert ais_shape is not None
    
    # Assert the shape is displayed in the context
    ctx = widget.get_context()
    assert get_displayed_count(ctx) == 1


def test_projection_types(qapp):
    """Test setting projection types."""
    widget = OCPWidget()
    view = widget.get_view()
    camera = view.Camera()
    
    # Test perspective (Projection_Perspective = 1)
    widget.set_projection_type('perspective')
    assert camera.ProjectionType() == 1
    
    # Test orthographic (Projection_Orthographic = 0)
    widget.set_projection_type('orthographic')
    assert camera.ProjectionType() == 0


def test_display_modes(qapp):
    """Test setting display modes."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    ctx = widget.get_context()
    
    # Test shaded mode (mode 1)
    widget.set_display_mode('shaded')
    assert ctx.DisplayMode() == 1
    
    # Test wireframe mode (mode 0)
    widget.set_display_mode('wireframe')
    assert ctx.DisplayMode() == 0
    
    # Test both mode (mode 2)
    widget.set_display_mode('both')
    assert ctx.DisplayMode() == 2


def test_standard_views(qapp):
    """Test standard view projections."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    # Test top view - looking down Z axis
    widget.set_projection('top')
    x, y, z = view.Proj()
    assert abs(z - 1.0) < 0.01
    
    # Test front view - looking along negative Y axis
    widget.set_projection('front')
    x, y, z = view.Proj()
    assert abs(y + 1.0) < 0.01
    
    # Test right view - looking along positive X axis
    widget.set_projection('right')
    x, y, z = view.Proj()
    assert abs(x - 1.0) < 0.01
    
    # Test all other views (basic smoke test)
    for view_name in ['back', 'bottom', 'left', 'iso']:
        widget.set_projection(view_name)


def test_erase_all(qapp):
    """Test clearing all shapes."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    ctx = widget.get_context()
    assert get_displayed_count(ctx) == 1
    
    widget.erase_all()
    assert get_displayed_count(ctx) == 0


def test_fit_all(qapp):
    """Test fit all operation."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    widget.fit_all()
    # Fit all operation completes without error
    view = widget.get_view()
    assert view is not None


def test_multiple_shapes(qapp):
    """Test displaying multiple shapes."""
    widget = OCPWidget()
    ctx = widget.get_context()
    
    box1 = create_box(100, 100, 100)
    box2 = create_box(50, 50, 50)
    box3 = create_box(25, 25, 25)
    
    widget.display_shape(box1)
    assert get_displayed_count(ctx) == 1
    
    widget.display_shape(box2)
    assert get_displayed_count(ctx) == 2
    
    widget.display_shape(box3)
    assert get_displayed_count(ctx) == 3
    
    # Clear and verify
    widget.erase_all()
    assert get_displayed_count(ctx) == 0


def test_display_shape_with_transparency(qapp):
    """Test displaying a shape with transparency."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    
    ais_shape = widget.display_shape(box, transparency=0.5)
    assert ais_shape is not None


def test_display_shape_with_display_mode(qapp):
    """Test displaying a shape with specific display mode."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    
    # Test with wireframe mode
    ais_shape = widget.display_shape(box, display_mode='wireframe')
    assert ais_shape is not None
    
    # Test with shaded mode
    box2 = create_box(50, 50, 50)
    ais_shape2 = widget.display_shape(box2, display_mode='shaded')
    assert ais_shape2 is not None


def test_get_viewer(qapp):
    """Test getting the viewer."""
    widget = OCPWidget()
    viewer = widget.get_viewer()
    assert viewer is not None


def test_get_view(qapp):
    """Test getting the view."""
    widget = OCPWidget()
    view = widget.get_view()
    assert view is not None


def test_get_context(qapp):
    """Test getting the context."""
    widget = OCPWidget()
    ctx = widget.get_context()
    assert ctx is not None


def test_update_display(qapp):
    """Test update display method."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Should not raise an error
    widget.update_display()


def test_widget_minimum_size(qapp):
    """Test widget has proper minimum size."""
    widget = OCPWidget()
    assert widget.minimumWidth() == 640
    assert widget.minimumHeight() == 480


def test_display_without_update(qapp):
    """Test displaying a shape without updating."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    
    ais_shape = widget.display_shape(box, update=False)
    assert ais_shape is not None
    
    ctx = widget.get_context()
    assert get_displayed_count(ctx) == 1


def test_iso_view(qapp):
    """Test isometric view projection."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    widget.set_projection('iso')
    x, y, z = view.Proj()
    # Iso view should have equal components (normalized, so ~0.577 each)
    # Verify they're all equal and positive
    assert abs(x - y) < 0.01
    assert abs(y - z) < 0.01
    assert x > 0 and y > 0 and z > 0


def test_left_view(qapp):
    """Test left view projection."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    widget.set_projection('left')
    x, y, z = view.Proj()
    assert abs(x + 1.0) < 0.01  # Looking along negative X


def test_back_view(qapp):
    """Test back view projection."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    widget.set_projection('back')
    x, y, z = view.Proj()
    assert abs(y - 1.0) < 0.01  # Looking along positive Y


def test_bottom_view(qapp):
    """Test bottom view projection."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    widget.set_projection('bottom')
    x, y, z = view.Proj()
    assert abs(z + 1.0) < 0.01  # Looking up along negative Z


def test_display_shape_default_color(qapp):
    """Test displaying a shape with default color (None)."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    
    ais_shape = widget.display_shape(box, color=None)
    assert ais_shape is not None
