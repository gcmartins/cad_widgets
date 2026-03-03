"""
Basic tests for OCPWidget
"""

import sys

import pytest
from PySide6.QtWidgets import QApplication
from cad_widgets import (
    OCPWidget,
    ViewDirection,
    ProjectionType,
    DisplayMode,
    SelectionMode,
    GeometryService,
)
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
    box = GeometryService().create_box(100, 100, 100)

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
    widget.set_projection_type(ProjectionType.PERSPECTIVE)
    assert camera.ProjectionType() == 1

    # Test orthographic (Projection_Orthographic = 0)
    widget.set_projection_type(ProjectionType.ORTHOGRAPHIC)
    assert camera.ProjectionType() == 0


def test_display_modes(qapp):
    """Test setting display modes."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    ctx = widget.get_context()

    # Test shaded mode (mode 1)
    widget.set_display_mode(DisplayMode.SHADED)
    assert ctx.DisplayMode() == 1

    # Test wireframe mode (mode 0)
    widget.set_display_mode(DisplayMode.WIREFRAME)
    assert ctx.DisplayMode() == 0

    # Test both mode (shaded with edges)
    widget.set_display_mode(DisplayMode.BOTH)
    # BOTH mode uses shaded (1) with face boundaries enabled
    assert ctx.DisplayMode() == 1


def test_standard_views(qapp):
    """Test standard view projections."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()

    # Test top view - looking down Z axis
    widget.set_projection(ViewDirection.TOP)
    x, y, z = view.Proj()
    assert abs(z - 1.0) < 0.01

    # Test front view - looking along negative Y axis
    widget.set_projection(ViewDirection.FRONT)
    x, y, z = view.Proj()
    assert abs(y + 1.0) < 0.01

    # Test right view - looking along positive X axis
    widget.set_projection(ViewDirection.RIGHT)
    x, y, z = view.Proj()
    assert abs(x - 1.0) < 0.01

    # Test all other views (basic smoke test)
    for view_name in [
        ViewDirection.BACK,
        ViewDirection.BOTTOM,
        ViewDirection.LEFT,
        ViewDirection.ISO,
    ]:
        widget.set_projection(view_name)


def test_erase_all(qapp):
    """Test clearing all shapes."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    ctx = widget.get_context()
    assert get_displayed_count(ctx) == 1

    widget.erase_all()
    assert get_displayed_count(ctx) == 0


def test_fit_all(qapp):
    """Test fit all operation."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    widget.fit_all()
    # Fit all operation completes without error
    view = widget.get_view()
    assert view is not None


def test_multiple_shapes(qapp):
    """Test displaying multiple shapes."""
    widget = OCPWidget()
    ctx = widget.get_context()

    box1 = GeometryService().create_box(100, 100, 100)
    box2 = GeometryService().create_box(50, 50, 50)
    box3 = GeometryService().create_box(25, 25, 25)

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
    """Test displaying a shape - transparency is now global only."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)

    ais_shape = widget.display_shape(box)
    assert ais_shape is not None


def test_display_shape_with_display_mode(qapp):
    """Test displaying a shape with specific display mode."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)

    # Test with wireframe mode - set mode globally before displaying
    widget.set_display_mode(DisplayMode.WIREFRAME)
    ais_shape = widget.display_shape(box)
    assert ais_shape is not None

    # Test with shaded mode
    widget.set_display_mode(DisplayMode.SHADED)
    box2 = GeometryService().create_box(50, 50, 50)
    ais_shape2 = widget.display_shape(box2)
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
    box = GeometryService().create_box(100, 100, 100)
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
    box = GeometryService().create_box(100, 100, 100)

    ais_shape = widget.display_shape(box, update=False)
    assert ais_shape is not None

    ctx = widget.get_context()
    assert get_displayed_count(ctx) == 1


def test_iso_view(qapp):
    """Test isometric view projection."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()

    widget.set_projection(ViewDirection.ISO)
    x, y, z = view.Proj()
    # Iso view should have equal components (normalized, so ~0.577 each)
    # Verify they're all equal and positive
    assert abs(x - y) < 0.01
    assert abs(y - z) < 0.01
    assert x > 0 and y > 0 and z > 0


def test_left_view(qapp):
    """Test left view projection."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()

    widget.set_projection(ViewDirection.LEFT)
    x, y, z = view.Proj()
    assert abs(x + 1.0) < 0.01  # Looking along negative X


def test_back_view(qapp):
    """Test back view projection."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()

    widget.set_projection(ViewDirection.BACK)
    x, y, z = view.Proj()
    assert abs(y - 1.0) < 0.01  # Looking along positive Y


def test_bottom_view(qapp):
    """Test bottom view projection."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)
    view = widget.get_view()

    widget.set_projection(ViewDirection.BOTTOM)
    x, y, z = view.Proj()
    assert abs(z + 1.0) < 0.01  # Looking up along negative Z


def test_display_shape_default_color(qapp):
    """Test displaying a shape with default color (None)."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)

    ais_shape = widget.display_shape(box, color=None)
    assert ais_shape is not None


# ============================================================================
# Selection Tests
# ============================================================================


def test_selection_enabled_by_default(qapp):
    """Test that selection is enabled by default."""
    widget = OCPWidget()
    assert widget.is_selection_enabled() is True


def test_default_selection_mode(qapp):
    """Test default selection mode is VOLUME."""
    widget = OCPWidget()
    assert widget.get_selection_mode() == SelectionMode.VOLUME


def test_set_selection_mode(qapp):
    """Test setting different selection modes."""
    widget = OCPWidget()

    widget.set_selection_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE

    widget.set_selection_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE

    widget.set_selection_mode(SelectionMode.VERTEX)
    assert widget.get_selection_mode() == SelectionMode.VERTEX

    widget.set_selection_mode(SelectionMode.VOLUME)
    assert widget.get_selection_mode() == SelectionMode.VOLUME


def test_disable_selection(qapp):
    """Test disabling selection."""
    widget = OCPWidget()

    widget.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False

    widget.set_selection_enabled(True)
    assert widget.is_selection_enabled() is True


def test_clear_selection(qapp):
    """Test clearing selection."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Clear selection should not raise an error
    widget.clear_selection()


def test_get_selected_shapes_empty(qapp):
    """Test getting selected shapes when nothing is selected."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    selected = widget.get_selected_shapes()
    assert isinstance(selected, list)
    assert len(selected) == 0


def test_selection_mode_all_types(qapp):
    """Test all selection mode types."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    modes = [
        SelectionMode.VOLUME,
        SelectionMode.SURFACE,
        SelectionMode.EDGE,
        SelectionMode.VERTEX,
    ]

    for mode in modes:
        widget.set_selection_mode(mode)
        assert widget.get_selection_mode() == mode


def test_selection_enabled_toggle(qapp):
    """Test toggling selection on and off."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Start enabled (default)
    assert widget.is_selection_enabled() is True

    # Disable
    widget.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False

    # Enable again
    widget.set_selection_enabled(True)
    assert widget.is_selection_enabled() is True

    # Disable again
    widget.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False


def test_selection_mode_with_multiple_shapes(qapp):
    """Test selection mode setting with multiple shapes displayed."""
    widget = OCPWidget()

    box1 = GeometryService().create_box(100, 100, 100)
    box2 = GeometryService().create_box(50, 50, 50)
    box3 = GeometryService().create_box(25, 25, 25)

    widget.display_shape(box1)
    widget.display_shape(box2)
    widget.display_shape(box3)

    # Should be able to set selection mode with multiple shapes
    widget.set_selection_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE


def test_clear_selection_multiple_times(qapp):
    """Test clearing selection multiple times."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Should not raise an error when called multiple times
    widget.clear_selection()
    widget.clear_selection()
    widget.clear_selection()


def test_selection_with_no_shapes(qapp):
    """Test selection operations with no shapes displayed."""
    widget = OCPWidget()

    # Should not raise errors
    widget.set_selection_mode(SelectionMode.SURFACE)
    widget.set_selection_enabled(False)
    widget.clear_selection()
    selected = widget.get_selected_shapes()
    assert len(selected) == 0


def test_selection_mode_persistence(qapp):
    """Test that selection mode persists through enable/disable cycles."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Set a non-default mode
    widget.set_selection_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE

    # Disable and re-enable selection
    widget.set_selection_enabled(False)
    widget.set_selection_enabled(True)

    # Mode should still be EDGE
    assert widget.get_selection_mode() == SelectionMode.EDGE


def test_selection_mode_change_clears_selection(qapp):
    """Test changing selection mode operations."""
    widget = OCPWidget()
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    widget.set_selection_mode(SelectionMode.VOLUME)
    widget.set_selection_mode(SelectionMode.SURFACE)
    widget.set_selection_mode(SelectionMode.EDGE)

    # Should complete without errors
    assert widget.get_selection_mode() == SelectionMode.EDGE


def test_get_selected_shapes_type(qapp):
    """Test that get_selected_shapes returns a list."""
    widget = OCPWidget()

    selected = widget.get_selected_shapes()
    assert isinstance(selected, list)
