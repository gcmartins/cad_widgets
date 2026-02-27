"""
Integration tests for SelectionToolbar and OCPWidget working together
Tests the full workflow of selection functionality with connected components
"""

import sys

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from cad_widgets import OCPWidget, SelectionMode
from cad_widgets.widgets.selection_toolbar import SelectionToolbar
from cad_widgets.utils import create_box, create_sphere, create_cylinder


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_toolbar_widget_integration_basic(qapp):
    """Test basic integration of toolbar with widget."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    toolbar.clear_selection_requested.connect(widget.clear_selection)
    
    # Verify initial states match
    assert toolbar.is_selection_enabled() == widget.is_selection_enabled()
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


def test_toolbar_disables_widget_selection(qapp):
    """Test that disabling selection in toolbar disables it in widget."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    
    # Disable via toolbar
    toolbar.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False
    
    # Enable via toolbar
    toolbar.set_selection_enabled(True)
    assert widget.is_selection_enabled() is True


def test_toolbar_clears_widget_selection(qapp):
    """Test that toolbar clear button clears widget selection."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect clear signal
    clear_called = []
    toolbar.clear_selection_requested.connect(lambda: clear_called.append(True))
    toolbar.clear_selection_requested.connect(widget.clear_selection)
    
    # Display a shape
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Trigger clear from toolbar
    toolbar._on_clear_selection()
    
    # Verify signal was received
    assert len(clear_called) == 1
    
    # Verify widget's selection is empty
    selected = widget.get_selected_shapes()
    assert len(selected) == 0


def test_full_integration_workflow(qapp):
    """Test complete integration workflow with all signals."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Track all events
    events = []
    
    # Connect all signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: [
            events.append(('mode_changed', mode_str)),
            widget.set_selection_mode(SelectionMode(mode_str))
        ]
    )
    toolbar.selection_enabled_changed.connect(
        lambda enabled: [
            events.append(('enabled_changed', enabled)),
            widget.set_selection_enabled(enabled)
        ]
    )
    toolbar.clear_selection_requested.connect(
        lambda: [
            events.append(('clear_requested', None)),
            widget.clear_selection()
        ]
    )
    
    # Display shapes
    box = create_box(100, 100, 100)
    sphere = create_sphere(50)
    widget.display_shape(box)
    widget.display_shape(sphere)
    
    # Perform various operations via toolbar
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    assert ('mode_changed', 'surface') in events
    
    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE
    assert ('mode_changed', 'edge') in events
    
    toolbar.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False
    assert ('enabled_changed', False) in events
    
    toolbar.set_selection_enabled(True)
    assert widget.is_selection_enabled() is True
    assert ('enabled_changed', True) in events
    
    toolbar._on_clear_selection()
    assert ('clear_requested', None) in events


def test_multiple_mode_changes_with_shapes(qapp):
    """Test changing selection modes multiple times with shapes displayed."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    
    # Display multiple shapes
    box = create_box(100, 100, 100)
    sphere = create_sphere(50)
    widget.display_shape(box)
    widget.display_shape(sphere)
    
    # Cycle through all modes multiple times
    modes = [SelectionMode.VOLUME, SelectionMode.SURFACE, SelectionMode.EDGE, SelectionMode.VERTEX]
    
    for _ in range(3):  # Cycle 3 times
        for mode in modes:
            toolbar.set_mode(mode)
            assert widget.get_selection_mode() == mode


def test_disable_enable_cycle_with_mode_changes(qapp):
    """Test disabling and enabling selection while changing modes."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    
    # Display a shape
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Set a mode
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    
    # Disable selection
    toolbar.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False
    
    # Change mode while disabled (signal won't emit)
    toolbar.set_mode(SelectionMode.EDGE)
    # Widget mode should still be SURFACE (not updated because disabled)
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    
    # Enable selection
    toolbar.set_selection_enabled(True)
    assert widget.is_selection_enabled() is True
    
    # Now the mode should update
    toolbar.set_mode(SelectionMode.VERTEX)
    assert widget.get_selection_mode() == SelectionMode.VERTEX


def test_toolbar_state_persistence(qapp):
    """Test that toolbar state persists through disable/enable cycles."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    
    # Set specific mode
    toolbar.set_mode(SelectionMode.EDGE)
    assert widget.get_selection_mode() == SelectionMode.EDGE
    
    # Disable and re-enable
    toolbar.set_selection_enabled(False)
    toolbar.set_selection_enabled(True)
    
    # Widget maintains its mode through the cycle
    assert widget.get_selection_mode() == SelectionMode.EDGE
    
    # Toolbar shows correct mode
    assert toolbar.get_current_mode() == SelectionMode.EDGE


def test_clear_selection_multiple_times_integration(qapp):
    """Test clearing selection multiple times through toolbar."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.clear_selection_requested.connect(widget.clear_selection)
    
    # Display shapes
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Clear multiple times (should not cause errors)
    for _ in range(5):
        toolbar._on_clear_selection()
        selected = widget.get_selected_shapes()
        assert len(selected) == 0


def test_simultaneous_toolbar_widget_updates(qapp):
    """Test that toolbar and widget stay synchronized during rapid changes."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect all signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    
    # Display shapes
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Rapid sequence of changes
    toolbar.set_mode(SelectionMode.SURFACE)
    toolbar.set_selection_enabled(False)
    toolbar.set_mode(SelectionMode.EDGE)  # Won't emit signal
    toolbar.set_selection_enabled(True)
    toolbar.set_mode(SelectionMode.VERTEX)
    toolbar.set_mode(SelectionMode.VOLUME)
    
    # Verify final state is consistent
    assert toolbar.is_selection_enabled() == widget.is_selection_enabled()
    assert toolbar.get_current_mode() == widget.get_selection_mode()


def test_toolbar_with_no_shapes(qapp):
    """Test toolbar-widget integration with no shapes displayed."""
    toolbar = SelectionToolbar()
    widget = OCPWidget()
    
    # Connect signals
    toolbar.selection_mode_changed.connect(
        lambda mode_str: widget.set_selection_mode(SelectionMode(mode_str))
    )
    toolbar.selection_enabled_changed.connect(widget.set_selection_enabled)
    toolbar.clear_selection_requested.connect(widget.clear_selection)
    
    # Perform operations without shapes
    toolbar.set_mode(SelectionMode.SURFACE)
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    
    toolbar.set_selection_enabled(False)
    assert widget.is_selection_enabled() is False
    
    toolbar._on_clear_selection()
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
    box1 = create_box(100, 100, 100)
    box2 = create_box(50, 50, 50)
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
    box = create_box(100, 100, 100)
    sphere = create_sphere(50)
    cylinder = create_cylinder(30, 80)
    
    widget.display_shape(box, color=(0.8, 0.2, 0.2))
    widget.display_shape(sphere, color=(0.2, 0.8, 0.2))
    widget.display_shape(cylinder, color=(0.2, 0.2, 0.8))
    
    # Test all selection modes work with various shapes
    modes = [SelectionMode.VOLUME, SelectionMode.SURFACE, SelectionMode.EDGE, SelectionMode.VERTEX]
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
    toolbar.clear_selection_requested.connect(widget.clear_selection)
    
    # Display shapes
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Set selection mode
    toolbar.set_mode(SelectionMode.SURFACE)
    
    # Clear shapes
    widget.erase_all()
    
    # Selection mode should persist
    assert widget.get_selection_mode() == SelectionMode.SURFACE
    
    # Add new shapes
    sphere = create_sphere(50)
    widget.display_shape(sphere)
    
    # Selection mode still active
    assert widget.get_selection_mode() == SelectionMode.SURFACE
