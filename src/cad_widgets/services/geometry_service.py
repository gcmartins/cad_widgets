"""
Geometry Service
Handles shape creation and management operations
Provides high-level API for creating and manipulating 3D shapes
"""

import logging
from typing import Optional, Tuple, Protocol, runtime_checkable
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
from OCP.STEPControl import STEPControl_Writer, STEPControl_Reader, STEPControl_AsIs
from OCP.IGESControl import IGESControl_Writer, IGESControl_Reader
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static

logger = logging.getLogger(__name__)


@runtime_checkable
class GeometryServiceProtocol(Protocol):
    """Structural interface for geometry operations.

    Allows injecting alternative implementations (e.g. mocks in tests)
    into GeometryManager without changing any production callsite.
    """

    def create_box(self, width: float, height: float, depth: float, position: Tuple[float, float, float] = ...) -> "TopoDS_Shape": ...  # noqa: E501
    def create_sphere(self, radius: float, center: Tuple[float, float, float] = ...) -> "TopoDS_Shape": ...
    def create_cylinder(self, radius: float, height: float, position: Tuple[float, float, float] = ..., direction: Tuple[float, float, float] = ...) -> "TopoDS_Shape": ...  # noqa: E501
    def create_cone(self, radius1: float, radius2: float, height: float, position: Tuple[float, float, float] = ..., direction: Tuple[float, float, float] = ...) -> "TopoDS_Shape": ...  # noqa: E501
    def create_torus(self, major_radius: float, minor_radius: float, position: Tuple[float, float, float] = ..., direction: Tuple[float, float, float] = ...) -> "TopoDS_Shape": ...  # noqa: E501
    def translate_shape(self, shape: "TopoDS_Shape", dx: float, dy: float, dz: float) -> "TopoDS_Shape": ...
    def rotate_shape(self, shape: "TopoDS_Shape", axis_point: Tuple[float, float, float], axis_direction: Tuple[float, float, float], angle_degrees: float) -> "TopoDS_Shape": ...  # noqa: E501
    def fuse_shapes(self, shape1: "TopoDS_Shape", shape2: "TopoDS_Shape") -> Optional["TopoDS_Shape"]: ...
    def cut_shapes(self, shape1: "TopoDS_Shape", shape2: "TopoDS_Shape") -> Optional["TopoDS_Shape"]: ...
    def import_file(self, filename: str) -> Optional["TopoDS_Shape"]: ...
    def export_shapes_to_step(self, shapes: list, filename: str) -> bool: ...
    def export_shapes_to_iges(self, shapes: list, filename: str) -> bool: ...


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
            logger.error("Error fusing shapes: %s", e, exc_info=True)
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
            logger.error("Error cutting shapes: %s", e, exc_info=True)
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
            logger.error("Error intersecting shapes: %s", e, exc_info=True)
        return None

    @staticmethod
    def export_step(shape: TopoDS_Shape, filename: str) -> bool:
        """Export a shape to a STEP file.
        
        Args:
            shape: Shape to export
            filename: Path to the output STEP file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create STEP writer
            writer = STEPControl_Writer()
            
            # Set transfer mode
            Interface_Static.SetCVal_s("write.step.schema", "AP203")
            
            # Transfer shape
            writer.Transfer(shape, STEPControl_AsIs)
            
            # Write to file
            status = writer.Write(filename)
            
            return status == IFSelect_ReturnStatus.IFSelect_RetDone
        except Exception as e:
            logger.error("Error exporting STEP file: %s", e, exc_info=True)
            return False

    @staticmethod
    def _import_with_reader(reader, filename: str, file_type: str) -> Optional[TopoDS_Shape]:
        """Common import logic for STEP and IGES files.
        
        Args:
            reader: The reader object (STEPControl_Reader or IGESControl_Reader)
            filename: Path to the file to import
            file_type: Type of file for error messages ("STEP" or "IGES")
            
        Returns:
            Imported shape or None if import failed
        """
        try:
            # Read file
            status = reader.ReadFile(filename)
            
            if status != IFSelect_ReturnStatus.IFSelect_RetDone:
                logger.error("Error reading %s file: %s", file_type, filename)
                return None
            
            # Transfer roots
            reader.TransferRoots()
            
            # Get shape
            shape = reader.OneShape()
            
            return shape if not shape.IsNull() else None
        except Exception as e:
            logger.error("Error importing %s file: %s", file_type, e, exc_info=True)
            return None

    @staticmethod
    def import_file(filename: str) -> Optional[TopoDS_Shape]:
        """Import a shape from a file (STEP or IGES).
        File type is automatically detected based on extension.
        
        Args:
            filename: Path to the file to import (.step, .stp, .iges, .igs)
            
        Returns:
            Imported shape or None if import failed
        """
        # Detect file type from extension
        filename_lower = filename.lower()
        if filename_lower.endswith(('.step', '.stp')):
            return GeometryService._import_with_reader(STEPControl_Reader(), filename, "STEP")
        elif filename_lower.endswith(('.iges', '.igs')):
            return GeometryService._import_with_reader(IGESControl_Reader(), filename, "IGES")
        else:
            logger.warning("Unsupported file format: %s", filename)
            return None

    @staticmethod
    def export_iges(shape: TopoDS_Shape, filename: str) -> bool:
        """Export a shape to an IGES file.
        
        Args:
            shape: Shape to export
            filename: Path to the output IGES file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create IGES writer
            writer = IGESControl_Writer()
            
            # Add shape
            writer.AddShape(shape)
            
            # Write to file
            writer.ComputeModel()
            success = writer.Write(filename)
            
            return success
        except Exception as e:
            logger.error("Error exporting IGES file: %s", e, exc_info=True)
            return False

    @staticmethod
    def export_shapes_to_iges(shapes: list[TopoDS_Shape], filename: str) -> bool:
        """Export multiple shapes to a single IGES file.
        
        Args:
            shapes: List of shapes to export
            filename: Path to the output IGES file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create IGES writer
            writer = IGESControl_Writer()
            
            # Add all shapes
            for shape in shapes:
                writer.AddShape(shape)
            
            # Write to file
            writer.ComputeModel()
            success = writer.Write(filename)
            
            return success
        except Exception as e:
            logger.error("Error exporting IGES file: %s", e, exc_info=True)
            return False

    def export_shapes_to_step(self, shapes: list[TopoDS_Shape], filename: str) -> bool:
        """Export multiple shapes to a single STEP file.
        
        Args:
            shapes: List of shapes to export
            filename: Path to the output STEP file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create STEP writer
            writer = STEPControl_Writer()
            
            # Set transfer mode
            Interface_Static.SetCVal_s("write.step.schema", "AP203")
            
            # Transfer all shapes
            for shape in shapes:
                writer.Transfer(shape, STEPControl_AsIs)
            
            # Write to file
            status = writer.Write(filename)
            
            return status == IFSelect_ReturnStatus.IFSelect_RetDone
        except Exception as e:
            logger.error("Error exporting STEP file: %s", e, exc_info=True)
            return False
