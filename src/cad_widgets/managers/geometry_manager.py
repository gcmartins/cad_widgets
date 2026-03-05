"""
Geometry Manager
Manages geometry shapes, their properties, and interactions with the viewer
"""
import uuid

from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from ..services import GeometryService
from ..enums import ShapeType
from ..models.shape_properties import (
    ShapeProperties,
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
    Translation,
    Rotation
)


@dataclass
class ManagedShape:
    """A managed shape with its properties and metadata."""
    shape_id: str
    shape: Any  # TopoDS_Shape
    shape_type: ShapeType
    name: str
    color: Tuple[float, float, float]
    properties: ShapeProperties


class GeometryManager(QObject):
    """
    Manages geometry shapes and their lifecycle.
    
    Provides a high-level API for:
    - Creating shapes from properties
    - Updating shape properties
    - Managing shape storage
    - Converting between shapes and properties
    
    Signals:
        shape_created: Emitted when a new shape is created (shape_id, managed_shape)
        shape_updated: Emitted when a shape is updated (shape_id, managed_shape)
        shape_removed: Emitted when a shape is removed (shape_id)
        all_cleared: Emitted when all shapes are cleared
    """
    
    # Signals
    shape_created = Signal(str, object)  # shape_id, ManagedShape
    shape_updated = Signal(str, object)  # shape_id, ManagedShape
    shape_removed = Signal(str)  # shape_id
    all_cleared = Signal()

    def __init__(self):
        """Initialize the geometry manager."""
        super().__init__()
        self._shapes: Dict[str, ManagedShape] = {}
        self._geo_service = GeometryService()

    def _new_shape_id(self, shape_type: ShapeType) -> str:
        """Generate a new unique shape ID based on shape type."""
        return f"{shape_type.value}_{uuid.uuid4().hex[:8]}"

    def create_shape(
        self,
        shape_type: ShapeType,
        name: str,
        color: Tuple[float, float, float],
        properties: ShapeProperties
    ) -> Any:
        """
        Create a shape from properties.
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            name: Display name
            color: RGB color tuple
            properties: Shape properties
            
        Returns:
            Created TopoDS_Shape
        """
        shape = self._create_shape_from_properties(shape_type, properties)
        
        if shape:
            shape_id = self._new_shape_id(shape_type)
            managed_shape = ManagedShape(
                shape_id=shape_id,
                shape=shape,
                shape_type=shape_type,
                name=name,
                color=color,
                properties=properties
            )
            self._shapes[shape_id] = managed_shape
            
            # Emit signal for observers
            self.shape_created.emit(shape_id, managed_shape)
        
        return managed_shape

    def update_shape(
        self,
        shape_id: str,
        properties: ShapeProperties
    ) -> Optional[Any]:
        """
        Update a shape with new properties.
        
        Args:
            shape_id: ID of the shape to update
            properties: New properties
            
        Returns:
            Updated TopoDS_Shape or None if shape not found
        """
        if shape_id not in self._shapes:
            return None
        
        managed_shape = self._shapes[shape_id]
        
        # For UNION and SUBTRACTION shapes, we need to:
        # 1. Unapply the current transformations to get back to the base shape
        # 2. Apply the new transformations
        if managed_shape.shape_type in (ShapeType.UNION, ShapeType.SUBTRACTION):
            # Get the base shape by unapplying current transformations
            base_shape = managed_shape.shape
            
            # Unapply current translation (inverse operation)
            old_tx = managed_shape.properties.translation.x
            old_ty = managed_shape.properties.translation.y
            old_tz = managed_shape.properties.translation.z
            if old_tx != 0 or old_ty != 0 or old_tz != 0:
                base_shape = self._geo_service.translate_shape(base_shape, -old_tx, -old_ty, -old_tz)
            
            # Unapply current rotation (inverse operation, in reverse order)
            old_rz = managed_shape.properties.rotation.z
            old_ry = managed_shape.properties.rotation.y
            old_rx = managed_shape.properties.rotation.x
            if old_rz != 0:
                base_shape = self._geo_service.rotate_shape(base_shape, (0, 0, 0), (0, 0, 1), -old_rz)
            if old_ry != 0:
                base_shape = self._geo_service.rotate_shape(base_shape, (0, 0, 0), (0, 1, 0), -old_ry)
            if old_rx != 0:
                base_shape = self._geo_service.rotate_shape(base_shape, (0, 0, 0), (1, 0, 0), -old_rx)
            
            # Now apply new transformations to the base shape
            new_shape = self._apply_transformations(base_shape, properties)
        else:
            # For primitive shapes, recreate from properties
            new_shape = self._create_shape_from_properties(
                managed_shape.shape_type,
                properties
            )
        
        if new_shape:
            managed_shape.shape = new_shape
            managed_shape.properties = properties
            
            # Emit signal for observers
            self.shape_updated.emit(shape_id, managed_shape)
        
        return new_shape

    def remove_shape(self, shape_id: str) -> bool:
        """
        Remove a shape from management.
        
        Args:
            shape_id: ID of the shape to remove
            
        Returns:
            True if removed, False if not found
        """
        if shape_id in self._shapes:
            del self._shapes[shape_id]
            
            # Emit signal for observers
            self.shape_removed.emit(shape_id)
            return True
        return False

    def get_shape(self, shape_id: str) -> Optional[ManagedShape]:
        """
        Get a managed shape by ID.
        
        Args:
            shape_id: ID of the shape
            
        Returns:
            ManagedShape or None if not found
        """
        return self._shapes.get(shape_id)

    def get_all_shape_ids(self) -> list[str]:
        """Get list of all managed shape IDs."""
        return list(self._shapes.keys())

    def clear_all(self):
        """Clear all managed shapes."""
        self._shapes.clear()
        
        # Emit signal for observers
        self.all_cleared.emit()

    def union_shapes(self, shape_ids: list[str]) -> Optional[str]:
        """
        Perform boolean union on multiple shapes.
        Creates a new shape and removes the original shapes.
        
        Args:
            shape_ids: List of shape IDs to union
            
        Returns:
            New shape ID or None if operation fails
        """
        if len(shape_ids) < 2:
            return None
        
        # Get all shapes
        shapes = [self._shapes[sid] for sid in shape_ids if sid in self._shapes]
        if len(shapes) < 2:
            return None
        
        # Start with first shape
        result_shape = shapes[0].shape
        result_color = shapes[0].color
        result_name = "Union"
        
        # Union with remaining shapes
        for managed_shape in shapes[1:]:
            result_shape = self._geo_service.fuse_shapes(result_shape, managed_shape.shape)
            if result_shape is None:
                return None
        
        # Generate new shape ID
        new_shape_id = self._new_shape_id(ShapeType.UNION)
        
        # Create managed shape with basic properties (translation/rotation are already applied)   
        properties = ShapeProperties(
            translation=Translation(x=0, y=0, z=0),
            rotation=Rotation(x=0, y=0, z=0)
        )
        
        new_managed_shape = ManagedShape(
            shape_id=new_shape_id,
            shape=result_shape,
            shape_type=ShapeType.UNION,
            name=result_name,
            color=result_color,
            properties=properties
        )
        
        # Remove original shapes
        for shape_id in shape_ids:
            if shape_id in self._shapes:
                del self._shapes[shape_id]
                self.shape_removed.emit(shape_id)
        
        # Add new shape
        self._shapes[new_shape_id] = new_managed_shape
        self.shape_created.emit(new_shape_id, new_managed_shape)
        
        return new_shape_id

    def subtract_shapes(self, shape_ids: list[str]) -> Optional[str]:
        """
        Perform boolean subtraction on multiple shapes.
        Subtracts all shapes from the first one.
        Creates a new shape and removes the original shapes.
        
        Args:
            shape_ids: List of shape IDs (first is base, rest are subtracted)
            
        Returns:
            New shape ID or None if operation fails
        """
        if len(shape_ids) < 2:
            return None
        
        # Get all shapes
        shapes = [self._shapes[sid] for sid in shape_ids if sid in self._shapes]
        if len(shapes) < 2:
            return None
        
        # Start with first shape as base
        result_shape = shapes[0].shape
        result_color = shapes[0].color
        result_name = "Subtraction"
        
        # Subtract remaining shapes
        for managed_shape in shapes[1:]:
            result_shape = self._geo_service.cut_shapes(result_shape, managed_shape.shape)
            if result_shape is None:
                return None
        
        # Generate new shape ID
        new_shape_id = self._new_shape_id(ShapeType.SUBTRACTION)
        
        # Create managed shape with basic properties
        properties = ShapeProperties(
            translation=Translation(x=0, y=0, z=0),
            rotation=Rotation(x=0, y=0, z=0)
        )
        
        new_managed_shape = ManagedShape(
            shape_id=new_shape_id,
            shape=result_shape,
            shape_type=ShapeType.SUBTRACTION,
            name=result_name,
            color=result_color,
            properties=properties
        )
        
        # Remove original shapes
        for shape_id in shape_ids:
            if shape_id in self._shapes:
                del self._shapes[shape_id]
                self.shape_removed.emit(shape_id)
        
        # Add new shape
        self._shapes[new_shape_id] = new_managed_shape
        self.shape_created.emit(new_shape_id, new_managed_shape)
        
        return new_shape_id

    def _apply_transformations(
        self,
        shape: Any,
        properties: ShapeProperties
    ) -> Any:
        """
        Apply rotation and translation transformations to a shape.
        
        Args:
            shape: The shape to transform
            properties: Shape properties containing rotation and translation
            
        Returns:
            Transformed shape
        """
        # Apply rotation
        rx = properties.rotation.x
        ry = properties.rotation.y
        rz = properties.rotation.z
        if rx != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (1, 0, 0), rx)
        if ry != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (0, 1, 0), ry)
        if rz != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (0, 0, 1), rz)
        
        # Apply translation
        tx = properties.translation.x
        ty = properties.translation.y
        tz = properties.translation.z
        if tx != 0 or ty != 0 or tz != 0:
            shape = self._geo_service.translate_shape(shape, tx, ty, tz)

        return shape

    def _create_shape_from_properties(
        self,
        shape_type: ShapeType,
        properties: ShapeProperties
    ) -> Optional[Any]:
        """
        Create a geometry shape from properties.
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            properties: Shape properties
            
        Returns:
            TopoDS_Shape or None
        """
        # Create base shape based on type
        if shape_type == ShapeType.BOX and isinstance(properties, BoxProperties):
            shape = self._geo_service.create_box(
                properties.width,
                properties.height,
                properties.depth
            )
        elif shape_type == ShapeType.SPHERE and isinstance(properties, SphereProperties):
            shape = self._geo_service.create_sphere(properties.radius)
        elif shape_type == ShapeType.CYLINDER and isinstance(properties, CylinderProperties):
            shape = self._geo_service.create_cylinder(
                properties.radius,
                properties.height
            )
        elif shape_type == ShapeType.CONE and isinstance(properties, ConeProperties):
            shape = self._geo_service.create_cone(
                properties.base_radius,
                properties.top_radius,
                properties.height
            )
        elif shape_type == ShapeType.TORUS and isinstance(properties, TorusProperties):
            shape = self._geo_service.create_torus(
                properties.radius,
                properties.length
            )
        else:
            return None

        # Apply transformations (rotation and translation)
        shape = self._apply_transformations(shape, properties)

        return shape

    @staticmethod
    def create_properties_for_type(
        shape_type: ShapeType,
        **kwargs
    ) -> ShapeProperties:
        """
        Create appropriate properties object for a shape type.
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            **kwargs: Property values
            
        Returns:
            ShapeProperties subclass instance
        """
        if shape_type == ShapeType.BOX:
            return BoxProperties(**kwargs)
        elif shape_type == ShapeType.SPHERE:
            return SphereProperties(**kwargs)
        elif shape_type == ShapeType.CYLINDER:
            return CylinderProperties(**kwargs)
        elif shape_type == ShapeType.CONE:
            return ConeProperties(**kwargs)
        elif shape_type == ShapeType.TORUS:
            return TorusProperties(**kwargs)
        else:
            return ShapeProperties(**kwargs)

    @staticmethod
    def properties_from_dict(
        shape_type: ShapeType,
        data: Dict[str, Any]
    ) -> ShapeProperties:
        """
        Create properties from dictionary.
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            data: Dictionary with property values
            
        Returns:
            ShapeProperties subclass instance
        """
        if shape_type == ShapeType.BOX:
            return BoxProperties.from_dict(data)
        elif shape_type == ShapeType.SPHERE:
            return SphereProperties.from_dict(data)
        elif shape_type == ShapeType.CYLINDER:
            return CylinderProperties.from_dict(data)
        elif shape_type == ShapeType.CONE:
            return ConeProperties.from_dict(data)
        elif shape_type == ShapeType.TORUS:
            return TorusProperties.from_dict(data)
        else:
            return ShapeProperties.from_dict(data)
