"""
Tests for ViewToolbar and SelectionToolbar components
"""


from cad_widgets.widgets.view_toolbar import ViewToolbar
from cad_widgets.widgets.selection_toolbar import SelectionToolbar
from cad_widgets import ViewDirection, ProjectionType, DisplayMode, SelectionMode


def test_toolbar_creation_horizontal(qapp):
    """Test horizontal toolbar creation."""
    toolbar = ViewToolbar(orientation="horizontal")
    assert toolbar is not None


def test_toolbar_creation_vertical(qapp):
    """Test vertical toolbar creation."""
    toolbar = ViewToolbar(orientation="vertical")
    assert toolbar is not None


def test_default_projection_type(qapp):
    """Test default projection type is perspective."""
    toolbar = ViewToolbar()
    assert toolbar.get_projection_type() == "orthographic"


def test_default_display_mode(qapp):
    """Test default display mode is shaded."""
    toolbar = ViewToolbar()
    assert toolbar.get_display_mode() == "shaded"


def test_set_projection_type(qapp):
    """Test setting projection type programmatically."""
    toolbar = ViewToolbar()

    toolbar.set_projection_type(ProjectionType.ORTHOGRAPHIC)
    assert toolbar.get_projection_type() == "orthographic"

    toolbar.set_projection_type(ProjectionType.PERSPECTIVE)
    assert toolbar.get_projection_type() == "perspective"


def test_set_display_mode(qapp):
    """Test setting display mode programmatically."""
    toolbar = ViewToolbar()

    toolbar.set_display_mode(DisplayMode.WIREFRAME)
    assert toolbar.get_display_mode() == "wireframe"

    toolbar.set_display_mode(DisplayMode.SHADED)
    assert toolbar.get_display_mode() == "shaded"


def test_projection_changed_signal(qapp):
    """Test projection changed signal emission."""
    toolbar = ViewToolbar()

    received_signals = []
    toolbar.projection_changed.connect(lambda proj: received_signals.append(proj))

    # Simulate button clicks by calling the internal method
    toolbar._on_projection_changed(ViewDirection.ISO)
    toolbar._on_projection_changed(ViewDirection.TOP)
    toolbar._on_projection_changed(ViewDirection.FRONT)

    assert len(received_signals) == 3
    assert received_signals == ["iso", "top", "front"]


def test_projection_type_changed_signal(qapp):
    """Test projection type changed signal emission."""
    toolbar = ViewToolbar()

    received_signals = []
    toolbar.projection_type_changed.connect(
        lambda ptype: received_signals.append(ptype)
    )

    toolbar.set_projection_type(ProjectionType.PERSPECTIVE)

    # Should have received the signal
    assert "perspective" in received_signals


def test_display_mode_changed_signal(qapp):
    """Test display mode changed signal emission."""
    toolbar = ViewToolbar()

    received_signals = []
    toolbar.display_mode_changed.connect(lambda mode: received_signals.append(mode))

    toolbar.set_display_mode(DisplayMode.WIREFRAME)

    # Should have received the signal
    assert "wireframe" in received_signals


def test_fit_all_signal(qapp):
    """Test fit all signal emission."""
    toolbar = ViewToolbar()

    signal_received = []
    toolbar.fit_all_requested.connect(lambda: signal_received.append(True))

    toolbar._on_fit_all_requested()

    assert len(signal_received) == 1


def test_multiple_signal_connections(qapp):
    """Test that multiple signals work together."""
    toolbar = ViewToolbar()

    events = []

    toolbar.projection_changed.connect(lambda p: events.append(("projection", p)))
    toolbar.projection_type_changed.connect(lambda pt: events.append(("proj_type", pt)))
    toolbar.display_mode_changed.connect(lambda dm: events.append(("display_mode", dm)))
    toolbar.fit_all_requested.connect(lambda: events.append(("fit_all", None)))

    # Trigger various events
    toolbar._on_projection_changed(ViewDirection.ISO)
    toolbar.set_projection_type(ProjectionType.PERSPECTIVE)
    toolbar.set_display_mode(DisplayMode.WIREFRAME)
    toolbar._on_fit_all_requested()

    # Check that we received signals
    assert len(events) >= 4
    assert ("projection", "iso") in events
    assert ("fit_all", None) in events


def test_case_insensitive_setters(qapp):
    """Test that setters work with enum values."""
    toolbar = ViewToolbar()

    toolbar.set_projection_type(ProjectionType.ORTHOGRAPHIC)
    assert toolbar.get_projection_type() == "orthographic"

    toolbar.set_display_mode(DisplayMode.WIREFRAME)
    assert toolbar.get_display_mode() == "wireframe"


# ============================================================================
# SelectionToolbar Tests
# ============================================================================


def test_selection_toolbar_creation_horizontal(qapp):
    """Test horizontal selection toolbar creation."""
    toolbar = SelectionToolbar(orientation="horizontal")
    assert toolbar is not None


def test_selection_toolbar_creation_vertical(qapp):
    """Test vertical selection toolbar creation."""
    toolbar = SelectionToolbar(orientation="vertical")
    assert toolbar is not None


def test_selection_toolbar_default_mode(qapp):
    """Test default selection mode is volume."""
    toolbar = SelectionToolbar()
    assert toolbar.get_current_mode() == SelectionMode.VOLUME


def test_set_selection_mode_programmatically(qapp):
    """Test setting selection mode programmatically."""
    toolbar = SelectionToolbar()

    toolbar.set_mode(SelectionMode.SURFACE)
    assert toolbar.get_current_mode() == SelectionMode.SURFACE

    toolbar.set_mode(SelectionMode.EDGE)
    assert toolbar.get_current_mode() == SelectionMode.EDGE

    toolbar.set_mode(SelectionMode.VERTEX)
    assert toolbar.get_current_mode() == SelectionMode.VERTEX

    toolbar.set_mode(SelectionMode.VOLUME)
    assert toolbar.get_current_mode() == SelectionMode.VOLUME


def test_selection_mode_changed_signal(qapp):
    """Test selection mode changed signal emission."""
    toolbar = SelectionToolbar()

    received_signals = []
    toolbar.selection_mode_changed.connect(lambda mode: received_signals.append(mode))

    toolbar.set_mode(SelectionMode.SURFACE)
    toolbar.set_mode(SelectionMode.EDGE)
    toolbar.set_mode(SelectionMode.VERTEX)

    assert len(received_signals) == 3
    assert "surface" in received_signals
    assert "edge" in received_signals
    assert "vertex" in received_signals


def test_selection_toolbar_all_modes(qapp):
    """Test all selection modes can be set."""
    toolbar = SelectionToolbar()

    modes = [
        SelectionMode.VOLUME,
        SelectionMode.SURFACE,
        SelectionMode.EDGE,
        SelectionMode.VERTEX,
    ]

    for mode in modes:
        toolbar.set_mode(mode)
        assert toolbar.get_current_mode() == mode


def test_selection_toolbar_mode_signal(qapp):
    """Test mode change signal working."""
    toolbar = SelectionToolbar()

    events = []

    toolbar.selection_mode_changed.connect(lambda m: events.append(("mode", m)))

    toolbar.set_mode(SelectionMode.EDGE)

    assert len(events) >= 1
    assert ("mode", "edge") in events
