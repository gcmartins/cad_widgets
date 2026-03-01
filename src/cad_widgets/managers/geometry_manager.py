"""
Geometry Manager
Manages geometry shapes, their properties, and interactions with the viewer
"""

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
)


@dataclass
class ManagedShape:
    """A managed shape with its properties and metadata."""
    shape: Any  # TopoDS_Shape
    shape_type: ShapeType
    name: str
    color: Tuple[float, float, float]
    properties: ShapeProperties
    transparency: float = 0.0


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

    def create_shape(
        self,
        shape_id: str,
        shape_type: ShapeType,
        name: str,
        color: Tuple[float, float, float],
        properties: ShapeProperties,
        transparency: float = 0.0
    ) -> Any:
        """
        Create a shape from properties.
        
        Args:
            shape_id: Unique identifier for the shape
            shape_type: Type of shape (ShapeType enum)
            name: Display name
            color: RGB color tuple
            properties: Shape properties
            transparency: Transparency value (0-1)
            
        Returns:
            Created TopoDS_Shape
        """
        shape = self._create_shape_from_properties(shape_type, properties)
        
        if shape:
            managed_shape = ManagedShape(
                shape=shape,
                shape_type=shape_type,
                name=name,
                color=color,
                properties=properties,
                transparency=transparency
            )
            self._shapes[shape_id] = managed_shape
            
            # Emit signal for observers
            self.shape_created.emit(shape_id, managed_shape)
        
        return shape

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
                properties.radius,
                properties.radius * 0.2,
                properties.height
            )
        elif shape_type == ShapeType.TORUS and isinstance(properties, TorusProperties):
            shape = self._geo_service.create_torus(
                properties.radius,
                properties.length
            )
        else:
            return None

        # Apply translation
        tx = properties.translation.x
        ty = properties.translation.y
        tz = properties.translation.z
        if tx != 0 or ty != 0 or tz != 0:
            shape = self._geo_service.translate_shape(shape, tx, ty, tz)

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
