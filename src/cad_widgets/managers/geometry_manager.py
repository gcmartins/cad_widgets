"""
Geometry Manager
Manages geometry shapes, their properties, and interactions with the viewer
"""
import uuid

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

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
    ImportedProperties,
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
    # For UNION/SUBTRACTION: the input shapes kept as editable internal components
    components: List["ManagedShape"] = field(default_factory=list)
    # Set when this shape is an internal component of a boolean operation
    parent_id: Optional[str] = None


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

    def _generate_shape_name(self, shape_type: ShapeType) -> str:
        """
        Generate a standardized shape name based on shape type.
        Pattern: <SHAPE_TYPE>_<incremental_number>
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            
        Returns:
            Generated name (e.g., "Box_1", "Sphere_2", "Union_1")
        """
        # Count existing shapes of this type
        count = sum(1 for s in self._shapes.values() if s.shape_type == shape_type)
        # Generate name with capitalized shape type and incremental number
        return f"{shape_type.value.capitalize()}_{count + 1}"

    def create_shape(
        self,
        shape_type: ShapeType,
        color: Tuple[float, float, float],
        properties: ShapeProperties,
        name: Optional[str] = None
    ) -> Any:
        """
        Create a shape from properties.
        
        Args:
            shape_type: Type of shape (ShapeType enum)
            color: RGB color tuple
            properties: Shape properties
            name: Display name (auto-generated if None)
            
        Returns:
            Created TopoDS_Shape
        """
        # Auto-generate name if not provided
        if name is None:
            name = self._generate_shape_name(shape_type)
        
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

    def import_shape(
        self,
        filename: str,
        color: Tuple[float, float, float],
        properties: Optional[ImportedProperties] = None,
        name: Optional[str] = None
    ) -> Any:
        """
        Import an existing shape from a file (STEP or IGES).
        File type is automatically detected based on extension.
        
        Args:
            filename: Path to the file to import (.step, .stp, .iges, .igs)
            color: RGB color tuple
            properties: Optional ImportedProperties (defaults to new instance)
            name: Display name (auto-generated if None)
            
        Returns:
            ManagedShape instance or None if import fails
        """
        # Import using unified import_file method
        shape = self._geo_service.import_file(filename)
        
        # Check if import was successful
        if shape is None:
            return None
        
        if properties is None:
            properties = ImportedProperties()
        
        # Auto-generate name if not provided
        if name is None:
            name = self._generate_shape_name(ShapeType.IMPORTED)
        
        # Apply transformations if any
        transformed_shape = self._apply_transformations(shape, properties)
        
        shape_id = self._new_shape_id(ShapeType.IMPORTED)
        managed_shape = ManagedShape(
            shape_id=shape_id,
            shape=transformed_shape,
            shape_type=ShapeType.IMPORTED,
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

        When the shape is an internal component of a boolean operation the
        component is rebuilt and the parent boolean shape is recomputed and
        re-emitted automatically.
        
        Args:
            shape_id: ID of the shape to update
            properties: New properties
            
        Returns:
            Updated TopoDS_Shape or None if shape not found
        """
        if shape_id not in self._shapes:
            return None

        managed_shape = self._shapes[shape_id]

        # Case 1: component of a boolean op – update it then recompute parent
        if managed_shape.parent_id is not None:
            return self._update_component_shape(managed_shape, properties)

        # Case 2: UNION/SUBTRACTION that owns components – recompute from scratch
        if managed_shape.shape_type in (ShapeType.UNION, ShapeType.SUBTRACTION) \
                and managed_shape.components:
            base_shape = self._recompute_boolean_from_components(managed_shape)
            if base_shape is None:
                return None
            new_shape = self._apply_transformations(base_shape, properties)
            managed_shape.shape = new_shape
            managed_shape.properties = properties
            self.shape_updated.emit(shape_id, managed_shape)
            return new_shape

        # Case 3: IMPORTED – swap transforms
        if managed_shape.shape_type == ShapeType.IMPORTED:
            new_shape = self._update_transformed_shape(managed_shape, properties)
            if new_shape:
                managed_shape.shape = new_shape
                managed_shape.properties = properties
                self.shape_updated.emit(shape_id, managed_shape)
            return new_shape

        # Case 4: primitive shape – recreate from properties
        new_shape = self._create_shape_from_properties(managed_shape.shape_type, properties)
        if new_shape:
            managed_shape.shape = new_shape
            managed_shape.properties = properties
            self.shape_updated.emit(shape_id, managed_shape)
        return new_shape

    def _update_component_shape(
        self,
        managed_shape: "ManagedShape",
        properties: ShapeProperties
    ) -> Optional[Any]:
        """
        Rebuild a component shape and propagate the change to its parent boolean.
        """
        parent = self._shapes.get(managed_shape.parent_id)
        if parent is None:
            return None

        # Rebuild the component itself
        if managed_shape.shape_type in (ShapeType.UNION, ShapeType.SUBTRACTION) \
                and managed_shape.components:
            base = self._recompute_boolean_from_components(managed_shape)
            new_shape = self._apply_transformations(base, properties) if base else None
        elif managed_shape.shape_type == ShapeType.IMPORTED:
            new_shape = self._update_transformed_shape(managed_shape, properties)
        else:
            new_shape = self._create_shape_from_properties(managed_shape.shape_type, properties)

        if new_shape is None:
            return None

        managed_shape.shape = new_shape
        managed_shape.properties = properties

        # Recompute the parent boolean using the rebuilt component
        base_shape = self._recompute_boolean_from_components(parent)
        if base_shape is None:
            return None
        parent.shape = self._apply_transformations(base_shape, parent.properties)

        self.shape_updated.emit(parent.shape_id, parent)
        return new_shape

    def _recompute_boolean_from_components(
        self,
        managed_shape: "ManagedShape"
    ) -> Optional[Any]:
        """
        Recompute the merged geometry of a boolean shape from its stored components.
        """
        if not managed_shape.components:
            return managed_shape.shape

        component_shapes = [c.shape for c in managed_shape.components]

        if managed_shape.shape_type == ShapeType.UNION:
            result = component_shapes[0]
            for cs in component_shapes[1:]:
                result = self._geo_service.fuse_shapes(result, cs)
                if result is None:
                    return None
        elif managed_shape.shape_type == ShapeType.SUBTRACTION:
            result = component_shapes[0]
            for cs in component_shapes[1:]:
                result = self._geo_service.cut_shapes(result, cs)
                if result is None:
                    return None
        else:
            return managed_shape.shape

        return result

    def _update_transformed_shape(
        self,
        managed_shape: "ManagedShape",
        new_properties: ShapeProperties
    ) -> Any:
        """
        Rebuild a shape by unapplying its current transformations then applying
        the new ones.  Used for imported shapes and legacy boolean shapes that
        have no stored components.
        """
        shape = managed_shape.shape

        # Unapply current translation
        old_tx = managed_shape.properties.translation.x
        old_ty = managed_shape.properties.translation.y
        old_tz = managed_shape.properties.translation.z
        if old_tx != 0 or old_ty != 0 or old_tz != 0:
            shape = self._geo_service.translate_shape(shape, -old_tx, -old_ty, -old_tz)

        # Unapply current rotation (reverse order)
        old_rz = managed_shape.properties.rotation.z
        old_ry = managed_shape.properties.rotation.y
        old_rx = managed_shape.properties.rotation.x
        if old_rz != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (0, 0, 1), -old_rz)
        if old_ry != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (0, 1, 0), -old_ry)
        if old_rx != 0:
            shape = self._geo_service.rotate_shape(shape, (0, 0, 0), (1, 0, 0), -old_rx)

        return self._apply_transformations(shape, new_properties)

    def remove_shape(self, shape_id: str) -> bool:
        """
        Remove a shape from management.
        Component shapes (internal to a boolean operation) cannot be removed
        individually — remove the parent boolean shape instead.
        
        Args:
            shape_id: ID of the shape to remove
            
        Returns:
            True if removed, False if not found or if it is a component
        """
        if shape_id not in self._shapes:
            return False

        managed_shape = self._shapes[shape_id]

        # Components belong to a parent boolean shape and cannot be deleted alone
        if managed_shape.parent_id is not None:
            return False

        # Recursively purge component shapes from the registry (no signals)
        self._remove_component_subtree(managed_shape)

        del self._shapes[shape_id]
        self.shape_removed.emit(shape_id)
        return True

    def _remove_component_subtree(self, managed_shape: "ManagedShape") -> None:
        """Remove all nested component shapes from the registry without emitting signals."""
        for comp in managed_shape.components:
            self._remove_component_subtree(comp)
            self._shapes.pop(comp.shape_id, None)

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
        """Get list of all top-level (non-component) managed shape IDs."""
        return [sid for sid, s in self._shapes.items() if s.parent_id is None]

    def clear_all(self):
        """Clear all managed shapes."""
        self._shapes.clear()
        
        # Emit signal for observers
        self.all_cleared.emit()

    def union_shapes(self, shape_ids: list[str]) -> Optional[str]:
        """
        Perform boolean union on multiple shapes.
        The input shapes are kept as internal components of the resulting union;
        they remain editable and appear in the tree under the union branch.
        
        Args:
            shape_ids: List of shape IDs to union
            
        Returns:
            New shape ID or None if operation fails
        """
        if len(shape_ids) < 2:
            return None

        # Only top-level shapes can be used as inputs
        shapes = [self._shapes[sid] for sid in shape_ids
                  if sid in self._shapes and self._shapes[sid].parent_id is None]
        if len(shapes) < 2:
            return None

        # Compute the fused geometry
        result_shape = shapes[0].shape
        result_color = shapes[0].color
        for managed_shape in shapes[1:]:
            result_shape = self._geo_service.fuse_shapes(result_shape, managed_shape.shape)
            if result_shape is None:
                return None

        new_shape_id = self._new_shape_id(ShapeType.UNION)
        result_name = self._generate_shape_name(ShapeType.UNION)
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
            properties=properties,
            components=shapes,
        )

        # Mark every input shape as a component of this union
        for comp in shapes:
            comp.parent_id = new_shape_id

        # Remove input shapes from the top-level view (they live under the union now)
        for shape_id in shape_ids:
            if shape_id in self._shapes:
                self.shape_removed.emit(shape_id)

        # Register and announce the new union shape
        self._shapes[new_shape_id] = new_managed_shape
        self.shape_created.emit(new_shape_id, new_managed_shape)

        return new_shape_id

    def subtract_shapes(self, shape_ids: list[str]) -> Optional[str]:
        """
        Perform boolean subtraction on multiple shapes (first minus the rest).
        The input shapes are kept as internal components of the result;
        they remain editable and appear in the tree under the subtraction branch.
        
        Args:
            shape_ids: List of shape IDs (first is base, rest are subtracted)
            
        Returns:
            New shape ID or None if operation fails
        """
        if len(shape_ids) < 2:
            return None

        # Only top-level shapes can be used as inputs
        shapes = [self._shapes[sid] for sid in shape_ids
                  if sid in self._shapes and self._shapes[sid].parent_id is None]
        if len(shapes) < 2:
            return None

        # Compute the cut geometry
        result_shape = shapes[0].shape
        result_color = shapes[0].color
        for managed_shape in shapes[1:]:
            result_shape = self._geo_service.cut_shapes(result_shape, managed_shape.shape)
            if result_shape is None:
                return None

        new_shape_id = self._new_shape_id(ShapeType.SUBTRACTION)
        result_name = self._generate_shape_name(ShapeType.SUBTRACTION)
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
            properties=properties,
            components=shapes,
        )

        # Mark every input shape as a component of this subtraction
        for comp in shapes:
            comp.parent_id = new_shape_id

        # Remove input shapes from the top-level view (they live under the subtraction now)
        for shape_id in shape_ids:
            if shape_id in self._shapes:
                self.shape_removed.emit(shape_id)

        # Register and announce the new subtraction shape
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
                properties.major_radius,
                properties.minor_radius
            )
        elif shape_type == ShapeType.IMPORTED and isinstance(properties, ImportedProperties):
            # For imported shapes, no base shape is created
            # The shape is already provided externally
            return None
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
        elif shape_type == ShapeType.IMPORTED:
            return ImportedProperties(**kwargs)
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
        elif shape_type == ShapeType.IMPORTED:
            return ImportedProperties.from_dict(data)
        else:
            return ShapeProperties.from_dict(data)
        
    def export_shapes_to_iges(self, filename: str) -> bool:
        shape_ids = self.get_all_shape_ids()
        shapes = [self.get_shape(sid).shape for sid in shape_ids]
        return self._geo_service.export_shapes_to_iges(shapes, filename)
    
    def export_shapes_to_step(self, filename: str) -> bool:
        shape_ids = self.get_all_shape_ids()
        shapes = [self.get_shape(sid).shape for sid in shape_ids]
        return self._geo_service.export_shapes_to_step(shapes, filename)
