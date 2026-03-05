"""
Geometry Service
Handles shape creation and management operations
Provides high-level API for creating and manipulating 3D shapes
"""

from typing import Optional, Tuple
from OCP.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeTorus,
)
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Trsf, gp_Vec
from OCP.TopoDS import TopoDS_Shape
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common


class GeometryService:
    """Service for creating and managing 3D shapes."""

    @staticmethod
    def create_box(
        width: float,
        height: float,
        depth: float,
        position: Tuple[float, float, float] = (0, 0, 0),
    ) -> TopoDS_Shape:
        """
        Create a box (rectangular prism) centered at the specified position.

        Args:
            width: Width (X dimension)
            height: Height (Y dimension)
            depth: Depth (Z dimension)
            position: Position tuple (x, y, z) of the box center (default: origin)

        Returns:
            TopoDS_Shape representing the box
        """
        # Offset position to center the box at the specified position
        corner_x = position[0] - width / 2
        corner_y = position[1] - height / 2
        corner_z = position[2] - depth / 2
        pos = gp_Pnt(corner_x, corner_y, corner_z)
        box_maker = BRepPrimAPI_MakeBox(pos, width, height, depth)
        return box_maker.Shape()

    @staticmethod
    def create_sphere(
        radius: float, center: Tuple[float, float, float] = (0, 0, 0)
    ) -> TopoDS_Shape:
        """
        Create a sphere.

        Args:
            radius: Radius of the sphere
            center: Center point tuple (x, y, z) (default: origin)

        Returns:
            TopoDS_Shape representing the sphere
        """
        center_pt = gp_Pnt(*center)
        sphere_maker = BRepPrimAPI_MakeSphere(center_pt, radius)
        return sphere_maker.Shape()

    @staticmethod
    def create_cylinder(
        radius: float,
        height: float,
        position: Tuple[float, float, float] = (0, 0, 0),
        direction: Tuple[float, float, float] = (0, 0, 1),
    ) -> TopoDS_Shape:
        """
        Create a cylinder centered at the specified position.

        Args:
            radius: Radius of the cylinder
            height: Height of the cylinder
            position: Position tuple (x, y, z) for the cylinder center
            direction: Direction tuple (x, y, z) for the cylinder axis (default: Z-axis)

        Returns:
            TopoDS_Shape representing the cylinder
        """
        # Offset position to center the cylinder at the specified position
        # Calculate offset along the direction vector
        dir_vec = gp_Dir(*direction)
        offset = height / 2
        base_x = position[0] - dir_vec.X() * offset
        base_y = position[1] - dir_vec.Y() * offset
        base_z = position[2] - dir_vec.Z() * offset
        
        axis = gp_Ax2(gp_Pnt(base_x, base_y, base_z), dir_vec)
        cylinder_maker = BRepPrimAPI_MakeCylinder(axis, radius, height)
        return cylinder_maker.Shape()

    @staticmethod
    def create_cone(
        radius1: float,
        radius2: float,
        height: float,
        position: Tuple[float, float, float] = (0, 0, 0),
        direction: Tuple[float, float, float] = (0, 0, 1),
    ) -> TopoDS_Shape:
        """
        Create a cone or truncated cone.

        Args:
            radius1: Radius at the base
            radius2: Radius at the top
            height: Height of the cone
            position: Position tuple (x, y, z) for the cone base
            direction: Direction tuple (x, y, z) for the cone axis (default: Z-axis)

        Returns:
            TopoDS_Shape representing the cone
        """
        axis = gp_Ax2(gp_Pnt(*position), gp_Dir(*direction))
        cone_maker = BRepPrimAPI_MakeCone(axis, radius1, radius2, height)
        return cone_maker.Shape()

    @staticmethod
    def create_torus(
        major_radius: float,
        minor_radius: float,
        position: Tuple[float, float, float] = (0, 0, 0),
        direction: Tuple[float, float, float] = (0, 0, 1),
    ) -> TopoDS_Shape:
        """
        Create a torus (donut shape).

        Args:
            major_radius: Major radius (distance from center to tube center)
            minor_radius: Minor radius (tube radius)
            position: Position tuple (x, y, z) for the torus center
            direction: Direction tuple (x, y, z) for the torus axis (default: Z-axis)

        Returns:
            TopoDS_Shape representing the torus
        """
        axis = gp_Ax2(gp_Pnt(*position), gp_Dir(*direction))
        torus_maker = BRepPrimAPI_MakeTorus(axis, major_radius, minor_radius)
        return torus_maker.Shape()

    @staticmethod
    def translate_shape(
        shape: TopoDS_Shape, dx: float, dy: float, dz: float
    ) -> TopoDS_Shape:
        """
        Translate (move) a shape.

        Args:
            shape: Shape to translate
            dx: Translation in X direction
            dy: Translation in Y direction
            dz: Translation in Z direction

        Returns:
            Translated shape
        """
        transform = gp_Trsf()
        transform.SetTranslation(gp_Vec(dx, dy, dz))

        transformer = BRepBuilderAPI_Transform(shape, transform, True)
        return transformer.Shape()

    @staticmethod
    def rotate_shape(
        shape: TopoDS_Shape,
        axis_point: Tuple[float, float, float],
        axis_direction: Tuple[float, float, float],
        angle_degrees: float,
    ) -> TopoDS_Shape:
        """
        Rotate a shape around an axis.

        Args:
            shape: Shape to rotate
            axis_point: Point tuple (x, y, z) on the rotation axis
            axis_direction: Direction tuple (x, y, z) of the rotation axis
            angle_degrees: Rotation angle in degrees

        Returns:
            Rotated shape
        """
        import math

        transform = gp_Trsf()
        axis = gp_Ax2(gp_Pnt(*axis_point), gp_Dir(*axis_direction)).Axis()
        transform.SetRotation(axis, math.radians(angle_degrees))

        transformer = BRepBuilderAPI_Transform(shape, transform, True)
        return transformer.Shape()

    @staticmethod
    def scale_shape(
        shape: TopoDS_Shape, center: Tuple[float, float, float], factor: float
    ) -> TopoDS_Shape:
        """
        Scale a shape uniformly.

        Args:
            shape: Shape to scale
            center: Center point tuple (x, y, z) of scaling
            factor: Scale factor (1.0 = no change, 2.0 = double size, 0.5 = half size)

        Returns:
            Scaled shape
        """
        transform = gp_Trsf()
        transform.SetScale(gp_Pnt(*center), factor)

        transformer = BRepBuilderAPI_Transform(shape, transform, True)
        return transformer.Shape()

    @staticmethod
    def fuse_shapes(
        shape1: TopoDS_Shape, shape2: TopoDS_Shape
    ) -> Optional[TopoDS_Shape]:
        """
        Perform boolean union (fusion) of two shapes.

        Args:
            shape1: First shape
            shape2: Second shape

        Returns:
            Fused shape or None if operation fails
        """
        try:
            fuse = BRepAlgoAPI_Fuse(shape1, shape2)
            fuse.Build()
            if fuse.IsDone():
                return fuse.Shape()
        except Exception as e:
            print(f"Error fusing shapes: {e}")
        return None

    @staticmethod
    def cut_shapes(
        shape1: TopoDS_Shape, shape2: TopoDS_Shape
    ) -> Optional[TopoDS_Shape]:
        """
        Perform boolean subtraction (cut shape2 from shape1).

        Args:
            shape1: Base shape
            shape2: Tool shape to subtract

        Returns:
            Result shape or None if operation fails
        """
        try:
            cut = BRepAlgoAPI_Cut(shape1, shape2)
            cut.Build()
            if cut.IsDone():
                return cut.Shape()
        except Exception as e:
            print(f"Error cutting shapes: {e}")
        return None

    @staticmethod
    def intersect_shapes(
        shape1: TopoDS_Shape, shape2: TopoDS_Shape
    ) -> Optional[TopoDS_Shape]:
        """
        Perform boolean intersection (common volume) of two shapes.

        Args:
            shape1: First shape
            shape2: Second shape

        Returns:
            Intersection shape or None if operation fails
        """
        try:
            common = BRepAlgoAPI_Common(shape1, shape2)
            common.Build()
            if common.IsDone():
                return common.Shape()
        except Exception as e:
            print(f"Error intersecting shapes: {e}")
        return None
