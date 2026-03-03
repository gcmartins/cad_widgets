"""
Integration tests for SelectionToolbar and OCPWidget working together
Tests the full workflow of selection functionality with connected components
"""



from cad_widgets import OCPWidget, SelectionMode, GeometryService
from cad_widgets.widgets.selection_toolbar import SelectionToolbar


def test_toolbar_widget_integration_basic(qapp):
    """Test basic integration of toolbar with widget."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Verify initial states match
    assert toolbar.get_current_mode() == widget.get_selection_mode()


def test_toolbar_changes_widget_selection_mode(qapp):
    """Test that toolbar mode changes update the widget."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Change modes via toolbar and verify widget follows
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE

    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE

    toolbar.set_mode(SelectionMode.VERTEX)
    assert widget.get_selection_mode() == SelectionMode.VERTEX

    toolbar.set_mode(SelectionMode.VOLUME)
    assert widget.get_selection_mode() == SelectionMode.VOLUME


def test_full_integration_workflow(qapp):
    """Test complete integration workflow with all signals."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Track all events
    events = []

    # Connect all signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: [
            events.append(("mode_changed", mode_str)),
            widget.set_selection_mode(SelectionMode(mode_str)),
        ]
    )

    # Display shapes
    box = GeometryService().create_box(100, 100, 100)
    sphere = GeometryService().create_sphere(50)
    widget.display_shape(box)
    widget.display_shape(sphere)

    # Perform various operations via toolbar
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    assert ("mode_changed", "surface") in events

    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE
    assert ("mode_changed", "edge") in events


def test_multiple_mode_changes_with_shapes(qapp):
    """Test changing selection modes multiple times with shapes displayed."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Display multiple shapes
    box = GeometryService().create_box(100, 100, 100)
    sphere = GeometryService().create_sphere(50)
    widget.display_shape(box)
    widget.display_shape(sphere)

    # Cycle through all modes multiple times
    modes = [
        SelectionMode.VOLUME,
        SelectionMode.SURFACE,
        SelectionMode.EDGE,
        SelectionMode.VERTEX,
    ]

    for _ in range(3):  # Cycle 3 times
        for mode in modes:
            toolbar.set_mode(mode)
            assert widget.get_selection_mode() == mode


def test_toolbar_state_persistence(qapp):
    """Test that toolbar state persists."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Set specific mode
    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE

    # Toolbar shows correct mode
    assert toolbar.get_current_mode() == SelectionMode.EDGE


def test_simultaneous_toolbar_widget_updates(qapp):
    """Test that toolbar and widget stay synchronized during rapid changes."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect all signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Display shapes
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Rapid sequence of mode changes
    toolbar.set_mode(SelectionMode.SURFACE)
    toolbar.set_mode(SelectionMode.EDGE)
    toolbar.set_mode(SelectionMode.VERTEX)
    toolbar.set_mode(SelectionMode.VOLUME)

    # Verify final state is consistent
    assert toolbar.get_current_mode() == widget.get_selection_mode()
    assert widget.get_selection_mode() == SelectionMode.VOLUME


def test_toolbar_with_no_shapes(qapp):
    """Test toolbar-widget integration with no shapes displayed."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Perform operations without shapes
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE

    selected = widget.get_selected_shapes()
    assert len(selected) == 0


def test_widget_direct_changes_independent_of_toolbar(qapp):
    """Test that widget can be changed directly without affecting toolbar state."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Don't connect signals - test independence

    # Set different states
    toolbar.set_mode(SelectionMode.SURFACE)
    widget.set_selection_mode(SelectionMode.VERTEX)

    # They should be independent
    assert toolbar.get_current_mode() == SelectionMode.SURFACE
    assert widget.get_selection_mode() == SelectionMode.VERTEX


def test_reconnect_signals(qapp):
    """Test that signals can be disconnected and reconnected."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    connection = toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Test connection works
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE

    # Disconnect
    toolbar.selection_mode_changed.disconnect(connection)

    # Change should not propagate
    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE  # Still old value

    # Reconnect
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Should work again
    toolbar.set_mode(SelectionMode.VERTEX)
    assert widget.get_selection_mode() == SelectionMode.VERTEX


def test_multiple_widgets_single_toolbar(qapp):
    """Test one toolbar controlling multiple widgets."""
    toolbar = SelectionToolbar()
    widget1 = OCPWidget()
    widget2 = OCPWidget()

    # Connect toolbar to both widgets
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget1.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget2.set_selection_mode(SelectionMode(mode_str))
    )

    # Display shapes in both widgets
    box1 = GeometryService().create_box(100, 100, 100)
    box2 = GeometryService().create_box(50, 50, 50)
    widget1.display_shape(box1)
    widget2.display_shape(box2)

    # Change mode via toolbar
    toolbar.set_mode(SelectionMode.EDGE)

    # Both widgets should update
    assert widget1.get_selection_mode() == SelectionMode.EDGE
    assert widget2.get_selection_mode() == SelectionMode.EDGE


def test_toolbar_widget_with_all_shape_types(qapp):
    """Test integration with various shape types."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Display various shapes
    box = GeometryService().create_box(100, 100, 100)
    sphere = GeometryService().create_sphere(50)
    cylinder = GeometryService().create_cylinder(30, 80)

    widget.display_shape(box, color=(0.8, 0.2, 0.2))
    widget.display_shape(sphere, color=(0.2, 0.8, 0.2))
    widget.display_shape(cylinder, color=(0.2, 0.2, 0.8))

    # Test all selection modes work with various shapes
    modes = [
        SelectionMode.VOLUME,
        SelectionMode.SURFACE,
        SelectionMode.EDGE,
        SelectionMode.VERTEX,
    ]
    for mode in modes:
        toolbar.set_mode(mode)
        assert widget.get_selection_mode() == mode


def test_clear_and_reload_shapes(qapp):
    """Test clearing and reloading shapes with selection active."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()

    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )

    # Display shapes
    box = GeometryService().create_box(100, 100, 100)
    widget.display_shape(box)

    # Set selection mode
    toolbar.set_mode(SelectionMode.SURFACE)

    # Clear shapes
    widget.erase_all()

    # Selection mode should persist
    assert widget.get_selection_mode() == SelectionMode.SURFACE

    # Add new shapes
    sphere = GeometryService().create_sphere(50)
    widget.display_shape(sphere)

    # Selection mode still active
    assert widget.get_selection_mode() == SelectionMode.SURFACE
