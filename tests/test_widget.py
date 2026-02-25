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


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


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


def test_projection_types(qapp):
    """Test setting projection types."""
    widget = OCPWidget()
    
    # Test perspective
    widget.set_projection_type('perspective')
    
    # Test orthographic
    widget.set_projection_type('orthographic')


def test_display_modes(qapp):
    """Test setting display modes."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    # Test shaded mode
    widget.set_display_mode('shaded')
    
    # Test wireframe mode
    widget.set_display_mode('wireframe')
    
    # Test both mode
    widget.set_display_mode('both')


def test_standard_views(qapp):
    """Test standard view projections."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    views = ['iso', 'front', 'back', 'top', 'bottom', 'left', 'right']
    for view in views:
        widget.set_projection(view)


def test_erase_all(qapp):
    """Test clearing all shapes."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    widget.erase_all()


def test_fit_all(qapp):
    """Test fit all operation."""
    widget = OCPWidget()
    box = create_box(100, 100, 100)
    widget.display_shape(box)
    
    widget.fit_all()
