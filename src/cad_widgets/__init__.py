"""
CAD Widgets - OpenCascade PySide6 Integration
A library for building 3D CAD viewers with PySide6 and OpenCascade (OCP)
"""

from .widgets.ocp_widget import OCPWidget
from .widgets.view_toolbar import ViewToolbar
from .widgets.selection_toolbar import SelectionToolbar
from .widgets.enums import ViewDirection, ProjectionType, DisplayMode, SelectionMode
from .services import SelectionService, ViewService, GeometryService

__version__ = "0.1.0"
