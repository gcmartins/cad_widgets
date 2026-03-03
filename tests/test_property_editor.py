"""
Tests for the PropertyEditorWidget component
"""

import pytest
from PySide6.QtTest import QSignalSpy
from cad_widgets import PropertyEditorWidget


@pytest.fixture
def property_editor(qapp):
    """Create a PropertyEditorWidget instance."""
    editor = PropertyEditorWidget()
    editor.show()  # Show widget so visibility checks work correctly
    return editor


def test_property_editor_initialization(property_editor):
    """Test that the property editor widget initializes correctly."""
    assert property_editor is not None
    assert property_editor.shape_info_label is not None
    assert property_editor.shape_info_label.text() == "No shape selected"
    assert not property_editor.size_group.isEnabled()
    assert not property_editor.translation_group.isEnabled()
    assert not property_editor.rotation_group.isEnabled()


def test_set_shape_box(property_editor):
    """Test setting a box shape for editing."""
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 10.0, "y": 20.0, "z": 30.0},
        "rotation": {"x": 0.0, "y": 90.0, "z": 0.0},
    }
    
    property_editor.set_shape("box_1", "Box", properties)
    
    assert property_editor._current_shape_id == "box_1"
    assert property_editor._current_shape_type == "Box"
    assert property_editor.shape_info_label.text() == "Editing: Box (box_1)"
    assert property_editor.size_group.isEnabled()
    assert property_editor.translation_group.isEnabled()
    assert property_editor.rotation_group.isEnabled()
    
    # Check size parameters for box
    assert property_editor.size_spinboxes["width"].value() == 50.0
    assert property_editor.size_spinboxes["height"].value() == 60.0
    assert property_editor.size_spinboxes["depth"].value() == 70.0
    assert property_editor.size_spinboxes["width"].isVisible()
    assert property_editor.size_spinboxes["height"].isVisible()
    assert property_editor.size_spinboxes["depth"].isVisible()
    assert not property_editor.size_spinboxes["radius"].isVisible()
    
    # Check translation
    assert property_editor.trans_x.value() == 10.0
    assert property_editor.trans_y.value() == 20.0
    assert property_editor.trans_z.value() == 30.0
    
    # Check rotation
    assert property_editor.rot_x.value() == 0.0
    assert property_editor.rot_y.value() == 90.0
    assert property_editor.rot_z.value() == 0.0


def test_set_shape_sphere(property_editor):
    """Test setting a sphere shape for editing."""
    properties = {
        "radius": 25.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    
    property_editor.set_shape("sphere_1", "Sphere", properties)
    
    assert property_editor._current_shape_id == "sphere_1"
    assert property_editor._current_shape_type == "Sphere"
    
    # Check size parameters for sphere
    assert property_editor.size_spinboxes["radius"].value() == 25.0
    assert property_editor.size_spinboxes["radius"].isVisible()
    assert not property_editor.size_spinboxes["width"].isVisible()
    assert not property_editor.size_spinboxes["height"].isVisible()
    assert not property_editor.size_spinboxes["depth"].isVisible()


def test_set_shape_cylinder(property_editor):
    """Test setting a cylinder shape for editing."""
    properties = {
        "radius": 15.0,
        "height": 50.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    
    property_editor.set_shape("cylinder_1", "Cylinder", properties)
    
    # Check size parameters for cylinder
    assert property_editor.size_spinboxes["radius"].value() == 15.0
    assert property_editor.size_spinboxes["height"].value() == 50.0
    assert property_editor.size_spinboxes["radius"].isVisible()
    assert property_editor.size_spinboxes["height"].isVisible()
    assert not property_editor.size_spinboxes["width"].isVisible()
    assert not property_editor.size_spinboxes["depth"].isVisible()


def test_clear_shape(property_editor):
    """Test clearing the current shape selection."""
    # First set a shape
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 10.0, "y": 20.0, "z": 30.0},
        "rotation": {"x": 0.0, "y": 90.0, "z": 0.0},
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    # Clear the shape
    property_editor.clear_shape()
    
    assert property_editor._current_shape_id is None
    assert property_editor._current_shape_type is None
    assert property_editor.shape_info_label.text() == "No shape selected"
    assert not property_editor.size_group.isEnabled()
    assert not property_editor.translation_group.isEnabled()
    assert not property_editor.rotation_group.isEnabled()


def test_get_current_properties_box(property_editor):
    """Test getting current properties for a box."""
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 10.0, "y": 20.0, "z": 30.0},
        "rotation": {"x": 0.0, "y": 90.0, "z": 0.0},
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    current_props = property_editor._get_current_properties()
    
    assert current_props["width"] == 50.0
    assert current_props["height"] == 60.0
    assert current_props["depth"] == 70.0
    assert current_props["translation"]["x"] == 10.0
    assert current_props["translation"]["y"] == 20.0
    assert current_props["translation"]["z"] == 30.0
    assert current_props["rotation"]["x"] == 0.0
    assert current_props["rotation"]["y"] == 90.0
    assert current_props["rotation"]["z"] == 0.0
    # Radius should not be in properties since it's hidden for box
    assert "radius" not in current_props


def test_get_current_properties_sphere(property_editor):
    """Test getting current properties for a sphere."""
    properties = {
        "radius": 25.0,
        "translation": {"x": 5.0, "y": 10.0, "z": 15.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("sphere_1", "Sphere", properties)
    
    current_props = property_editor._get_current_properties()
    
    assert current_props["radius"] == 25.0
    assert current_props["translation"]["x"] == 5.0
    assert current_props["translation"]["y"] == 10.0
    assert current_props["translation"]["z"] == 15.0
    # Width, height, depth should not be in properties since they're hidden for sphere
    assert "width" not in current_props
    assert "height" not in current_props
    assert "depth" not in current_props


def test_signal_emission_on_value_change(property_editor, qapp):
    """Test that properties_changed signal is emitted when values change."""
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    # Create signal spy
    spy = QSignalSpy(property_editor.properties_changed)
    
    # Change a value and trigger editingFinished (simulates pressing Enter)
    property_editor.size_spinboxes["width"].setValue(100.0)
    property_editor.size_spinboxes["width"].editingFinished.emit()
    qapp.processEvents()  # Process pending signals
    
    # Check signal was emitted
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[0] == "box_1"  # shape_id
    assert isinstance(signal_args[1], dict)  # properties dict
    assert signal_args[1]["width"] == 100.0


def test_signal_not_emitted_during_loading(property_editor):
    """Test that properties_changed signal is NOT emitted during initial loading."""
    # Create signal spy before setting shape
    spy = QSignalSpy(property_editor.properties_changed)
    
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 10.0, "y": 20.0, "z": 30.0},
        "rotation": {"x": 0.0, "y": 90.0, "z": 0.0},
    }
    
    # Set shape (which loads properties)
    property_editor.set_shape("box_1", "Box", properties)
    
    # No signal should have been emitted during loading
    assert spy.count() == 0


def test_translation_value_changes(property_editor, qapp):
    """Test changing translation values."""
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    spy = QSignalSpy(property_editor.properties_changed)
    
    # Change translation X and trigger editingFinished
    property_editor.trans_x.setValue(50.0)
    property_editor.trans_x.editingFinished.emit()
    qapp.processEvents()  # Process pending signals
    
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[1]["translation"]["x"] == 50.0


def test_rotation_value_changes(property_editor, qapp):
    """Test changing rotation values."""
    properties = {
        "radius": 25.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("sphere_1", "Sphere", properties)
    
    spy = QSignalSpy(property_editor.properties_changed)
    
    # Change rotation Y and trigger editingFinished
    property_editor.rot_y.setValue(45.0)
    property_editor.rot_y.editingFinished.emit()
    qapp.processEvents()  # Process pending signals
    
    assert spy.count() == 1
    signal_args = spy.at(0)
    assert signal_args[1]["rotation"]["y"] == 45.0


def test_multiple_value_changes(property_editor, qapp):
    """Test multiple value changes emit multiple signals."""
    properties = {
        "width": 50.0,
        "height": 60.0,
        "depth": 70.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    spy = QSignalSpy(property_editor.properties_changed)
    
    # Change multiple values and trigger editingFinished for each
    property_editor.size_spinboxes["width"].setValue(100.0)
    property_editor.size_spinboxes["width"].editingFinished.emit()
    
    property_editor.size_spinboxes["height"].setValue(120.0)
    property_editor.size_spinboxes["height"].editingFinished.emit()
    
    property_editor.trans_x.setValue(10.0)
    property_editor.trans_x.editingFinished.emit()
    
    qapp.processEvents()  # Process pending signals
    
    # Should have emitted 3 signals
    assert spy.count() == 3


def test_shape_type_visibility_torus(property_editor):
    """Test that torus shows correct parameters."""
    properties = {
        "radius": 25.0,
        "length": 10.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("torus_1", "Torus", properties)
    
    # Check size parameters for torus
    assert property_editor.size_spinboxes["radius"].isVisible()
    assert property_editor.size_spinboxes["length"].isVisible()
    assert not property_editor.size_spinboxes["width"].isVisible()
    assert not property_editor.size_spinboxes["height"].isVisible()
    assert not property_editor.size_spinboxes["depth"].isVisible()


def test_shape_type_visibility_cone(property_editor):
    """Test that cone shows correct parameters."""
    properties = {
        "radius": 30.0,
        "height": 70.0,
        "translation": {"x": 0.0, "y": 0.0, "z": 0.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
    }
    property_editor.set_shape("cone_1", "Cone", properties)
    
    # Check size parameters for cone
    assert property_editor.size_spinboxes["radius"].isVisible()
    assert property_editor.size_spinboxes["height"].isVisible()
    assert not property_editor.size_spinboxes["width"].isVisible()
    assert not property_editor.size_spinboxes["depth"].isVisible()
    assert not property_editor.size_spinboxes["length"].isVisible()


def test_default_property_values(property_editor):
    """Test setting shape without providing all properties."""
    # Set properties with missing values
    properties = {
        "width": 50.0,
        # height and depth missing
    }
    property_editor.set_shape("box_1", "Box", properties)
    
    # Should have defaults for missing values
    assert property_editor.size_spinboxes["width"].value() == 50.0
    assert property_editor.size_spinboxes["height"].value() == 1.0  # default
    assert property_editor.size_spinboxes["depth"].value() == 1.0  # default
    assert property_editor.trans_x.value() == 0.0
    assert property_editor.trans_y.value() == 0.0
    assert property_editor.trans_z.value() == 0.0


def test_spinbox_ranges(property_editor):
    """Test that spinboxes have correct ranges."""
    # Size spinboxes should allow positive values
    for spinbox in property_editor.size_spinboxes.values():
        assert spinbox.minimum() == 0.01
        assert spinbox.maximum() == 10000.0
    
    # Translation spinboxes should allow negative values
    assert property_editor.trans_x.minimum() == -10000.0
    assert property_editor.trans_x.maximum() == 10000.0
    
    # Rotation spinboxes should be -360 to 360
    assert property_editor.rot_x.minimum() == -360.0
    assert property_editor.rot_x.maximum() == 360.0
