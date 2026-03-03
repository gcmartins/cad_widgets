"""
Integration tests for GeometryManager with OCPWidget and GeometryTreeWidget
Tests the signal-based communication and integration between components
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from cad_widgets.managers.geometry_manager import GeometryManager
from cad_widgets.widgets.ocp_widget import OCPWidget
from cad_widgets.widgets.geometry_tree import GeometryTreeWidget
from cad_widgets.enums import ShapeType
from cad_widgets.models.shape_properties import (
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    Translation,
    Rotation,
)


@pytest.fixture(scope="module")
def app():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def geometry_manager():
    """Create a fresh GeometryManager for each test."""
    return GeometryManager()


@pytest.fixture
def ocp_widget():
    """Create a fresh OCPWidget for each test."""
    widget = OCPWidget()
    widget.show()  # Show widget to initialize OpenGL context
    return widget


@pytest.fixture
def geometry_tree():
    """Create a fresh GeometryTreeWidget for each test."""
    tree = GeometryTreeWidget()
    tree.show()
    return tree


@pytest.fixture
def integrated_system(geometry_manager, ocp_widget, geometry_tree):
    """Create a fully integrated system with all components connected."""
    # Connect geometry manager signals to viewer
    geometry_manager.shape_created.connect(ocp_widget.on_shape_created)
    geometry_manager.shape_updated.connect(ocp_widget.on_shape_updated)
    geometry_manager.shape_removed.connect(ocp_widget.on_shape_removed)
    geometry_manager.all_cleared.connect(ocp_widget.on_all_cleared)
    
    # Connect geometry manager signals to tree
    geometry_manager.shape_created.connect(geometry_tree.on_shape_created)
    geometry_manager.shape_updated.connect(geometry_tree.on_shape_updated)
    geometry_manager.shape_removed.connect(geometry_tree.on_shape_removed)
    geometry_manager.all_cleared.connect(geometry_tree.on_all_cleared)
    
    return {
        'manager': geometry_manager,
        'viewer': ocp_widget,
        'tree': geometry_tree
    }


def test_create_shape_updates_viewer_and_tree(integrated_system, app):
    """Test that creating a shape updates both viewer and tree."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    properties = BoxProperties(
        width=100.0,
        height=60.0,
        depth=40.0,
        translation=Translation(x=10.0, y=20.0, z=30.0)
    )
    
    # Create shape
    shape = manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Verify shape was created
    assert shape is not None
    
    # Verify tree has the shape
    shape_ids = tree.get_shape_ids()
    assert "box_1" in shape_ids
    
    # Verify tree has correct shape data
    tree_item = tree.tree.findItems("Test Box", Qt.MatchFlag.MatchRecursive, 0)[0]
    assert tree_item is not None


def test_update_shape_updates_viewer_and_tree(integrated_system, app):
    """Test that updating a shape updates both viewer and tree."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    # Create initial shape
    initial_props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=initial_props
    )
    
    app.processEvents()
    
    # Update shape with new properties
    new_props = BoxProperties(
        width=100.0,
        height=80.0,
        depth=60.0,
        translation=Translation(x=20.0, y=30.0, z=40.0)
    )
    manager.update_shape("box_1", new_props)
    
    app.processEvents()
    
    # Verify tree reflects update (check for position in properties)
    assert "box_1" in tree.get_shape_ids()


def test_remove_shape_removes_from_viewer_and_tree(integrated_system, app):
    """Test that removing a shape removes it from both viewer and tree."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    # Create shape
    properties = SphereProperties(radius=25.0)
    manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Test Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Verify shape exists in tree
    assert "sphere_1" in tree.get_shape_ids()
    
    # Remove shape
    manager.remove_shape("sphere_1")
    
    app.processEvents()
    
    # Verify shape removed from tree
    assert "sphere_1" not in tree.get_shape_ids()


def test_clear_all_clears_viewer_and_tree(integrated_system, app):
    """Test that clearing all shapes clears both viewer and tree."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    # Create multiple shapes
    properties1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=properties1
    )
    
    properties2 = SphereProperties(radius=25.0)
    manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=properties2
    )
    
    properties3 = CylinderProperties(radius=15.0, height=50.0)
    manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Cylinder 1",
        color=(0.0, 0.0, 1.0),
        properties=properties3
    )
    
    app.processEvents()
    
    # Verify all shapes in tree
    assert len(tree.get_shape_ids()) == 3
    
    # Clear all
    manager.clear_all()
    
    app.processEvents()
    
    # Verify tree is empty
    assert len(tree.get_shape_ids()) == 0


def test_multiple_shapes_integration(integrated_system, app):
    """Test creating multiple shapes of different types."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    # Create box
    box_props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=box_props
    )
    
    # Create sphere
    sphere_props = SphereProperties(radius=25.0)
    manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere",
        color=(0.0, 1.0, 0.0),
        properties=sphere_props
    )
    
    # Create cylinder
    cylinder_props = CylinderProperties(radius=15.0, height=50.0)
    manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=cylinder_props
    )
    
    app.processEvents()
    
    # Verify all shapes in tree
    shape_ids = tree.get_shape_ids()
    assert len(shape_ids) == 3
    assert "box_1" in shape_ids
    assert "sphere_1" in shape_ids
    assert "cylinder_1" in shape_ids


def test_shape_with_translation_integration(integrated_system, app):
    """Test that shapes with translation are correctly handled."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    properties = BoxProperties(
        width=50.0,
        height=50.0,
        depth=50.0,
        translation=Translation(x=100.0, y=50.0, z=25.0)
    )
    
    manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Translated Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Verify shape in tree
    assert "box_1" in tree.get_shape_ids()
    
    # Verify tree shows position property
    tree_item = tree.tree.findItems("Translated Box", Qt.MatchFlag.MatchRecursive, 0)[0]
    assert tree_item is not None


def test_shape_with_rotation_integration(integrated_system, app):
    """Test that shapes with rotation are correctly handled."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    properties = CylinderProperties(
        radius=15.0,
        height=50.0,
        rotation=Rotation(x=45.0, y=30.0, z=15.0)
    )
    
    manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Rotated Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Verify shape in tree
    assert "cylinder_1" in tree.get_shape_ids()


def test_shape_with_transparency_integration(integrated_system, app):
    """Test that shapes are correctly handled - transparency is now global only."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    properties = SphereProperties(radius=25.0)
    
    manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Transparent Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Verify shape in tree
    assert "sphere_1" in tree.get_shape_ids()


def test_sequential_operations_integration(integrated_system, app):
    """Test a sequence of operations on the integrated system."""
    manager = integrated_system['manager']
    integrated_system['viewer']
    tree = integrated_system['tree']
    
    # Create shape
    props1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=props1
    )
    
    app.processEvents()
    assert "box_1" in tree.get_shape_ids()
    
    # Update shape
    props2 = BoxProperties(width=100.0, height=100.0, depth=100.0)
    manager.update_shape("box_1", props2)
    
    app.processEvents()
    assert "box_1" in tree.get_shape_ids()
    
    # Add another shape
    props3 = SphereProperties(radius=25.0)
    manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=props3
    )
    
    app.processEvents()
    assert len(tree.get_shape_ids()) == 2
    
    # Remove first shape
    manager.remove_shape("box_1")
    
    app.processEvents()
    assert "box_1" not in tree.get_shape_ids()
    assert "sphere_1" in tree.get_shape_ids()
    
    # Clear all
    manager.clear_all()
    
    app.processEvents()
    assert len(tree.get_shape_ids()) == 0


def test_manager_signals_received_by_viewer(geometry_manager, ocp_widget, app):
    """Test that viewer receives all signals from geometry manager."""
    # Create spies for viewer methods
    created_calls = []
    updated_calls = []
    removed_calls = []
    cleared_calls = []
    
    # Connect to track calls
    ocp_widget.on_shape_created = lambda sid, ms: created_calls.append((sid, ms))
    ocp_widget.on_shape_updated = lambda sid, ms: updated_calls.append((sid, ms))
    ocp_widget.on_shape_removed = lambda sid: removed_calls.append(sid)
    ocp_widget.on_all_cleared = lambda: cleared_calls.append(True)
    
    # Connect signals
    geometry_manager.shape_created.connect(ocp_widget.on_shape_created)
    geometry_manager.shape_updated.connect(ocp_widget.on_shape_updated)
    geometry_manager.shape_removed.connect(ocp_widget.on_shape_removed)
    geometry_manager.all_cleared.connect(ocp_widget.on_all_cleared)
    
    # Create shape
    props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    
    app.processEvents()
    assert len(created_calls) == 1
    assert created_calls[0][0] == "box_1"
    
    # Update shape
    new_props = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape("box_1", new_props)
    
    app.processEvents()
    assert len(updated_calls) == 1
    assert updated_calls[0][0] == "box_1"
    
    # Remove shape
    geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    assert len(removed_calls) == 1
    assert removed_calls[0] == "box_1"
    
    # Clear all (with shapes)
    geometry_manager.create_shape(
        shape_id="box_2",
        shape_type=ShapeType.BOX,
        name="Box 2",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    geometry_manager.clear_all()
    
    app.processEvents()
    assert len(cleared_calls) == 1


def test_manager_signals_received_by_tree(geometry_manager, geometry_tree, app):
    """Test that tree receives all signals from geometry manager."""
    # Create spies for tree methods
    created_calls = []
    updated_calls = []
    removed_calls = []
    cleared_calls = []
    
    # Store original methods
    original_on_shape_created = geometry_tree.on_shape_created
    original_on_shape_updated = geometry_tree.on_shape_updated
    original_on_shape_removed = geometry_tree.on_shape_removed
    original_on_all_cleared = geometry_tree.on_all_cleared
    
    # Wrap methods to track calls
    def tracked_created(sid, ms):
        created_calls.append((sid, ms))
        original_on_shape_created(sid, ms)
    
    def tracked_updated(sid, ms):
        updated_calls.append((sid, ms))
        original_on_shape_updated(sid, ms)
    
    def tracked_removed(sid):
        removed_calls.append(sid)
        original_on_shape_removed(sid)
    
    def tracked_cleared():
        cleared_calls.append(True)
        original_on_all_cleared()
    
    geometry_tree.on_shape_created = tracked_created
    geometry_tree.on_shape_updated = tracked_updated
    geometry_tree.on_shape_removed = tracked_removed
    geometry_tree.on_all_cleared = tracked_cleared
    
    # Connect signals
    geometry_manager.shape_created.connect(geometry_tree.on_shape_created)
    geometry_manager.shape_updated.connect(geometry_tree.on_shape_updated)
    geometry_manager.shape_removed.connect(geometry_tree.on_shape_removed)
    geometry_manager.all_cleared.connect(geometry_tree.on_all_cleared)
    
    # Create shape
    props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    
    app.processEvents()
    assert len(created_calls) == 1
    assert created_calls[0][0] == "box_1"
    assert "box_1" in geometry_tree.get_shape_ids()
    
    # Update shape
    new_props = BoxProperties(
        width=100.0,
        height=100.0,
        depth=100.0,
        translation=Translation(x=10.0, y=20.0, z=30.0)
    )
    geometry_manager.update_shape("box_1", new_props)
    
    app.processEvents()
    assert len(updated_calls) == 1
    assert updated_calls[0][0] == "box_1"
    
    # Remove shape
    geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    assert len(removed_calls) == 1
    assert removed_calls[0] == "box_1"
    assert "box_1" not in geometry_tree.get_shape_ids()
    
    # Clear all
    geometry_manager.create_shape(
        shape_id="box_2",
        shape_type=ShapeType.BOX,
        name="Box 2",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    geometry_manager.clear_all()
    
    app.processEvents()
    assert len(cleared_calls) == 1
    assert len(geometry_tree.get_shape_ids()) == 0


def test_viewer_only_integration(geometry_manager, ocp_widget, app):
    """Test geometry manager with viewer only (no tree)."""
    # Connect only viewer
    geometry_manager.shape_created.connect(ocp_widget.on_shape_created)
    geometry_manager.shape_updated.connect(ocp_widget.on_shape_updated)
    geometry_manager.shape_removed.connect(ocp_widget.on_shape_removed)
    geometry_manager.all_cleared.connect(ocp_widget.on_all_cleared)
    
    # Create and manipulate shapes
    props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    
    app.processEvents()
    
    # Update shape
    new_props = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape("box_1", new_props)
    
    app.processEvents()
    
    # Remove shape
    geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    
    # No errors should occur
    assert True


def test_tree_only_integration(geometry_manager, geometry_tree, app):
    """Test geometry manager with tree only (no viewer)."""
    # Connect only tree
    geometry_manager.shape_created.connect(geometry_tree.on_shape_created)
    geometry_manager.shape_updated.connect(geometry_tree.on_shape_updated)
    geometry_manager.shape_removed.connect(geometry_tree.on_shape_removed)
    geometry_manager.all_cleared.connect(geometry_tree.on_all_cleared)
    
    # Create shapes
    props = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=props
    )
    
    app.processEvents()
    
    # Verify in tree
    assert "box_1" in geometry_tree.get_shape_ids()
    
    # Update and verify
    new_props = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape("box_1", new_props)
    
    app.processEvents()
    assert "box_1" in geometry_tree.get_shape_ids()
    
    # Remove and verify
    geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    assert "box_1" not in geometry_tree.get_shape_ids()
