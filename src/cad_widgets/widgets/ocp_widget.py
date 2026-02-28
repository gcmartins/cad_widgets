"""
OCP Widget for PySide6
A 3D CAD viewer widget integrating OpenCascade (OCP) with PySide6

Features:
- Smooth, flicker-free rotation, panning, and zooming
- Immediate rendering mode for interactive operations
- Rendering lock to prevent concurrent redraws
- Platform-specific window integration (X11/Windows/macOS)
"""

from typing import Optional

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
import sys

from OCP.V3d import V3d_Viewer
from OCP.Aspect import Aspect_DisplayConnection
from OCP.OpenGl import OpenGl_GraphicDriver
from OCP.AIS import AIS_InteractiveContext

from ..enums import ViewDirection, ProjectionType, DisplayMode, SelectionMode
from ..services import SelectionService, ViewService

# Platform-specific window imports
if sys.platform == "win32":
    from OCP.WNT import WNT_Window
elif sys.platform == "darwin":
    from OCP.Cocoa import Cocoa_Window
else:
    from OCP.Xw import Xw_Window


class OCPWidget(QWidget):
    """
    A Qt widget for displaying OpenCascade 3D content.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set widget properties
        self.setMinimumSize(640, 480)
        self.setMouseTracking(True)

        # Set widget attributes for proper rendering
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        # Initialize OpenCascade components
        self._display_connection = None
        self._graphic_driver = None
        self._viewer = None
        self._view = None
        self._context = None

        # Services
        self._selection_service: Optional[SelectionService] = None
        self._view_service: Optional[ViewService] = None

        # Mouse tracking
        self._last_pos = None
        self._mouse_moved = False  # Track if mouse moved during press

        # Initialize the viewer
        self._init_viewer()

        # Setup the view after widget is shown
        QTimer.singleShot(100, self._setup_view)

    def _init_viewer(self):
        """Initialize the OpenCascade viewer components."""
        try:
            # Create display connection
            self._display_connection = Aspect_DisplayConnection()

            # Create graphic driver
            self._graphic_driver = OpenGl_GraphicDriver(self._display_connection)

            # Create viewer
            self._viewer = V3d_Viewer(self._graphic_driver)

            # Set viewer properties
            self._viewer.SetDefaultLights()
            self._viewer.SetLightOn()

            # Create view
            self._view = self._viewer.CreateView()

            # Create AIS context for interactive display
            self._context = AIS_InteractiveContext(self._viewer)

            # Initialize services
            self._selection_service = SelectionService(self._context)
            self._view_service = ViewService(self._view, self._viewer, self._context)

            # Note: Window setup happens via native Qt integration
            # The viewer renders when paintEvent triggers Redraw()

        except Exception as e:
            print(f"Error initializing viewer: {e}")
            import traceback

            traceback.print_exc()

    def _setup_view(self):
        """Setup view parameters after widget is shown."""
        if self._view and self._view_service:
            try:
                # Create and set the native window
                self._create_occ_window()

                # Map the view
                self._view_service.must_be_resized()

                # Setup initial view parameters
                self._view_service.setup_initial_view()

                # Fit all objects
                self.fit_all()

            except Exception as e:
                print(f"Error setting up view: {e}")

    def _create_occ_window(self):
        """Create and set the platform-specific OCC window."""
        try:
            window_handle = int(self.winId())

            if sys.platform == "win32":
                # Windows
                occ_window = WNT_Window(window_handle)
            elif sys.platform == "darwin":
                # macOS
                occ_window = Cocoa_Window(window_handle)
            else:
                # Linux/X11
                # On X11, we need both display and window ID
                # The display connection was created during viewer init
                occ_window = Xw_Window(self._display_connection, window_handle)

            # Set the window for the view
            self._view.SetWindow(occ_window)  # type: ignore[union-attr]

            # Map the window if needed
            if not occ_window.IsMapped():
                occ_window.Map()

        except Exception as e:
            print(f"Error creating OCC window: {e}")
            import traceback

            traceback.print_exc()

    def display_shape(
        self,
        shape,
        color=None,
        transparency=0.0,
        update=True,
        display_mode: Optional[DisplayMode] = None,
    ):
        """
        Display an OCP shape in the viewer.

        Args:
            shape: OCP TopoDS_Shape object
            color: Tuple of RGB values (0-1) or None for default
            transparency: Float 0-1 for transparency
            update: Whether to update the display
            display_mode: DisplayMode enum or None for default

        Returns:
            AIS_Shape object
        """
        if not self._view_service:
            return None

        return self._view_service.display_shape(
            shape, color, transparency, update, display_mode
        )

    def erase_all(self):
        """Remove all shapes from the display."""
        if self._view_service:
            self._view_service.erase_all()

    def fit_all(self):
        """Fit all displayed objects in the view."""
        if self._view_service:
            self._view_service.fit_all()
            self.update_display()

    def update_display(self):
        """Update the display."""
        if self._view_service:
            self._view_service.redraw()

    def set_projection(self, direction: ViewDirection):
        """
        Set view direction.

        Args:
            direction: ViewDirection enum
        """
        if self._view_service:
            self._view_service.set_projection(direction)
            self.fit_all()

    def set_projection_type(
        self, projection_type: ProjectionType = ProjectionType.PERSPECTIVE
    ):
        """
        Set the camera projection type.

        Args:
            projection_type: ProjectionType enum
        """
        if self._view_service:
            self._view_service.set_projection_type(projection_type)
            self.update_display()

    def set_display_mode(self, mode: DisplayMode = DisplayMode.SHADED):
        """
        Set the display mode for all shapes.

        Args:
            mode: DisplayMode enum
        """
        if self._view_service:
            self._view_service.set_display_mode(mode)
            self.update_display()

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        if self._view_service:
            self._view_service.must_be_resized()
            self._view_service.redraw()

    def paintEvent(self, event):
        """Handle paint events."""
        # OpenCascade handles its own rendering
        if self._view_service:
            self._view_service.redraw()

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        self._last_pos = event.position().toPoint()
        self._mouse_moved = False  # Reset movement flag

        # Start rotation or panning
        if self._view_service:
            x, y = self._last_pos.x(), self._last_pos.y()
            if event.buttons() & Qt.MouseButton.LeftButton:
                self._view_service.start_rotation(x, y)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for rotation, panning, and hover detection."""
        pos = event.position().toPoint()
        x, y = pos.x(), pos.y()

        # If no buttons pressed, handle hover detection
        if event.buttons() == Qt.MouseButton.NoButton:
            if (
                self._view
                and self._selection_service
                and self._selection_service.is_enabled()
            ):
                self._selection_service.move_to(x, y, self._view, True)
            return

        # Handle dragging operations
        if not self._view_service or not self._last_pos:
            return

        dx = x - self._last_pos.x()
        dy = y - self._last_pos.y()

        # Mark that mouse has moved
        if abs(dx) > 2 or abs(dy) > 2:  # Threshold to ignore tiny movements
            self._mouse_moved = True

        if event.buttons() & Qt.MouseButton.LeftButton:
            # Rotation - use current position
            self._view_service.rotate(x, y)
            self._view_service.redraw()
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            # Panning
            self._view_service.pan(dx, dy)
            self._view_service.redraw()

        self._last_pos = pos

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        # If left button was clicked without moving (not a drag), perform selection
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not self._mouse_moved
            and self._selection_service
            and self._selection_service.is_enabled()
        ):
            pos = event.position().toPoint()
            x, y = pos.x(), pos.y()

            # Handle selection based on modifier keys
            replace = not (
                event.modifiers()
                & (
                    Qt.KeyboardModifier.ControlModifier
                    | Qt.KeyboardModifier.ShiftModifier
                )
            )
            self._selection_service.select(x, y, self._view, replace)

        # Clear last position to end interaction
        self._last_pos = None
        self._mouse_moved = False

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if not self._view_service:
            return

        delta = event.angleDelta().y()
        zoom_factor = 1.2 if delta > 0 else 0.8
        self._view_service.zoom(zoom_factor)
        self._view_service.redraw()

    def get_context(self):
        """Get the AIS interactive context."""
        return self._context

    def get_view(self):
        """Get the V3d view."""
        return self._view

    def get_viewer(self):
        """Get the V3d viewer."""
        return self._viewer

    def get_selection_service(self) -> Optional[SelectionService]:
        """Get the selection service."""
        return self._selection_service

    def get_view_service(self) -> Optional[ViewService]:
        """Get the view service."""
        return self._view_service

    def set_selection_mode(self, mode: SelectionMode):
        """
        Set the selection mode for picking entities.

        Args:
            mode: SelectionMode enum (VOLUME, SURFACE, EDGE, VERTEX)
        """
        if self._selection_service:
            self._selection_service.set_mode(mode)
            self.update_display()

    def set_selection_enabled(self, enabled: bool):
        """
        Enable or disable selection.

        Args:
            enabled: True to enable selection, False to disable
        """
        if self._selection_service:
            self._selection_service.set_enabled(enabled)

    def clear_selection(self):
        """Clear all selected entities."""
        if self._selection_service:
            self._selection_service.clear()

    def get_selection_mode(self) -> SelectionMode:
        """
        Get the current selection mode.

        Returns:
            Current SelectionMode
        """
        if self._selection_service:
            return self._selection_service.get_mode()
        return SelectionMode.VOLUME

    def is_selection_enabled(self) -> bool:
        """
        Check if selection is enabled.

        Returns:
            True if selection is enabled, False otherwise
        """
        if self._selection_service:
            return self._selection_service.is_enabled()
        return False

    def get_selected_shapes(self):
        """
        Get list of currently selected AIS shapes.

        Returns:
            List of selected AIS_Shape objects
        """
        if self._selection_service:
            return self._selection_service.get_selected_shapes()
        return []
