"""
Tests for ViewToolbar component
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from cad_widgets.widgets.view_toolbar import ViewToolbar


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_toolbar_creation_horizontal(qapp):
    """Test horizontal toolbar creation."""
    toolbar = ViewToolbar(orientation='horizontal')
    assert toolbar is not None


def test_toolbar_creation_vertical(qapp):
    """Test vertical toolbar creation."""
    toolbar = ViewToolbar(orientation='vertical')
    assert toolbar is not None


def test_default_projection_type(qapp):
    """Test default projection type is perspective."""
    toolbar = ViewToolbar()
    assert toolbar.get_projection_type() == 'perspective'


def test_default_display_mode(qapp):
    """Test default display mode is shaded."""
    toolbar = ViewToolbar()
    assert toolbar.get_display_mode() == 'shaded'


def test_set_projection_type(qapp):
    """Test setting projection type programmatically."""
    toolbar = ViewToolbar()
    
    toolbar.set_projection_type('orthographic')
    assert toolbar.get_projection_type() == 'orthographic'
    
    toolbar.set_projection_type('perspective')
    assert toolbar.get_projection_type() == 'perspective'


def test_set_display_mode(qapp):
    """Test setting display mode programmatically."""
    toolbar = ViewToolbar()
    
    toolbar.set_display_mode('wireframe')
    assert toolbar.get_display_mode() == 'wireframe'
    
    toolbar.set_display_mode('shaded')
    assert toolbar.get_display_mode() == 'shaded'


def test_projection_changed_signal(qapp):
    """Test projection changed signal emission."""
    toolbar = ViewToolbar()
    
    received_signals = []
    toolbar.projection_changed.connect(lambda proj: received_signals.append(proj))
    
    # Simulate button clicks by calling the internal method
    toolbar._on_projection_changed('iso')
    toolbar._on_projection_changed('top')
    toolbar._on_projection_changed('front')
    
    assert len(received_signals) == 3
    assert received_signals == ['iso', 'top', 'front']


def test_projection_type_changed_signal(qapp):
    """Test projection type changed signal emission."""
    toolbar = ViewToolbar()
    
    received_signals = []
    toolbar.projection_type_changed.connect(lambda ptype: received_signals.append(ptype))
    
    toolbar.set_projection_type('orthographic')
    
    # Should have received the signal
    assert 'orthographic' in received_signals


def test_display_mode_changed_signal(qapp):
    """Test display mode changed signal emission."""
    toolbar = ViewToolbar()
    
    received_signals = []
    toolbar.display_mode_changed.connect(lambda mode: received_signals.append(mode))
    
    toolbar.set_display_mode('wireframe')
    
    # Should have received the signal
    assert 'wireframe' in received_signals


def test_fit_all_signal(qapp):
    """Test fit all signal emission."""
    toolbar = ViewToolbar()
    
    signal_received = []
    toolbar.fit_all_requested.connect(lambda: signal_received.append(True))
    
    toolbar._on_fit_all_requested()
    
    assert len(signal_received) == 1


def test_clear_signal(qapp):
    """Test clear signal emission."""
    toolbar = ViewToolbar()
    
    signal_received = []
    toolbar.clear_requested.connect(lambda: signal_received.append(True))
    
    toolbar._on_clear_requested()
    
    assert len(signal_received) == 1


def test_multiple_signal_connections(qapp):
    """Test that multiple signals work together."""
    toolbar = ViewToolbar()
    
    events = []
    
    toolbar.projection_changed.connect(lambda p: events.append(('projection', p)))
    toolbar.projection_type_changed.connect(lambda pt: events.append(('proj_type', pt)))
    toolbar.display_mode_changed.connect(lambda dm: events.append(('display_mode', dm)))
    toolbar.fit_all_requested.connect(lambda: events.append(('fit_all', None)))
    toolbar.clear_requested.connect(lambda: events.append(('clear', None)))
    
    # Trigger various events
    toolbar._on_projection_changed('iso')
    toolbar.set_projection_type('orthographic')
    toolbar.set_display_mode('wireframe')
    toolbar._on_fit_all_requested()
    toolbar._on_clear_requested()
    
    # Check that we received signals
    assert len(events) >= 5
    assert ('projection', 'iso') in events
    assert ('fit_all', None) in events
    assert ('clear', None) in events


def test_case_insensitive_setters(qapp):
    """Test that setters work with different case."""
    toolbar = ViewToolbar()
    
    toolbar.set_projection_type('ORTHOGRAPHIC')
    assert toolbar.get_projection_type() == 'orthographic'
    
    toolbar.set_display_mode('WIREFRAME')
    assert toolbar.get_display_mode() == 'wireframe'
