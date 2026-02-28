"""
View Service
Handles all view-related operations and geometry display for OCP viewer
"""

from typing import Optional, Tuple
from OCP.V3d import V3d_View, V3d_Viewer, V3d_TypeOfVisualization
from OCP.Aspect import Aspect_TypeOfTriedronPosition
from OCP.Quantity import Quantity_Color, Quantity_NOC_WHITE, Quantity_TOC_RGB
from OCP.Graphic3d import Graphic3d_Camera
from OCP.AIS import AIS_InteractiveContext, AIS_Shape

from cad_widgets.enums import ViewDirection, ProjectionType, DisplayMode


class ViewService:
    """Service for managing view operations and geometry display in OCP viewer."""
    
    def __init__(self, view: V3d_View, viewer: V3d_Viewer, context: AIS_InteractiveContext):
        """
        Initialize the view service.
        
        Args:
            view: V3d view
            viewer: V3d viewer
            context: AIS interactive context
        """
        self._view = view
        self._viewer = viewer
        self._context = context
        self._is_rendering = False
    
    def setup_initial_view(self):
        """Setup initial view parameters."""
        try:
            # Set white background
            self._view.SetBackgroundColor(
                Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
            )
            
            # Set up trihedron (axis indicator)
            self._setup_trihedron()
            
            # Set projection to perspective
            self.set_projection_type(ProjectionType.PERSPECTIVE)
            
        except Exception as e:
            print(f"Error setting up initial view: {e}")
    
    def _setup_trihedron(self):
        """Setup the trihedron (axis indicator)."""
        try:
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
            except Exception as e:
                print(f"Could not display trihedron: {e}")
        except Exception as e:
            print(f"Unexpected trihedron error: {e}")
    
    def set_projection(self, direction: ViewDirection):
        """
        Set view direction.
        
        Args:
            direction: ViewDirection enum
        """
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
        except Exception as e:
            print(f"Error setting projection: {e}")
    
    def set_projection_type(self, projection_type: ProjectionType):
        """
        Set the camera projection type.
        
        Args:
            projection_type: ProjectionType enum
        """
        try:
            if projection_type == ProjectionType.ORTHOGRAPHIC:
                self._view.Camera().SetProjectionType(
                    Graphic3d_Camera.Projection_Orthographic
                )
            else:  # perspective
                self._view.Camera().SetProjectionType(
                    Graphic3d_Camera.Projection_Perspective
                )
        except (TypeError, AttributeError):
            # Try alternative approach with enum value
            try:
                # Projection types might be ints
                proj_value = 1 if projection_type == ProjectionType.ORTHOGRAPHIC else 0
                self._view.Camera().SetProjectionType(proj_value)
            except Exception as e:
                print(f"Could not set projection type: {e}")
        except Exception as e:
            print(f"Error setting projection type: {e}")
    
    def fit_all(self):
        """Fit all displayed objects in the view."""
        try:
            self._view.FitAll()
            self._view.ZFitAll()
        except Exception as e:
            print(f"Error fitting view: {e}")
    
    def redraw(self):
        """Redraw the view."""
        if not self._is_rendering:
            try:
                self._is_rendering = True
                self._view.Redraw()
                self._is_rendering = False
            except Exception as e:
                self._is_rendering = False
                print(f"Error in redraw: {e}")
    
    def must_be_resized(self):
        """Notify view that it must be resized."""
        try:
            self._view.MustBeResized()
        except Exception as e:
            print(f"Error resizing view: {e}")
    
    def start_rotation(self, x: int, y: int):
        """
        Start rotation at given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            self._view.StartRotation(x, y)
        except Exception as e:
            print(f"Error starting rotation: {e}")
    
    def rotate(self, x: int, y: int):
        """
        Rotate view to given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            self._view.Rotation(x, y)
        except Exception as e:
            print(f"Error rotating: {e}")
    
    def pan(self, dx: int, dy: int):
        """
        Pan the view.
        
        Args:
            dx: Delta X
            dy: Delta Y
        """
        try:
            self._view.Pan(dx, -dy)
        except Exception as e:
            print(f"Error panning: {e}")
    
    def zoom(self, factor: float):
        """
        Zoom the view.
        
        Args:
            factor: Zoom factor
        """
        try:
            self._view.SetZoom(factor)
        except Exception as e:
            print(f"Error zooming: {e}")
    
    def get_view(self) -> V3d_View:
        """Get the V3d view."""
        return self._view
    
    def get_viewer(self) -> V3d_Viewer:
        """Get the V3d viewer."""
        return self._viewer
    
    def get_context(self) -> AIS_InteractiveContext:
        """Get the AIS interactive context."""
        return self._context
    
    # Geometry display methods
    
    def display_shape(
        self, 
        shape, 
        color: Optional[Tuple[float, float, float]] = None,
        transparency: float = 0.0, 
        update: bool = True, 
        display_mode: Optional[DisplayMode] = None
    ) -> Optional[AIS_Shape]:
        """
        Display an OCP shape in the viewer.
        
        Args:
            shape: OCP TopoDS_Shape object
            color: Tuple of RGB values (0-1) or None for default
            transparency: Float 0-1 for transparency
            update: Whether to update the display
            display_mode: DisplayMode enum or None for default
            
        Returns:
            AIS_Shape object or None if error
        """
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
    
    def set_display_mode(self, mode: DisplayMode):
        """
        Set the display mode for all shapes.
        
        Args:
            mode: DisplayMode enum
        """
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
        except Exception as e:
            print(f"Error setting display mode: {e}")
    
    def erase_all(self):
        """Remove all shapes from the display."""
        try:
            self._context.RemoveAll(True)
        except Exception as e:
            print(f"Error erasing all shapes: {e}")
    
    def erase_shape(self, ais_shape: AIS_Shape, update: bool = True):
        """
        Remove a specific shape from the display.
        
        Args:
            ais_shape: AIS_Shape to remove
            update: Whether to update display
        """
        try:
            self._context.Remove(ais_shape, update)
        except Exception as e:
            print(f"Error erasing shape: {e}")
    
    def update_shape(self, ais_shape: AIS_Shape, update: bool = True):
        """
        Update a displayed shape.
        
        Args:
            ais_shape: AIS_Shape to update
            update: Whether to update display
        """
        try:
            self._context.Redisplay(ais_shape, update)
        except Exception as e:
            print(f"Error updating shape: {e}")
    
    def set_shape_color(
        self, 
        ais_shape: AIS_Shape, 
        color: Tuple[float, float, float],
        update: bool = True
    ):
        """
        Set the color of a shape.
        
        Args:
            ais_shape: AIS_Shape to colorize
            color: Tuple of RGB values (0-1)
            update: Whether to update display
        """
        try:
            r, g, b = color
            quantity_color = Quantity_Color(r, g, b, Quantity_TOC_RGB)
            ais_shape.SetColor(quantity_color)
            if update:
                self._context.Redisplay(ais_shape, True)
        except Exception as e:
            print(f"Error setting shape color: {e}")
    
    def set_shape_transparency(
        self, 
        ais_shape: AIS_Shape, 
        transparency: float,
        update: bool = True
    ):
        """
        Set the transparency of a shape.
        
        Args:
            ais_shape: AIS_Shape to set transparency
            transparency: Float 0-1 for transparency
            update: Whether to update display
        """
        try:
            ais_shape.SetTransparency(transparency)
            if update:
                self._context.Redisplay(ais_shape, True)
        except Exception as e:
            print(f"Error setting shape transparency: {e}")
