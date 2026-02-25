"""
Shape creation and manipulation utilities for OCP
"""

from OCP.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeTorus,
)
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Vec, gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform


def create_box(width, height, depth, position=None):
    """
    Create a box shape.
    
    Args:
        width: Box width (X dimension)
        height: Box height (Y dimension)
        depth: Box depth (Z dimension)
        position: Optional gp_Pnt for box corner position
        
    Returns:
        TopoDS_Shape: The created box shape
    """
    if position:
        return BRepPrimAPI_MakeBox(position, width, height, depth).Shape()
    return BRepPrimAPI_MakeBox(width, height, depth).Shape()


def create_sphere(radius, center=None):
    """
    Create a sphere shape.
    
    Args:
        radius: Sphere radius
        center: Optional gp_Pnt for sphere center
        
    Returns:
        TopoDS_Shape: The created sphere shape
    """
    if center:
        return BRepPrimAPI_MakeSphere(center, radius).Shape()
    return BRepPrimAPI_MakeSphere(radius).Shape()


def create_cylinder(radius, height, axis=None):
    """
    Create a cylinder shape.
    
    Args:
        radius: Cylinder radius
        height: Cylinder height
        axis: Optional gp_Ax2 for cylinder axis (default: Z-axis at origin)
        
    Returns:
        TopoDS_Shape: The created cylinder shape
    """
    if not axis:
        axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()


def create_cone(radius1, radius2, height, axis=None):
    """
    Create a cone shape.
    
    Args:
        radius1: Bottom radius
        radius2: Top radius
        height: Cone height
        axis: Optional gp_Ax2 for cone axis (default: Z-axis at origin)
        
    Returns:
        TopoDS_Shape: The created cone shape
    """
    if not axis:
        axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCone(axis, radius1, radius2, height).Shape()


def create_torus(major_radius, minor_radius, axis=None):
    """
    Create a torus shape.
    
    Args:
        major_radius: Major radius (distance from center to tube center)
        minor_radius: Minor radius (tube radius)
        axis: Optional gp_Ax2 for torus axis (default: Z-axis at origin)
        
    Returns:
        TopoDS_Shape: The created torus shape
    """
    if not axis:
        axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeTorus(axis, major_radius, minor_radius).Shape()


def translate_shape(shape, dx, dy, dz):
    """
    Translate a shape by the given offset.
    
    Args:
        shape: The shape to translate
        dx: X offset
        dy: Y offset
        dz: Z offset
        
    Returns:
        TopoDS_Shape: The translated shape
    """
    transform = gp_Trsf()
    transform.SetTranslation(gp_Vec(dx, dy, dz))
    return BRepBuilderAPI_Transform(shape, transform).Shape()
