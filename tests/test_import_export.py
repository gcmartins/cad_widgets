"""
Tests for STEP and IGES import/export functionality
"""

import tempfile
import os
from cad_widgets import GeometryService, GeometryManager, ShapeType, ImportedProperties


def test_export_import_step():
    """Test exporting and importing a STEP file."""
    geo = GeometryService()
    
    # Create a box
    box = geo.create_box(100, 50, 75)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.step', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Export to STEP
        success = geo.export_step(box, tmp_path)
        assert success, "STEP export should succeed"
        assert os.path.exists(tmp_path), "STEP file should exist"
        
        # Import from STEP
        imported_shape = geo.import_file(tmp_path)
        assert imported_shape is not None, "STEP import should succeed"
        assert not imported_shape.IsNull(), "Imported shape should not be null"
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_export_import_iges():
    """Test exporting and importing an IGES file."""
    geo = GeometryService()
    
    # Create a sphere
    sphere = geo.create_sphere(50)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.iges', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Export to IGES
        success = geo.export_iges(sphere, tmp_path)
        assert success, "IGES export should succeed"
        assert os.path.exists(tmp_path), "IGES file should exist"
        
        # Import from IGES
        imported_shape = geo.import_file(tmp_path)
        assert imported_shape is not None, "IGES import should succeed"
        assert not imported_shape.IsNull(), "Imported shape should not be null"
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_export_step_complex_shape():
    """Test exporting a complex shape to STEP."""
    geo = GeometryService()
    
    # Create a complex shape with boolean operations
    box = geo.create_box(100, 100, 100)
    sphere = geo.create_sphere(60, center=(50, 50, 50))
    result = geo.cut_shapes(box, sphere)
    
    assert result is not None, "Boolean operation should succeed"
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.step', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Export to STEP
        success = geo.export_step(result, tmp_path)
        assert success, "STEP export of complex shape should succeed"
        assert os.path.exists(tmp_path), "STEP file should exist"
        
        # Import and verify
        imported_shape = geo.import_file(tmp_path)
        assert imported_shape is not None, "STEP import should succeed"
        assert not imported_shape.IsNull(), "Imported shape should not be null"
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_import_nonexistent_step():
    """Test importing from a non-existent file."""
    geo = GeometryService()
    
    result = geo.import_file("nonexistent_file.step")
    assert result is None, "Import from non-existent file should return None"


def test_import_nonexistent_iges():
    """Test importing from a non-existent file."""
    geo = GeometryService()
    
    result = geo.import_file("nonexistent_file.iges")
    assert result is None, "Import from non-existent file should return None"


def test_geometry_manager_import_shape():
    """Test importing a shape through GeometryManager."""
    manager = GeometryManager()
    geo = GeometryService()
    
    # Create a shape and export it to a temporary file
    box = geo.create_box(100, 50, 75)
    
    # Create a temporary file for the test
    with tempfile.NamedTemporaryFile(suffix='.step', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Export the box to STEP file
        success = geo.export_step(box, tmp_path)
        assert success, "Export should succeed"
        
        # Import it through the manager (name will be auto-generated as "IMPORTED_1")
        managed_shape = manager.import_shape(
            filename=tmp_path,
            color=(0.6, 0.6, 0.7)
        )
        
        assert managed_shape is not None, "Imported shape should be created"
        assert managed_shape.shape_type == ShapeType.IMPORTED, "Shape type should be IMPORTED"
        assert managed_shape.name == "Imported_1", "Shape name should be auto-generated"
        assert isinstance(managed_shape.properties, ImportedProperties), "Properties should be ImportedProperties"
        
        # Verify shape is in manager
        retrieved = manager.get_shape(managed_shape.shape_id)
        assert retrieved is not None, "Shape should be retrievable"
        assert retrieved.shape_type == ShapeType.IMPORTED, "Retrieved shape type should be IMPORTED"
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_imported_shape_transformation_update():
    """Test that translation and rotation updates work on imported shapes."""
    from cad_widgets.models.shape_properties import Translation, Rotation
    
    manager = GeometryManager()
    geo = GeometryService()
    
    # Create a shape and export it to a temporary file
    cylinder = geo.create_cylinder(20, 100)
    
    # Create a temporary file for the test
    with tempfile.NamedTemporaryFile(suffix='.step', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Export the cylinder to STEP file
        success = geo.export_step(cylinder, tmp_path)
        assert success, "Export should succeed"
        
        # Import it through the manager
        managed_shape = manager.import_shape(
            filename=tmp_path,
            color=(0.5, 0.5, 0.8)
        )
    
        # Initial properties should be zero
        assert managed_shape.properties.translation.x == 0.0
        assert managed_shape.properties.translation.y == 0.0
        assert managed_shape.properties.translation.z == 0.0
        assert managed_shape.properties.rotation.x == 0.0
        assert managed_shape.properties.rotation.y == 0.0
        assert managed_shape.properties.rotation.z == 0.0
        
        # Update with translation and rotation
        new_props = ImportedProperties(
            translation=Translation(x=50.0, y=100.0, z=150.0),
            rotation=Rotation(x=45.0, y=90.0, z=180.0)
        )
        
        updated_shape = manager.update_shape(managed_shape.shape_id, new_props)
        
        # Verify shape was updated
        assert updated_shape is not None, "Update should return a shape"
        
        # Verify properties were updated
        retrieved = manager.get_shape(managed_shape.shape_id)
        assert retrieved is not None
        assert retrieved.properties.translation.x == 50.0
        assert retrieved.properties.translation.y == 100.0
        assert retrieved.properties.translation.z == 150.0
        assert retrieved.properties.rotation.x == 45.0
        assert retrieved.properties.rotation.y == 90.0
        assert retrieved.properties.rotation.z == 180.0
        
        # Update again with different values
        new_props2 = ImportedProperties(
            translation=Translation(x=20.0, y=30.0, z=40.0),
            rotation=Rotation(x=15.0, y=30.0, z=45.0)
        )
        
        updated_shape2 = manager.update_shape(managed_shape.shape_id, new_props2)
        assert updated_shape2 is not None, "Second update should also work"
        
        retrieved2 = manager.get_shape(managed_shape.shape_id)
        assert retrieved2 is not None
        assert retrieved2.properties.translation.x == 20.0
        assert retrieved2.properties.translation.y == 30.0
        assert retrieved2.properties.translation.z == 40.0
        assert retrieved2.properties.rotation.x == 15.0
        assert retrieved2.properties.rotation.y == 30.0
        assert retrieved2.properties.rotation.z == 45.0
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


