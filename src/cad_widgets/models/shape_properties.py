"""
Shape property classes for structured data handling
"""

import dataclasses
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Any


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

    # ClassVar fields are excluded from dataclasses.fields() automatically.
    _SKIP_FIELDS: ClassVar[frozenset] = frozenset({"translation", "rotation"})
    # Subclasses override this to customise display labels for their fields.
    _display_fields: ClassVar[Dict[str, str]] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {
            "translation": self.translation.to_dict(),
            "rotation": self.rotation.to_dict(),
        }
        for f in dataclasses.fields(self):
            if f.name not in self._SKIP_FIELDS:
                result[f.name] = getattr(self, f.name)
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShapeProperties":
        """Create from dictionary."""
        kwargs: Dict[str, Any] = {
            "translation": Translation.from_dict(data.get("translation", {})),
            "rotation": Rotation.from_dict(data.get("rotation", {})),
        }
        for f in dataclasses.fields(cls):
            if f.name not in cls._SKIP_FIELDS:
                default = (
                    f.default
                    if f.default is not dataclasses.MISSING
                    else f.default_factory()  # type: ignore[misc]
                )
                kwargs[f.name] = data.get(f.name, default)
        return cls(**kwargs)

    def get_formatted_properties(self) -> Dict[str, str]:
        """Get formatted properties for display in tree."""
        formatted: Dict[str, str] = {}

        if any([self.translation.x, self.translation.y, self.translation.z]):
            formatted["Position"] = (
                f"({self.translation.x:.1f}, {self.translation.y:.1f}, {self.translation.z:.1f})"
            )

        if any([self.rotation.x, self.rotation.y, self.rotation.z]):
            formatted["Rotation"] = (
                f"({self.rotation.x:.1f}°, {self.rotation.y:.1f}°, {self.rotation.z:.1f}°)"
            )

        for f in dataclasses.fields(self):
            if f.name not in self._SKIP_FIELDS:
                label = self._display_fields.get(f.name, f.name.replace("_", " ").title())
                formatted[label] = f"{getattr(self, f.name):.2f}"

        return formatted


@dataclass
class BoxProperties(ShapeProperties):
    """Properties for box shapes."""
    width: float = 50.0
    height: float = 50.0
    depth: float = 50.0


@dataclass
class SphereProperties(ShapeProperties):
    """Properties for sphere shapes."""
    radius: float = 30.0


@dataclass
class CylinderProperties(ShapeProperties):
    """Properties for cylinder shapes."""
    radius: float = 20.0
    height: float = 60.0


@dataclass
class ConeProperties(ShapeProperties):
    """Properties for cone shapes."""
    base_radius: float = 30.0
    top_radius: float = 10.0
    height: float = 70.0

    _display_fields: ClassVar[Dict[str, str]] = {
        "base_radius": "Base Radius",
        "top_radius": "Top Radius",
    }


@dataclass
class TorusProperties(ShapeProperties):
    """Properties for torus shapes."""
    major_radius: float = 25.0
    minor_radius: float = 10.0  # tube radius

    _display_fields: ClassVar[Dict[str, str]] = {
        "major_radius": "Major Radius",
        "minor_radius": "Minor Radius",
    }


@dataclass
class ImportedProperties(ShapeProperties):
    """Properties for imported shapes (STEP, IGES, etc.).

    Imported shapes have no editable size parameters,
    only translation and rotation transformations.
    """
