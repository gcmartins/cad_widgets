"""
Enums for OCP Widget display and view controls
"""

from enum import StrEnum


class ViewDirection(StrEnum):
    """Standard view directions for 3D visualization."""

    TOP = "top"
    BOTTOM = "bottom"
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    ISO = "iso"


class ProjectionType(StrEnum):
    """Camera projection types."""

    PERSPECTIVE = "perspective"
    ORTHOGRAPHIC = "orthographic"


class DisplayMode(StrEnum):
    """Shape display modes."""

    SHADED = "shaded"
    WIREFRAME = "wireframe"
    BOTH = "both"


class SelectionMode(StrEnum):
    """3D entity selection modes."""

    VOLUME = "volume"
    SURFACE = "surface"
    EDGE = "edge"
    VERTEX = "vertex"


class ShapeType(StrEnum):
    """Geometry shape types."""

    BOX = "box"
    SPHERE = "sphere"
    CYLINDER = "cylinder"
    CONE = "cone"
    TORUS = "torus"
