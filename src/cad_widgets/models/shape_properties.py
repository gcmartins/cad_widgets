"""
Shape property classes for structured data handling
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Union


@dataclass
class Translation:
    """3D translation/position."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Translation":
        """Create from dictionary."""
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0)
        )


@dataclass
class Rotation:
    """3D rotation in degrees."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Rotation":
        """Create from dictionary."""
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            z=data.get("z", 0.0)
        )


@dataclass
class ShapeProperties:
    """Base class for shape properties."""
    translation: Translation = field(default_factory=Translation)
    rotation: Rotation = field(default_factory=Rotation)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for UI consumption."""
        return {
            "translation": self.translation.to_dict(),
            "rotation": self.rotation.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShapeProperties":
        """Create from dictionary."""
        return cls(
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display in tree."""
        formatted = {}
        
        # Add position if non-zero
        if any([self.translation.x, self.translation.y, self.translation.z]):
            formatted["Position"] = (
                f"({self.translation.x:.1f}, {self.translation.y:.1f}, {self.translation.z:.1f})"
            )
        
        # Add rotation if non-zero
        if any([self.rotation.x, self.rotation.y, self.rotation.z]):
            formatted["Rotation"] = (
                f"({self.rotation.x:.1f}°, {self.rotation.y:.1f}°, {self.rotation.z:.1f}°)"
            )
        
        return formatted


@dataclass
class BoxProperties(ShapeProperties):
    """Properties for box shapes."""
    width: float = 50.0
    height: float = 50.0
    depth: float = 50.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result.update({
            "width": self.width,
            "height": self.height,
            "depth": self.depth,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoxProperties":
        """Create from dictionary."""
        return cls(
            width=data.get("width", 50.0),
            height=data.get("height", 50.0),
            depth=data.get("depth", 50.0),
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display."""
        formatted = super().get_formatted_properties()
        formatted.update({
            "Width": f"{self.width:.2f}",
            "Height": f"{self.height:.2f}",
            "Depth": f"{self.depth:.2f}",
        })
        return formatted


@dataclass
class SphereProperties(ShapeProperties):
    """Properties for sphere shapes."""
    radius: float = 30.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result["radius"] = self.radius
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SphereProperties":
        """Create from dictionary."""
        return cls(
            radius=data.get("radius", 30.0),
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display."""
        formatted = super().get_formatted_properties()
        formatted["Radius"] = f"{self.radius:.2f}"
        return formatted


@dataclass
class CylinderProperties(ShapeProperties):
    """Properties for cylinder shapes."""
    radius: float = 20.0
    height: float = 60.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result.update({
            "radius": self.radius,
            "height": self.height,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CylinderProperties":
        """Create from dictionary."""
        return cls(
            radius=data.get("radius", 20.0),
            height=data.get("height", 60.0),
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display."""
        formatted = super().get_formatted_properties()
        formatted.update({
            "Radius": f"{self.radius:.2f}",
            "Height": f"{self.height:.2f}",
        })
        return formatted


@dataclass
class ConeProperties(ShapeProperties):
    """Properties for cone shapes."""
    radius: float = 30.0
    height: float = 70.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result.update({
            "radius": self.radius,
            "height": self.height,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConeProperties":
        """Create from dictionary."""
        return cls(
            radius=data.get("radius", 30.0),
            height=data.get("height", 70.0),
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display."""
        formatted = super().get_formatted_properties()
        formatted.update({
            "Radius": f"{self.radius:.2f}",
            "Height": f"{self.height:.2f}",
        })
        return formatted


@dataclass
class TorusProperties(ShapeProperties):
    """Properties for torus shapes."""
    radius: float = 25.0
    length: float = 10.0  # tube radius

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = super().to_dict()
        result.update({
            "radius": self.radius,
            "length": self.length,
        })
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TorusProperties":
        """Create from dictionary."""
        return cls(
            radius=data.get("radius", 25.0),
            length=data.get("length", 10.0),
            translation=Translation.from_dict(data.get("translation", {})),
            rotation=Rotation.from_dict(data.get("rotation", {})),
        )

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display."""
        formatted = super().get_formatted_properties()
        formatted.update({
            "Radius": f"{self.radius:.2f}",
            "Length": f"{self.length:.2f}",
        })
        return formatted
