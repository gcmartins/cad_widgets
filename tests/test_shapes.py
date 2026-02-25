"""
Tests for shape creation utilities
"""

import pytest
from cad_widgets.utils import (
    create_box, create_sphere, create_cylinder, 
    create_cone, create_torus, translate_shape
)
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir


def test_create_box_basic():
    """Test basic box creation."""
    box = create_box(100, 50, 75)
    assert box is not None


def test_create_box_with_position():
    """Test box creation with custom position."""
    position = gp_Pnt(10, 20, 30)
    box = create_box(100, 50, 75, position=position)
    assert box is not None


def test_create_sphere_basic():
    """Test basic sphere creation."""
    sphere = create_sphere(50)
    assert sphere is not None


def test_create_sphere_with_center():
    """Test sphere creation with custom center."""
    center = gp_Pnt(10, 20, 30)
    sphere = create_sphere(50, center=center)
    assert sphere is not None


def test_create_cylinder_basic():
    """Test basic cylinder creation."""
    cylinder = create_cylinder(25, 100)
    assert cylinder is not None


def test_create_cylinder_with_axis():
    """Test cylinder creation with custom axis."""
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))
    cylinder = create_cylinder(25, 100, axis=axis)
    assert cylinder is not None


def test_create_cone_basic():
    """Test basic cone creation."""
    cone = create_cone(50, 25, 100)
    assert cone is not None


def test_create_cone_with_axis():
    """Test cone creation with custom axis."""
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0))
    cone = create_cone(50, 25, 100, axis=axis)
    assert cone is not None


def test_create_torus_basic():
    """Test basic torus creation."""
    torus = create_torus(50, 15)
    assert torus is not None


def test_create_torus_with_axis():
    """Test torus creation with custom axis."""
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    torus = create_torus(50, 15, axis=axis)
    assert torus is not None


def test_translate_shape():
    """Test shape translation."""
    box = create_box(100, 100, 100)
    translated = translate_shape(box, 50, 25, 10)
    assert translated is not None
    # Original and translated should be different objects
    assert translated is not box


def test_multiple_shape_types():
    """Test creating multiple different shape types."""
    shapes = [
        create_box(100, 100, 100),
        create_sphere(50),
        create_cylinder(25, 100),
        create_cone(50, 25, 100),
        create_torus(50, 15),
    ]
    
    # All shapes should be created successfully
    assert all(shape is not None for shape in shapes)
    # All shapes should be different objects
    assert len(set(id(shape) for shape in shapes)) == len(shapes)
