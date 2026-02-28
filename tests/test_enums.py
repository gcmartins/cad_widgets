"""
Tests for enums
"""

import sys

import pytest
from PySide6.QtWidgets import QApplication
from cad_widgets import OCPWidget, ViewDirection, ProjectionType, DisplayMode, GeometryService


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_view_direction_enum_values():
    """Test ViewDirection enum values."""
    assert ViewDirection.TOP.value == "top"
    assert ViewDirection.BOTTOM.value == "bottom"
    assert ViewDirection.FRONT.value == "front"
    assert ViewDirection.BACK.value == "back"
    assert ViewDirection.LEFT.value == "left"
    assert ViewDirection.RIGHT.value == "right"
    assert ViewDirection.ISO.value == "iso"


def test_projection_type_enum_values():
    """Test ProjectionType enum values."""
    assert ProjectionType.PERSPECTIVE.value == "perspective"
    assert ProjectionType.ORTHOGRAPHIC.value == "orthographic"


def test_display_mode_enum_values():
    """Test DisplayMode enum values."""
    assert DisplayMode.SHADED.value == "shaded"
    assert DisplayMode.WIREFRAME.value == "wireframe"
    assert DisplayMode.BOTH.value == "both"


def test_widget_with_view_direction_enum(qapp):
    """Test using ViewDirection enum with OCPWidget."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()
    
    # Test with enum instead of string
    widget.set_projection(ViewDirection.TOP)
    x, y, z = view.Proj()
    assert abs(z - 1.0) < 0.01
    
    # Test with another enum value
    widget.set_projection(ViewDirection.FRONT)
    x, y, z = view.Proj()
    assert abs(y + 1.0) < 0.01


def test_widget_with_projection_type_enum(qapp):
    """Test using ProjectionType enum with OCPWidget."""
    widget = OCPWidget()
    view = widget.get_view()
    camera = view.Camera()
    
    # Test with enum instead of string
    widget.set_projection_type(ProjectionType.ORTHOGRAPHIC)
    assert camera.ProjectionType() == 0
    
    widget.set_projection_type(ProjectionType.PERSPECTIVE)
    assert camera.ProjectionType() == 1


def test_widget_with_display_mode_enum(qapp):
    """Test using DisplayMode enum with OCPWidget."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    ctx = widget.get_context()
    
    # Test with enum instead of string
    widget.set_display_mode(DisplayMode.WIREFRAME)
    assert ctx.DisplayMode() == 0
    
    widget.set_display_mode(DisplayMode.SHADED)
    assert ctx.DisplayMode() == 1
    
    widget.set_display_mode(DisplayMode.BOTH)
    assert ctx.DisplayMode() == 2


def test_display_shape_with_display_mode_enum(qapp):
    """Test displaying a shape with DisplayMode enum."""
    widget = OCPWidget()
    box1 = GeometryService().create_box(100, 100, 100)
    box2 = GeometryService().create_box(50, 50, 50)
    
    # Test with enum values
    ais_shape1 = widget.display_shape(box1, display_mode=DisplayMode.WIREFRAME)
    assert ais_shape1 is not None
    
    ais_shape2 = widget.display_shape(box2, display_mode=DisplayMode.SHADED)
    assert ais_shape2 is not None


def test_enum_string_comparison():
    """Test that enums can be compared with strings."""
    # Since enums inherit from str, they should work in string comparisons
    assert ViewDirection.TOP == "top"
    assert ProjectionType.PERSPECTIVE == "perspective"
    assert DisplayMode.SHADED == "shaded"


def test_all_view_directions_with_enum(qapp):
    """Test all view directions using enums."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Test all enum values work without error
    for direction in ViewDirection:
        widget.set_projection(direction)
    
    # Widget should still be functional
    assert widget.get_view() is not None


def test_enum_listing():
    """Test listing all enum values."""
    view_directions = list(ViewDirection)
    assert len(view_directions) == 7
    assert ViewDirection.TOP in view_directions
    assert ViewDirection.ISO in view_directions
    
    projection_types = list(ProjectionType)
    assert len(projection_types) == 2
    assert ProjectionType.PERSPECTIVE in projection_types
    
    display_modes = list(DisplayMode)
    assert len(display_modes) == 3
    assert DisplayMode.SHADED in display_modes
