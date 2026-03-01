"""
CAD Widgets - OpenCascade PySide6 Integration
A library for building 3D CAD viewers with PySide6 and OpenCascade (OCP)
"""

from .widgets.ocp_widget import OCPWidget
from .widgets.view_toolbar import ViewToolbar
from .widgets.selection_toolbar import SelectionToolbar
from .widgets.geometry_tree import GeometryTreeWidget
from .widgets.property_editor import PropertyEditorWidget
from .enums import ViewDirection, ProjectionType, DisplayMode, SelectionMode, ShapeType
from .services import SelectionService, ViewService, GeometryService
from .services.view_service import ShapeInfo
from .managers import GeometryManager, ManagedShape
from .models import (
    Translation,
    Rotation,
    ShapeProperties,
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
)

__version__ = "0.1.0"
