"""
Tests for GeometryManager
"""

import pytest
from PySide6.QtTest import QSignalSpy

from cad_widgets.managers.geometry_manager import GeometryManager, ManagedShape
from cad_widgets.enums import ShapeType
from cad_widgets.models.shape_properties import (
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
    RectangleProperties,
    CircleProperties,
    FaceProperties,
    Translation,
    Rotation,
)


@pytest.fixture
def geometry_manager():
    """Create a fresh GeometryManager for each test."""
    return GeometryManager()


def test_geometry_manager_initialization(geometry_manager):
    """Test that GeometryManager initializes correctly."""
    assert geometry_manager is not None
    assert len(geometry_manager.get_all_shape_ids()) == 0


def test_create_box_shape(geometry_manager, qapp):
    """Test creating a box shape."""
    properties = BoxProperties(
        width=100.0,
        height=60.0,
        depth=40.0,
        translation=Translation(x=10.0, y=20.0, z=30.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    spy = QSignalSpy(geometry_manager.shape_created)
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    qapp.processEvents()
    
    # Check shape was created
    assert managed_shape is not None
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == managed_shape.shape_id
    assert isinstance(signal_args[1], ManagedShape)
    
    # Check managed shape
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape.shape_type == ShapeType.BOX
    assert retrieved_shape.name == "Test Box"
    assert retrieved_shape.color == (1.0, 0.0, 0.0)
    # Transparency is now global only, not per-shape
    assert retrieved_shape.properties == properties


def test_create_sphere_shape(geometry_manager, qapp):
    """Test creating a sphere shape."""
    properties = SphereProperties(
        radius=25.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Test Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape.shape_type == ShapeType.SPHERE
    assert isinstance(retrieved_shape.properties, SphereProperties)
    assert retrieved_shape.properties.radius == 25.0


def test_create_cylinder_shape(geometry_manager, qapp):
    """Test creating a cylinder shape."""
    properties = CylinderProperties(
        radius=15.0,
        height=50.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CYLINDER,
        name="Test Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape.shape_type == ShapeType.CYLINDER
    assert isinstance(retrieved_shape.properties, CylinderProperties)


def test_create_cone_shape(geometry_manager, qapp):
    """Test creating a cone shape."""
    properties = ConeProperties(
        base_radius=20.0,
        top_radius=8.0,
        height=40.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CONE,
        name="Test Cone",
        color=(1.0, 1.0, 0.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape.shape_type == ShapeType.CONE
    assert isinstance(retrieved_shape.properties, ConeProperties)


def test_create_torus_shape(geometry_manager, qapp):
    """Test creating a torus shape."""
    properties = TorusProperties(
        major_radius=30.0,
        minor_radius=10.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0)
    )
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.TORUS,
        name="Test Torus",
        color=(1.0, 0.0, 1.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape is not None
    assert retrieved_shape.shape_type == ShapeType.TORUS
    assert isinstance(retrieved_shape.properties, TorusProperties)


def test_create_rectangle_shape(geometry_manager, qapp):
    """Test creating a rectangle surface shape."""
    properties = RectangleProperties(
        width=80.0,
        height=50.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0),
    )

    spy = QSignalSpy(geometry_manager.shape_created)

    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.RECTANGLE,
        name="Test Rectangle",
        color=(0.2, 0.8, 0.8),
        properties=properties,
    )

    qapp.processEvents()

    assert managed_shape is not None
    assert spy.count() == 1

    retrieved = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved is not None
    assert retrieved.shape_type == ShapeType.RECTANGLE
    assert retrieved.name == "Test Rectangle"
    assert retrieved.color == (0.2, 0.8, 0.8)
    assert isinstance(retrieved.properties, RectangleProperties)
    assert retrieved.properties.width == 80.0
    assert retrieved.properties.height == 50.0


def test_create_circle_shape(geometry_manager, qapp):
    """Test creating a circle surface shape."""
    properties = CircleProperties(
        radius=35.0,
        translation=Translation(x=0.0, y=0.0, z=0.0),
        rotation=Rotation(x=0.0, y=0.0, z=0.0),
    )

    spy = QSignalSpy(geometry_manager.shape_created)

    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CIRCLE,
        name="Test Circle",
        color=(0.9, 0.5, 0.1),
        properties=properties,
    )

    qapp.processEvents()

    assert managed_shape is not None
    assert spy.count() == 1

    retrieved = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved is not None
    assert retrieved.shape_type == ShapeType.CIRCLE
    assert retrieved.name == "Test Circle"
    assert isinstance(retrieved.properties, CircleProperties)
    assert retrieved.properties.radius == 35.0


def test_update_rectangle_shape(geometry_manager, qapp):
    """Test updating a rectangle surface shape's dimensions."""
    properties = RectangleProperties(width=60.0, height=40.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.RECTANGLE,
        name="Rectangle",
        color=(0.2, 0.8, 0.8),
        properties=properties,
    )
    shape_id = managed_shape.shape_id

    spy = QSignalSpy(geometry_manager.shape_updated)
    new_properties = RectangleProperties(width=120.0, height=90.0)
    updated = geometry_manager.update_shape(shape_id, new_properties)

    qapp.processEvents()

    assert updated is not None
    assert spy.count() == 1
    retrieved = geometry_manager.get_shape(shape_id)
    assert retrieved.properties.width == 120.0
    assert retrieved.properties.height == 90.0


def test_update_circle_shape(geometry_manager, qapp):
    """Test updating a circle surface shape's radius."""
    properties = CircleProperties(radius=30.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CIRCLE,
        name="Circle",
        color=(0.9, 0.5, 0.1),
        properties=properties,
    )
    shape_id = managed_shape.shape_id

    spy = QSignalSpy(geometry_manager.shape_updated)
    new_properties = CircleProperties(radius=55.0)
    updated = geometry_manager.update_shape(shape_id, new_properties)

    qapp.processEvents()

    assert updated is not None
    assert spy.count() == 1
    retrieved = geometry_manager.get_shape(shape_id)
    assert retrieved.properties.radius == 55.0


def test_rectangle_with_translation(geometry_manager):
    """Test creating a rectangle with a translation offset."""
    properties = RectangleProperties(
        width=80.0,
        height=50.0,
        translation=Translation(x=10.0, y=20.0, z=5.0),
    )
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.RECTANGLE,
        name="Translated Rectangle",
        color=(0.2, 0.8, 0.8),
        properties=properties,
    )

    assert managed_shape is not None
    retrieved = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved.properties.translation.x == 10.0
    assert retrieved.properties.translation.y == 20.0
    assert retrieved.properties.translation.z == 5.0


def test_circle_with_rotation(geometry_manager):
    """Test creating a circle with a rotation applied."""
    properties = CircleProperties(
        radius=35.0,
        rotation=Rotation(x=90.0, y=0.0, z=0.0),
    )
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CIRCLE,
        name="Rotated Circle",
        color=(0.9, 0.5, 0.1),
        properties=properties,
    )

    assert managed_shape is not None
    retrieved = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved.properties.rotation.x == 90.0


def test_create_properties_for_type_rectangle():
    """Test factory method for RectangleProperties."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.RECTANGLE,
        width=100.0,
        height=60.0,
    )

    assert isinstance(properties, RectangleProperties)
    assert properties.width == 100.0
    assert properties.height == 60.0


def test_create_properties_for_type_circle():
    """Test factory method for CircleProperties."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.CIRCLE,
        radius=45.0,
    )

    assert isinstance(properties, CircleProperties)
    assert properties.radius == 45.0


def test_properties_from_dict_rectangle():
    """Test creating RectangleProperties from a dictionary."""
    data = {
        "width": 80.0,
        "height": 50.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }

    properties = GeometryManager.properties_from_dict(ShapeType.RECTANGLE, data)

    assert isinstance(properties, RectangleProperties)
    assert properties.width == 80.0
    assert properties.height == 50.0


def test_properties_from_dict_circle():
    """Test creating CircleProperties from a dictionary."""
    data = {
        "radius": 35.0,
        "translation": {"x": 5.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }

    properties = GeometryManager.properties_from_dict(ShapeType.CIRCLE, data)

    assert isinstance(properties, CircleProperties)
    assert properties.radius == 35.0
    assert properties.translation.x == 5.0


def test_surface_shapes_type_mismatch_returns_none(geometry_manager):
    """Test that a type/properties mismatch returns None without raising."""
    result = geometry_manager.create_shape(
        shape_type=ShapeType.RECTANGLE,
        properties=BoxProperties(width=10.0, height=10.0, depth=10.0),
    )
    assert result is None


def test_update_shape(geometry_manager, qapp):
    """Test updating a shape with new properties."""
    # Create initial shape
    initial_properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=initial_properties
    )
    shape_id = managed_shape.shape_id
    
    spy = QSignalSpy(geometry_manager.shape_updated)
    
    # Update with new properties
    new_properties = BoxProperties(width=100.0, height=80.0, depth=60.0)
    updated_shape = geometry_manager.update_shape(shape_id, new_properties)
    
    qapp.processEvents()
    
    # Check shape was updated
    assert updated_shape is not None
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == shape_id
    assert isinstance(signal_args[1], ManagedShape)
    
    # Check updated properties
    retrieved_shape = geometry_manager.get_shape(shape_id)
    assert retrieved_shape.properties.width == 100.0
    assert retrieved_shape.properties.height == 80.0
    assert retrieved_shape.properties.depth == 60.0


def test_update_nonexistent_shape(geometry_manager):
    """Test updating a shape that doesn't exist."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    result = geometry_manager.update_shape("nonexistent", properties)
    
    assert result is None


def test_remove_shape(geometry_manager, qapp):
    """Test removing a shape."""
    # Create shape
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    shape_id = managed_shape.shape_id
    
    spy = QSignalSpy(geometry_manager.shape_removed)
    
    # Remove shape
    result = geometry_manager.remove_shape(shape_id)
    
    qapp.processEvents()
    
    # Check removal was successful
    assert result is True
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == shape_id
    
    # Check shape is gone
    assert geometry_manager.get_shape(shape_id) is None


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
    
    shape1 = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=properties1
    )
    
    shape2 = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=properties2
    )
    
    shape3 = geometry_manager.create_shape(
        shape_type=ShapeType.CYLINDER,
        name="Cylinder 1",
        color=(0.0, 0.0, 1.0),
        properties=properties3
    )
    
    shape_ids = geometry_manager.get_all_shape_ids()
    
    assert len(shape_ids) == 3
    assert shape1.shape_id in shape_ids
    assert shape2.shape_id in shape_ids
    assert shape3.shape_id in shape_ids


def test_clear_all(geometry_manager, qapp):
    """Test clearing all shapes."""
    # Create multiple shapes
    properties1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    properties2 = SphereProperties(radius=25.0)
    
    geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=properties1
    )
    
    geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=properties2
    )
    
    spy = QSignalSpy(geometry_manager.all_cleared)
    
    # Clear all
    geometry_manager.clear_all()
    
    qapp.processEvents()
    
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
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Translated Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape.properties.translation.x == 100.0
    assert retrieved_shape.properties.translation.y == 50.0
    assert retrieved_shape.properties.translation.z == 25.0


def test_shape_with_rotation(geometry_manager):
    """Test creating a shape with rotation."""
    properties = CylinderProperties(
        radius=15.0,
        height=50.0,
        rotation=Rotation(x=45.0, y=30.0, z=15.0)
    )
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.CYLINDER,
        name="Rotated Cylinder",
        color=(0.0, 0.0, 1.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved_shape.properties.rotation.x == 45.0
    assert retrieved_shape.properties.rotation.y == 30.0
    assert retrieved_shape.properties.rotation.z == 15.0


def test_shape_with_transparency(geometry_manager):
    """Test creating a shape - transparency is now global only."""
    properties = SphereProperties(radius=25.0)
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Transparent Sphere",
        color=(0.0, 1.0, 0.0),
        properties=properties
    )
    
    assert managed_shape is not None
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    # Transparency is no longer a per-shape property
    assert not hasattr(retrieved_shape, 'transparency')


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
        base_radius=25.0,
        top_radius=10.0,
        height=70.0
    )
    
    assert isinstance(properties, ConeProperties)
    assert properties.base_radius == 25.0
    assert properties.top_radius == 10.0
    assert properties.height == 70.0


def test_create_properties_for_type_torus():
    """Test creating TorusProperties using factory method."""
    properties = GeometryManager.create_properties_for_type(
        ShapeType.TORUS,
        major_radius=40.0,
        minor_radius=15.0
    )
    
    assert isinstance(properties, TorusProperties)
    assert properties.major_radius == 40.0
    assert properties.minor_radius == 15.0


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


def test_multiple_signal_emissions(geometry_manager, qapp):
    """Test that multiple operations emit correct signals."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    
    # Spy on all signals
    created_spy = QSignalSpy(geometry_manager.shape_created)
    updated_spy = QSignalSpy(geometry_manager.shape_updated)
    removed_spy = QSignalSpy(geometry_manager.shape_removed)
    
    # Create shape
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    shape_id = managed_shape.shape_id
    
    # Update shape
    new_properties = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape(shape_id, new_properties)
    
    # Remove shape
    geometry_manager.remove_shape(shape_id)
    
    qapp.processEvents()
    
    # Check signals
    assert created_spy.count() == 1
    assert updated_spy.count() == 1
    assert removed_spy.count() == 1


def test_managed_shape_structure(geometry_manager):
    """Test ManagedShape dataclass structure."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.5, 0.0),
        properties=properties
    )
    
    retrieved_shape = geometry_manager.get_shape(managed_shape.shape_id)
    
    # Verify all fields
    assert hasattr(retrieved_shape, 'shape')
    assert hasattr(retrieved_shape, 'shape_type')
    assert hasattr(retrieved_shape, 'name')
    assert hasattr(retrieved_shape, 'color')
    assert hasattr(retrieved_shape, 'properties')
    # Transparency is now global only, not per-shape
    assert not hasattr(retrieved_shape, 'transparency')
    
    # Verify values
    assert retrieved_shape.shape_type == ShapeType.BOX
    assert retrieved_shape.name == "Test Box"
    assert retrieved_shape.color == (1.0, 0.5, 0.0)
    # Transparency is no longer a per-shape property
    assert isinstance(retrieved_shape.properties, BoxProperties)


def test_update_shape_color(geometry_manager, qapp):
    """Test updating a shape's color."""
    properties = BoxProperties(width=50.0, height=50.0, depth=50.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    shape_id = managed_shape.shape_id

    spy = QSignalSpy(geometry_manager.shape_updated)

    result = geometry_manager.update_shape_color(shape_id, (0.0, 0.5, 1.0))

    qapp.processEvents()

    assert result is True
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == shape_id
    assert isinstance(signal_args[1], ManagedShape)

    retrieved = geometry_manager.get_shape(shape_id)
    assert retrieved.color == (0.0, 0.5, 1.0)


def test_update_shape_color_nonexistent(geometry_manager):
    """Test updating color of a shape that doesn't exist returns False."""
    result = geometry_manager.update_shape_color("nonexistent", (1.0, 0.0, 0.0))
    assert result is False


def test_update_shape_color_does_not_affect_properties(geometry_manager):
    """Test that updating color does not alter the shape's geometry properties."""
    properties = BoxProperties(width=50.0, height=30.0, depth=20.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Test Box",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )

    geometry_manager.update_shape_color(managed_shape.shape_id, (0.0, 1.0, 0.0))

    retrieved = geometry_manager.get_shape(managed_shape.shape_id)
    assert retrieved.properties.width == 50.0
    assert retrieved.properties.height == 30.0
    assert retrieved.properties.depth == 20.0


def test_update_shape_color_multiple_times(geometry_manager, qapp):
    """Test updating color multiple times emits a signal each time."""
    properties = SphereProperties(radius=25.0)
    managed_shape = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Test Sphere",
        color=(1.0, 0.0, 0.0),
        properties=properties
    )
    shape_id = managed_shape.shape_id

    spy = QSignalSpy(geometry_manager.shape_updated)

    geometry_manager.update_shape_color(shape_id, (0.0, 1.0, 0.0))
    geometry_manager.update_shape_color(shape_id, (0.0, 0.0, 1.0))

    qapp.processEvents()

    assert spy.count() == 2
    assert geometry_manager.get_shape(shape_id).color == (0.0, 0.0, 1.0)


def test_update_shape_color_on_union_component_does_not_emit_signal(geometry_manager, qapp):
    """Regression test: updating the color of an internal union component must not
    emit shape_updated (which would cause the component to be displayed as a
    standalone shape in the viewer)."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Box",
        color=(1.0, 0.0, 0.0),
        properties=BoxProperties(width=10.0, height=10.0, depth=10.0),
    )
    sphere = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Sphere",
        color=(0.0, 1.0, 0.0),
        properties=SphereProperties(radius=5.0),
    )

    union_id = geometry_manager.union_shapes([box.shape_id, sphere.shape_id])
    assert union_id is not None

    component_id = box.shape_id
    assert geometry_manager.get_shape(component_id).parent_id == union_id

    spy = QSignalSpy(geometry_manager.shape_updated)

    result = geometry_manager.update_shape_color(component_id, (0.0, 0.0, 1.0))

    qapp.processEvents()

    assert result is True
    assert spy.count() == 0, "shape_updated must not fire for internal union components"
    assert geometry_manager.get_shape(component_id).color == (0.0, 0.0, 1.0)


def test_sequential_operations(geometry_manager):
    """Test sequential create, update, and query operations."""
    # Create first shape
    props1 = BoxProperties(width=50.0, height=50.0, depth=50.0)
    shape1 = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="Box 1",
        color=(1.0, 0.0, 0.0),
        properties=props1
    )

    # Create second shape
    props2 = SphereProperties(radius=25.0)
    shape2 = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        name="Sphere 1",
        color=(0.0, 1.0, 0.0),
        properties=props2
    )

    # Verify both exist
    assert len(geometry_manager.get_all_shape_ids()) == 2

    # Update first shape
    new_props = BoxProperties(width=100.0, height=100.0, depth=100.0)
    geometry_manager.update_shape(shape1.shape_id, new_props)

    # Verify first shape updated
    updated_shape = geometry_manager.get_shape(shape1.shape_id)
    assert updated_shape.properties.width == 100.0

    # Remove second shape
    geometry_manager.remove_shape(shape2.shape_id)

    # Verify only one remains
    assert len(geometry_manager.get_all_shape_ids()) == 1
    assert shape1.shape_id in geometry_manager.get_all_shape_ids()
    assert shape2.shape_id not in geometry_manager.get_all_shape_ids()


# --- split_to_faces tests ---

def test_split_box_to_faces(geometry_manager):
    """Box should split into 6 faces."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        properties=BoxProperties(width=50.0, height=50.0, depth=50.0),
    )
    face_ids = geometry_manager.split_to_faces(box.shape_id)
    assert len(face_ids) == 6
    for fid in face_ids:
        face = geometry_manager.get_shape(fid)
        assert face is not None
        assert face.shape_type == ShapeType.FACE
        assert face.parent_id is None


def test_split_sphere_to_faces(geometry_manager):
    """Sphere should split into at least one face."""
    sphere = geometry_manager.create_shape(
        shape_type=ShapeType.SPHERE,
        properties=SphereProperties(radius=30.0),
    )
    face_ids = geometry_manager.split_to_faces(sphere.shape_id)
    assert len(face_ids) >= 1
    for fid in face_ids:
        assert geometry_manager.get_shape(fid).shape_type == ShapeType.FACE


def test_split_cylinder_to_faces(geometry_manager):
    """Cylinder should split into 3 faces (top cap, bottom cap, lateral)."""
    cyl = geometry_manager.create_shape(
        shape_type=ShapeType.CYLINDER,
        properties=CylinderProperties(radius=20.0, height=60.0),
    )
    face_ids = geometry_manager.split_to_faces(cyl.shape_id)
    assert len(face_ids) == 3


def test_split_face_names_convention(geometry_manager):
    """Face names should follow <parent_name>_Face_<n> pattern."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        name="MyBox",
        properties=BoxProperties(),
    )
    face_ids = geometry_manager.split_to_faces(box.shape_id)
    names = [geometry_manager.get_shape(fid).name for fid in face_ids]
    for i, name in enumerate(names, start=1):
        assert name == f"MyBox_Face_{i}"


def test_split_face_inherits_color(geometry_manager):
    """All produced faces should inherit the parent's color."""
    color = (1.0, 0.5, 0.0)
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        color=color,
        properties=BoxProperties(),
    )
    face_ids = geometry_manager.split_to_faces(box.shape_id)
    for fid in face_ids:
        assert geometry_manager.get_shape(fid).color == color


def test_split_removes_original(geometry_manager):
    """Original solid should be removed after split."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        properties=BoxProperties(),
    )
    original_id = box.shape_id
    geometry_manager.split_to_faces(original_id)
    assert geometry_manager.get_shape(original_id) is None


def test_split_emits_shape_removed(geometry_manager, qapp):
    """shape_removed should fire once with the original shape_id."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        properties=BoxProperties(),
    )
    spy = QSignalSpy(geometry_manager.shape_removed)
    geometry_manager.split_to_faces(box.shape_id)
    qapp.processEvents()
    assert spy.count() == 1
    assert spy.at(0)[0] == box.shape_id


def test_split_emits_shape_created_per_face(geometry_manager, qapp):
    """shape_created should fire once per extracted face."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        properties=BoxProperties(),
    )
    spy = QSignalSpy(geometry_manager.shape_created)
    face_ids = geometry_manager.split_to_faces(box.shape_id)
    qapp.processEvents()
    assert spy.count() == len(face_ids)


def test_split_nonexistent_returns_empty(geometry_manager):
    """split_to_faces on a bad ID should return an empty list."""
    assert geometry_manager.split_to_faces("nonexistent_id") == []


def test_split_surface_shape_returns_empty(geometry_manager):
    """Calling split_to_faces on a surface shape should return empty list."""
    rect = geometry_manager.create_shape(
        shape_type=ShapeType.RECTANGLE,
        properties=RectangleProperties(width=60.0, height=40.0),
    )
    assert geometry_manager.split_to_faces(rect.shape_id) == []


def test_split_component_returns_empty(geometry_manager):
    """Calling split_to_faces on a boolean component should return empty list."""
    box1 = geometry_manager.create_shape(
        shape_type=ShapeType.BOX, properties=BoxProperties()
    )
    box2 = geometry_manager.create_shape(
        shape_type=ShapeType.BOX, properties=BoxProperties()
    )
    geometry_manager.union_shapes([box1.shape_id, box2.shape_id])
    # The original boxes are now components with parent_id set
    component = geometry_manager.get_shape(box1.shape_id)
    assert component.parent_id is not None
    assert geometry_manager.split_to_faces(box1.shape_id) == []


def test_split_face_properties_type(geometry_manager):
    """Each produced face should have FaceProperties."""
    box = geometry_manager.create_shape(
        shape_type=ShapeType.BOX,
        properties=BoxProperties(),
    )
    face_ids = geometry_manager.split_to_faces(box.shape_id)
    for fid in face_ids:
        assert isinstance(geometry_manager.get_shape(fid).properties, FaceProperties)
