"""
Tests for shape creation utilities
"""

from cad_widgets import GeometryService


def test_create_box_basic():
    """Test basic box creation."""
    geo = GeometryService()
    box = geo.create_box(100, 50, 75)
    assert box is not None


def test_create_box_with_position():
    """Test box creation with custom position."""
    geo = GeometryService()
    box = geo.create_box(100, 50, 75, position=(10, 20, 30))
    assert box is not None


def test_create_sphere_basic():
    """Test basic sphere creation."""
    geo = GeometryService()
    sphere = geo.create_sphere(50)
    assert sphere is not None


def test_create_sphere_with_center():
    """Test sphere creation with custom center."""
    geo = GeometryService()
    sphere = geo.create_sphere(50, center=(10, 20, 30))
    assert sphere is not None


def test_create_cylinder_basic():
    """Test basic cylinder creation."""
    geo = GeometryService()
    cylinder = geo.create_cylinder(25, 100)
    assert cylinder is not None


def test_create_cylinder_with_axis():
    """Test cylinder creation with custom axis."""
    geo = GeometryService()
    cylinder = geo.create_cylinder(25, 100, position=(0, 0, 0), direction=(1, 0, 0))
    assert cylinder is not None


def test_create_cone_basic():
    """Test basic cone creation."""
    geo = GeometryService()
    cone = geo.create_cone(50, 25, 100)
    assert cone is not None


def test_create_cone_with_axis():
    """Test cone creation with custom axis."""
    geo = GeometryService()
    cone = geo.create_cone(50, 25, 100, position=(0, 0, 0), direction=(0, 1, 0))
    assert cone is not None


def test_create_torus_basic():
    """Test basic torus creation."""
    geo = GeometryService()
    torus = geo.create_torus(50, 15)
    assert torus is not None


def test_create_torus_with_axis():
    """Test torus creation with custom axis."""
    geo = GeometryService()
    torus = geo.create_torus(50, 15, position=(0, 0, 0), direction=(0, 0, 1))
    assert torus is not None


def test_translate_shape():
    """Test shape translation."""
    geo = GeometryService()
    box = geo.create_box(100, 100, 100)
    translated = geo.translate_shape(box, 50, 25, 10)
    assert translated is not None
    # Original and translated should be different objects
    assert translated is not box


def test_multiple_shape_types():
    """Test creating multiple different shape types."""
    geo = GeometryService()
    shapes = [
        geo.create_box(100, 100, 100),
        geo.create_sphere(50),
        geo.create_cylinder(25, 100),
        geo.create_cone(50, 25, 100),
        geo.create_torus(50, 15),
    ]

    # All shapes should be created successfully
    assert all(shape is not None for shape in shapes)
    # All shapes should be different objects
    assert len(set(id(shape) for shape in shapes)) == len(shapes)
