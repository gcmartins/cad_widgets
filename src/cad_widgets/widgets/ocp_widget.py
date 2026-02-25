"""
OCP Widget for PySide6
A 3D CAD viewer widget integrating OpenCascade (OCP) with PySide6

Features:
- Smooth, flicker-free rotation, panning, and zooming
- Immediate rendering mode for interactive operations
- Rendering lock to prevent concurrent redraws
- Platform-specific window integration (X11/Windows/macOS)
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
import sys

from OCP.V3d import V3d_Viewer, V3d_TypeOfVisualization
from OCP.Aspect import (
    Aspect_DisplayConnection,
    Aspect_TypeOfTriedronPosition,
)
from OCP.OpenGl import OpenGl_GraphicDriver
from OCP.AIS import AIS_InteractiveContext, AIS_Shape
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB, Quantity_NOC_WHITE
from OCP.Graphic3d import Graphic3d_Camera

from .enums import ViewDirection, ProjectionType, DisplayMode

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
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        
        # Initialize OpenCascade components
        self._display_connection = None
        self._graphic_driver = None
        self._viewer = None
        self._view = None
        self._context = None
        
        # Mouse tracking
        self._last_pos = None
        
        # Rendering control
        self._is_rendering = False
        
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
            
            # Note: Window setup happens via native Qt integration
            # The viewer renders when paintEvent triggers Redraw()
            
            # Set white background
            self._view.SetBackgroundColor(Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB))
            
        except Exception as e:
            print(f"Error initializing viewer: {e}")
            import traceback
            traceback.print_exc()

    def _setup_view(self):
        """Setup view parameters after widget is shown."""
        if self._view:
            try:
                # Create and set the native window
                self._create_occ_window()
                
                # Map the view
                self._view.MustBeResized()
                
                # Set up trihedron (axis indicator)
                try:
                    # Create white color for trihedron
                    white_color = Quantity_Color(Quantity_NOC_WHITE)
                    # Display trihedron with proper parameters
                    self._view.TriedronDisplay(
                        Aspect_TypeOfTriedronPosition.Aspect_TOTP_LEFT_LOWER,
                        white_color,
                        0.08,
                        V3d_TypeOfVisualization.V3d_WIREFRAME
                    )
                except (TypeError, AttributeError):
                    # Try with minimal parameters if signature is different
                    try:
                        white_color = Quantity_Color(Quantity_NOC_WHITE)
                        self._view.TriedronDisplay(
                            Aspect_TypeOfTriedronPosition.Aspect_TOTP_LEFT_LOWER,
                            white_color,
                            0.08
                        )
                    except Exception as e2:
                        print(f"Could not display trihedron: {e2}")
                except Exception as e:
                    print(f"Unexpected trihedron error: {e}")
                
                # Set projection to perspective
                try:
                    self._view.Camera().SetProjectionType(
                        Graphic3d_Camera.Projection_Perspective
                    )
                except (TypeError, AttributeError):
                    # Try alternative approach with enum value
                    try:
                        # Projection_Perspective might be an int (0)
                        self._view.Camera().SetProjectionType(0)
                    except Exception as e2:
                        print(f"Could not set perspective projection: {e2}")
                except Exception as e:
                    print(f"Unexpected projection error: {e}")
                
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
                occ_window = Xw_Window(
                    self._display_connection,
                    window_handle
                )
            
            # Set the window for the view
            self._view.SetWindow(occ_window)
            
            # Map the window if needed
            if not occ_window.IsMapped():
                occ_window.Map()
                
        except Exception as e:
            print(f"Error creating OCC window: {e}")
            import traceback
            traceback.print_exc()

    def display_shape(self, shape, color=None, transparency=0.0, update=True, display_mode: DisplayMode = None):
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
        if not self._context:
            return None
            
        try:
            # Create AIS shape
            ais_shape = AIS_Shape(shape)
            
            # Set color if provided
            if color:
                r, g, b = color
                quantity_color = Quantity_Color(r, g, b, Quantity_TOC_RGB)
                ais_shape.SetColor(quantity_color)
            
            # Set transparency
            if transparency > 0:
                ais_shape.SetTransparency(transparency)
            
            # Display the shape
            self._context.Display(ais_shape, update)
            
            # Set display mode if specified
            if display_mode:
                if display_mode == DisplayMode.WIREFRAME:
                    self._context.SetDisplayMode(ais_shape, 0, update)  # 0 = Wireframe
                elif display_mode == DisplayMode.SHADED:
                    self._context.SetDisplayMode(ais_shape, 1, update)  # 1 = Shaded
            
            return ais_shape
            
        except Exception as e:
            print(f"Error displaying shape: {e}")
            return None

    def erase_all(self):
        """Remove all shapes from the display."""
        if self._context:
            self._context.RemoveAll(True)

    def fit_all(self):
        """Fit all displayed objects in the view."""
        if self._view:
            try:
                self._view.FitAll()
                self._view.ZFitAll()
                self.update_display()
            except Exception as e:
                print(f"Error fitting view: {e}")

    def update_display(self):
        """Update the display."""
        if self._view:
            try:
                # Force immediate redraw for visual feedback
                self._redraw_immediate()
            except Exception as e:
                print(f"Error updating display: {e}")
    
    def _redraw_immediate(self):
        """Immediate redraw for interactive operations, bypasses Qt paint queue."""
        if self._view and not self._is_rendering:
            try:
                self._is_rendering = True
                self._view.Redraw()
                self._is_rendering = False
            except Exception as e:
                self._is_rendering = False
                print(f"Error in immediate redraw: {e}")

    def set_projection(self, direction: ViewDirection):
        """
        Set view direction.
        
        Args:
            direction: ViewDirection enum
        """
        if not self._view:
            return
            
        try:
            if direction == ViewDirection.TOP:
                self._view.SetProj(0, 0, 1)
                self._view.SetUp(0, 1, 0)  # Y-axis up for top view
            elif direction == ViewDirection.BOTTOM:
                self._view.SetProj(0, 0, -1)
                self._view.SetUp(0, 1, 0)  # Y-axis up for bottom view
            elif direction == ViewDirection.FRONT:
                self._view.SetProj(0, -1, 0)
                self._view.SetUp(0, 0, 1)  # Z-axis up for front view
            elif direction == ViewDirection.BACK:
                self._view.SetProj(0, 1, 0)
                self._view.SetUp(0, 0, 1)  # Z-axis up for back view
            elif direction == ViewDirection.LEFT:
                self._view.SetProj(-1, 0, 0)
                self._view.SetUp(0, 0, 1)  # Z-axis up for left view
            elif direction == ViewDirection.RIGHT:
                self._view.SetProj(1, 0, 0)
                self._view.SetUp(0, 0, 1)  # Z-axis up for right view
            elif direction == ViewDirection.ISO:
                self._view.SetProj(1, 1, 1)
                self._view.SetUp(0, 0, 1)  # Z-axis up for iso view
            
            self.fit_all()
        except Exception as e:
            print(f"Error setting projection: {e}")

    def set_projection_type(self, projection_type: ProjectionType = ProjectionType.PERSPECTIVE):
        """
        Set the camera projection type.
        
        Args:
            projection_type: ProjectionType enum
        """
        if not self._view:
            return
            
        try:
            if projection_type == ProjectionType.ORTHOGRAPHIC:
                self._view.Camera().SetProjectionType(
                    Graphic3d_Camera.Projection_Orthographic
                )
            else:  # perspective
                self._view.Camera().SetProjectionType(
                    Graphic3d_Camera.Projection_Perspective
                )
            self.update_display()
        except Exception as e:
            print(f"Error setting projection type: {e}")
    
    def set_display_mode(self, mode: DisplayMode = DisplayMode.SHADED):
        """
        Set the display mode for all shapes.
        
        Args:
            mode: DisplayMode enum
        """
        if not self._context:
            return
            
        try:
            if mode == DisplayMode.WIREFRAME:
                # Display mode 0 = Wireframe
                self._context.SetDisplayMode(0, True)
            elif mode == DisplayMode.BOTH:
                # Display mode 2 = Both shaded and wireframe
                self._context.SetDisplayMode(2, True)
            else:  # shaded
                # Display mode 1 = Shaded
                self._context.SetDisplayMode(1, True)
            self.update_display()
        except Exception as e:
            print(f"Error setting display mode: {e}")

    def resizeEvent(self, event):
        """Handle widget resize."""
        super().resizeEvent(event)
        if self._view:
            try:
                self._view.MustBeResized()
                # Use immediate redraw after resize
                self._redraw_immediate()
            except Exception as e:
                print(f"Error resizing view: {e}")

    def paintEvent(self, event):
        """Handle paint events."""
        # OpenCascade handles its own rendering
        # Only redraw if not already rendering
        if self._view and not self._is_rendering:
            try:
                self._is_rendering = True
                self._view.Redraw()
                self._is_rendering = False
            except Exception as e:
                self._is_rendering = False
                print(f"Error in paint event: {e}")

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        self._last_pos = event.position().toPoint()
        
        # Start rotation or panning
        if self._view:
            x, y = self._last_pos.x(), self._last_pos.y()
            if event.buttons() & Qt.LeftButton:
                self._view.StartRotation(x, y)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for rotation and panning."""
        if not self._view or not self._last_pos:
            return

        pos = event.position().toPoint()
        x, y = pos.x(), pos.y()
        dx = x - self._last_pos.x()
        dy = y - self._last_pos.y()

        try:
            if event.buttons() & Qt.LeftButton:
                # Rotation - use current position
                self._view.Rotation(x, y)
                # Use immediate redraw for smooth interaction
                self._redraw_immediate()
            elif event.buttons() & Qt.MiddleButton:
                # Panning
                self._view.Pan(dx, -dy)
                # Use immediate redraw for smooth interaction
                self._redraw_immediate()
        except Exception as e:
            print(f"Error in mouse move: {e}")

        self._last_pos = pos

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        # Clear last position to end interaction
        self._last_pos = None

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if not self._view:
            return

        try:
            delta = event.angleDelta().y()
            zoom_factor = 1.2 if delta > 0 else 0.8
            self._view.SetZoom(zoom_factor)
            # Use immediate redraw for smooth interaction
            self._redraw_immediate()
        except Exception as e:
            print(f"Error in wheel event: {e}")

    def get_context(self):
        """Get the AIS interactive context."""
        return self._context

    def get_view(self):
        """Get the V3d view."""
        return self._view

    def get_viewer(self):
        """Get the V3d viewer."""
        return self._viewer
