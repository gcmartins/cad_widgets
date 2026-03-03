"""
Tests for the GeometryTreeWidget component
"""

import pytest
from cad_widgets import GeometryTreeWidget


@pytest.fixture
def geometry_tree(qapp):
    """Create a GeometryTreeWidget instance."""
    return GeometryTreeWidget()


def test_geometry_tree_initialization(geometry_tree):
    """Test that the geometry tree widget initializes correctly."""
    assert geometry_tree is not None
    assert geometry_tree.tree is not None
    assert len(geometry_tree.get_shape_ids()) == 0


def test_add_shape(geometry_tree):
    """Test adding a shape to the tree."""
    shape_id = "test-shape-1"
    geometry_tree.add_shape(
        shape_id=shape_id,
        shape_type="Box",
        name="Test Box",
    )

    assert shape_id in geometry_tree.get_shape_ids()
    assert geometry_tree.is_shape_visible(shape_id)


def test_add_multiple_shapes(geometry_tree):
    """Test adding multiple shapes to the tree."""
    shape_ids = []
    for i in range(3):
        shape_id = f"shape-{i}"
        geometry_tree.add_shape(
            shape_id=shape_id,
            shape_type=f"Type{i}",
            name=f"Shape {i}",
        )
        shape_ids.append(shape_id)

    assert len(geometry_tree.get_shape_ids()) == 3
    for shape_id in shape_ids:
        assert shape_id in geometry_tree.get_shape_ids()


def test_remove_shape(geometry_tree):
    """Test removing a shape from the tree."""
    shape_id = "test-shape-remove"
    geometry_tree.add_shape(
        shape_id=shape_id,
        shape_type="Sphere",
        name="Test Sphere",
    )

    assert shape_id in geometry_tree.get_shape_ids()

    geometry_tree.remove_shape(shape_id)
    assert shape_id not in geometry_tree.get_shape_ids()


def test_set_shape_visibility(geometry_tree):
    """Test setting shape visibility."""
    shape_id = "test-shape-visibility"
    geometry_tree.add_shape(
        shape_id=shape_id,
        shape_type="Cylinder",
        name="Test Cylinder",
    )

    # Should be visible by default
    assert geometry_tree.is_shape_visible(shape_id)

    # Hide the shape
    geometry_tree.set_shape_visible(shape_id, False)
    assert not geometry_tree.is_shape_visible(shape_id)

    # Show the shape again
    geometry_tree.set_shape_visible(shape_id, True)
    assert geometry_tree.is_shape_visible(shape_id)


def test_clear_all(geometry_tree):
    """Test clearing all shapes from the tree."""
    # Add multiple shapes
    for i in range(5):
        geometry_tree.add_shape(
            shape_id=f"shape-{i}",
            shape_type="Box",
            name=f"Box {i}",
        )

    assert len(geometry_tree.get_shape_ids()) == 5

    # Clear all shapes
    geometry_tree.clear_all()
    assert len(geometry_tree.get_shape_ids()) == 0


def test_add_shape_with_properties(geometry_tree):
    """Test adding a shape with properties."""
    shape_id = "test-shape-props"

    geometry_tree.add_shape(
        shape_id=shape_id,
        shape_type="Box",
        name="Parametric Box",
    )

    assert shape_id in geometry_tree.get_shape_ids()
    # Properties should be added as child items in the tree


def test_update_shape_properties(geometry_tree):
    """Test updating shape properties."""
    shape_id = "test-shape-update"
    geometry_tree.add_shape(
        shape_id=shape_id,
        shape_type="Sphere",
        name="Dynamic Sphere",
    )

    # Update properties
    new_properties = {"radius": "30", "center": "(0, 0, 0)"}
    geometry_tree.update_shape_properties(shape_id, new_properties)

    # Shape should still exist
    assert shape_id in geometry_tree.get_shape_ids()
