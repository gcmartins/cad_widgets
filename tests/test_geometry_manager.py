"""
Tests for GeometryManager
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QSignalSpy

from cad_widgets.managers.geometry_manager import GeometryManager, ManagedShape
from cad_widgets.enums import ShapeType
from cad_widgets.models.shape_properties import (
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
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


def test_geometry_manager_initialization(geometry_manager):
    """Test that GeometryManager initializes correctly."""
    assert geometry_manager is not None
    assert len(geometry_manager.get_all_shape_ids()) == 0


def test_create_box_shape(geometry_manager, app):
    """Test creating a box shape."""
    properties = BoxProperties(
        width=100.0,
        height=60.0,
        depth=40.0,
        translation=Translation(x=10.0, y=20.0, z=30.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    spy = QSignalSpy(geometry_manager.shape_created)
    
    shape = geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    app.processEvents()
    
    # Check shape was created
    assert shape is not None
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == "box_1"
    assert isinstance(signal_args[1], ManagedShape)
    
    # Check managed shape
    managed_shape = geometry_manager.get_shape("box_1")
    assert managed_shape is not None
    assert managed_shape.shape_type == ShapeType.BOX
    assert managed_shape.name == "Test Box"
    assert managed_shape.color == (1.0, 0.0, 0.0)
    # Transparency is now global only, not per-shape
    assert managed_shape.properties == properties


def test_create_sphere_shape(geometry_manager, app):
    """Test creating a sphere shape."""
    properties = SphereProperties(
        radius=25.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Test Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("sphere_1")
    assert managed_shape is not None
    assert managed_shape.shape_type == ShapeType.SPHERE
    assert isinstance(managed_shape.properties, SphereProperties)
    assert managed_shape.properties.radius == 25.0


def test_create_cylinder_shape(geometry_manager, app):
    """Test creating a cylinder shape."""
    properties = CylinderProperties(
        radius=15.0,
        height=50.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Test Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("cylinder_1")
    assert managed_shape is not None
    assert managed_shape.shape_type == ShapeType.CYLINDER
    assert isinstance(managed_shape.properties, CylinderProperties)


def test_create_cone_shape(geometry_manager, app):
    """Test creating a cone shape."""
    properties = ConeProperties(
        radius=20.0,
        height=40.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="cone_1",
        shape_type=ShapeType.CONE,
        name="Test Cone",
        color=(1.0, 1.0, 0.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("cone_1")
    assert managed_shape is not None
    assert managed_shape.shape_type == ShapeType.CONE
    assert isinstance(managed_shape.properties, ConeProperties)


def test_create_torus_shape(geometry_manager, app):
    """Test creating a torus shape."""
    properties = TorusProperties(
        radius=30.0,
        length=10.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="torus_1",
        shape_type=ShapeType.TORUS,
        name="Test Torus",
        color=(1.0, 0.0, 1.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("torus_1")
    assert managed_shape is not None
    assert managed_shape.shape_type == ShapeType.TORUS
    assert isinstance(managed_shape.properties, TorusProperties)


def test_update_shape(geometry_manager, app):
    """Test updating a shape with new properties."""
    # Create initial shape
    initial_properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=initial_properties
    )
    
    spy = QSignalSpy(geometry_manager.shape_updated)
    
    # Update with new properties
    new_properties = BoxProperties(width=100.0, height=80.0, depth=60.0)
    updated_shape = geometry_manager.update_shape("box_1", new_properties)
    
    app.processEvents()
    
    # Check shape was updated
    assert updated_shape is not None
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == "box_1"
    assert isinstance(signal_args[1], ManagedShape)
    
    # Check updated properties
    managed_shape = geometry_manager.get_shape("box_1")
    assert managed_shape.properties.width == 100.0
    assert managed_shape.properties.height == 80.0
    assert managed_shape.properties.depth == 60.0


def test_update_nonexistent_shape(geometry_manager):
    """Test updating a shape that doesn't exist."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    result = geometry_manager.update_shape("nonexistent", properties)
    
    assert result is None


def test_remove_shape(geometry_manager, app):
    """Test removing a shape."""
    # Create shape
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    spy = QSignalSpy(geometry_manager.shape_removed)
    
    # Remove shape
    result = geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    
    # Check removal was successful
    assert result is True
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == "box_1"
    
    # Check shape is gone
    assert geometry_manager.get_shape("box_1") is None


def test_remove_nonexistent_shape(geometry_manager):
    """Test removing a shape that doesn't exist."""
    result = geometry_manager.remove_shape("nonexistent")
    assert result is False


def test_get_all_shape_ids(geometry_manager):
    """Test getting all shape IDs."""
    # Create multiple shapes
    properties1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    properties2 = SphereProperties(radius=25.0)
    properties3 = CylinderProperties(radius=15.0, height=50.0)
    
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=properties1
    )
    
    geometry_manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=properties2
    )
    
    geometry_manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Cylinder 1",
        color=(0.0, 0.0, 1.0),
        properties=properties3
    )
    
    shape_ids = geometry_manager.get_all_shape_ids()
    
    assert len(shape_ids) == 3
    assert "box_1" in shape_ids
    assert "sphere_1" in shape_ids
    assert "cylinder_1" in shape_ids


def test_clear_all(geometry_manager, app):
    """Test clearing all shapes."""
    # Create multiple shapes
    properties1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    properties2 = SphereProperties(radius=25.0)
    
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=properties1
    )
    
    geometry_manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=properties2
    )
    
    spy = QSignalSpy(geometry_manager.all_cleared)
    
    # Clear all
    geometry_manager.clear_all()
    
    app.processEvents()
    
    # Check all shapes are gone
    assert len(geometry_manager.get_all_shape_ids()) == 0
    
    # Check signal was emitted
    assert spy.count() == 1


def test_shape_with_translation(geometry_manager):
    """Test creating a shape with translation."""
    properties = BoxProperties(
        width=50.0,
        height=50.0,
        depth=50.0,
        translation=Translation(x=100.0, y=50.0, z=25.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Translated Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("box_1")
    assert managed_shape.properties.translation.x == 100.0
    assert managed_shape.properties.translation.y == 50.0
    assert managed_shape.properties.translation.z == 25.0


def test_shape_with_rotation(geometry_manager):
    """Test creating a shape with rotation."""
    properties = CylinderProperties(
        radius=15.0,
        height=50.0,
        rotation=Rotation(x=45.0, y=30.0, z=15.0)
    )
    
    shape = geometry_manager.create_shape(
        shape_id="cylinder_1",
        shape_type=ShapeType.CYLINDER,
        name="Rotated Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("cylinder_1")
    assert managed_shape.properties.rotation.x == 45.0
    assert managed_shape.properties.rotation.y == 30.0
    assert managed_shape.properties.rotation.z == 15.0


def test_shape_with_transparency(geometry_manager):
    """Test creating a shape - transparency is now global only."""
    properties = SphereProperties(radius=25.0)
    
    shape = geometry_manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Transparent Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    assert shape is not None
    managed_shape = geometry_manager.get_shape("sphere_1")
    # Transparency is no longer a per-shape property
    assert not hasattr(managed_shape, 'transparency')


def test_create_properties_for_type_box():
    """Test creating BoxProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.BOX,
        width=100.0,
        height=80.0,
        depth=60.0
    )
    
    assert isinstance(properties, BoxProperties)
    assert properties.width == 100.0
    assert properties.height == 80.0
    assert properties.depth == 60.0


def test_create_properties_for_type_sphere():
    """Test creating SphereProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.SPHERE,
        radius=30.0
    )
    
    assert isinstance(properties, SphereProperties)
    assert properties.radius == 30.0


def test_create_properties_for_type_cylinder():
    """Test creating CylinderProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.CYLINDER,
        radius=20.0,
        height=60.0
    )
    
    assert isinstance(properties, CylinderProperties)
    assert properties.radius == 20.0
    assert properties.height == 60.0


def test_create_properties_for_type_cone():
    """Test creating ConeProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.CONE,
        radius=25.0,
        height=70.0
    )
    
    assert isinstance(properties, ConeProperties)
    assert properties.radius == 25.0
    assert properties.height == 70.0


def test_create_properties_for_type_torus():
    """Test creating TorusProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.TORUS,
        radius=40.0,
        length=15.0
    )
    
    assert isinstance(properties, TorusProperties)
    assert properties.radius == 40.0
    assert properties.length == 15.0


def test_properties_from_dict_box():
    """Test creating BoxProperties from dictionary."""
    data = {
        "width": 100.0,
        "height": 80.0,
        "depth": 60.0,
        "translation": {"x": 10.0, "y": 20.0, "z": 30.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
    }
    
    properties = GeometryManager.properties_from_dict(ShapeType.BOX, data)
    
    assert isinstance(properties, BoxProperties)
    assert properties.width == 100.0
    assert properties.height == 80.0
    assert properties.depth == 60.0
    assert properties.translation.x == 10.0
    assert properties.translation.y == 20.0
    assert properties.translation.z == 30.0


def test_properties_from_dict_sphere():
    """Test creating SphereProperties from dictionary."""
    data = {
        "radius": 35.0,
        "translation": {"x": 5.0, "y": 10.0, "z": 15.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
    }
    
    properties = GeometryManager.properties_from_dict(ShapeType.SPHERE, data)
    
    assert isinstance(properties, SphereProperties)
    assert properties.radius == 35.0
    assert properties.translation.x == 5.0


def test_properties_from_dict_cylinder():
    """Test creating CylinderProperties from dictionary."""
    data = {
        "radius": 18.0,
        "height": 55.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0}
    }
    
    properties = GeometryManager.properties_from_dict(ShapeType.CYLINDER, data)
    
    assert isinstance(properties, CylinderProperties)
    assert properties.radius == 18.0
    assert properties.height == 55.0


def test_multiple_signal_emissions(geometry_manager, app):
    """Test that multiple operations emit correct signals."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    
    # Spy on all signals
    created_spy = QSignalSpy(geometry_manager.shape_created)
    updated_spy = QSignalSpy(geometry_manager.shape_updated)
    removed_spy = QSignalSpy(geometry_manager.shape_removed)
    
    # Create shape
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    # Update shape
    new_properties = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape("box_1", new_properties)
    
    # Remove shape
    geometry_manager.remove_shape("box_1")
    
    app.processEvents()
    
    # Check signals
    assert created_spy.count() == 1
    assert updated_spy.count() == 1
    assert removed_spy.count() == 1


def test_managed_shape_structure(geometry_manager):
    """Test ManagedShape dataclass structure."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.5, 0.0),
        properties=properties
    )
    
    managed_shape = geometry_manager.get_shape("box_1")
    
    # Verify all fields
    assert hasattr(managed_shape, 'shape')
    assert hasattr(managed_shape, 'shape_type')
    assert hasattr(managed_shape, 'name')
    assert hasattr(managed_shape, 'color')
    assert hasattr(managed_shape, 'properties')
    # Transparency is now global only, not per-shape
    assert not hasattr(managed_shape, 'transparency')
    
    # Verify values
    assert managed_shape.shape_type == ShapeType.BOX
    assert managed_shape.name == "Test Box"
    assert managed_shape.color == (1.0, 0.5, 0.0)
    # Transparency is no longer a per-shape property
    assert isinstance(managed_shape.properties, BoxProperties)


def test_sequential_operations(geometry_manager):
    """Test sequential create, update, and query operations."""
    # Create first shape
    props1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    geometry_manager.create_shape(
        shape_id="box_1",
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=props1
    )
    
    # Create second shape
    props2 = SphereProperties(radius=25.0)
    geometry_manager.create_shape(
        shape_id="sphere_1",
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=props2
    )
    
    # Verify both exist
    assert len(geometry_manager.get_all_shape_ids()) == 2
    
    # Update first shape
    new_props = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape("box_1", new_props)
    
    # Verify first shape updated
    updated_shape = geometry_manager.get_shape("box_1")
    assert updated_shape.properties.width == 100.0
    
    # Remove second shape
    geometry_manager.remove_shape("sphere_1")
    
    # Verify only one remains
    assert len(geometry_manager.get_all_shape_ids()) == 1
    assert "box_1" in geometry_manager.get_all_shape_ids()
    assert "sphere_1" not in geometry_manager.get_all_shape_ids()
