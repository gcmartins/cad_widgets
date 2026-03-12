"""
View Service
Handles all view-related operations and geometry display for OCP viewer
"""

from typing import Optional, Tuple, Dict
from OCP.V3d import V3d_View, V3d_Viewer, V3d_TypeOfVisualization
from OCP.Aspect import Aspect_GradientFillMethod, Aspect_TypeOfTriedronPosition
from OCP.Quantity import Quantity_Color, Quantity_NOC_WHITE, Quantity_TOC_RGB
from OCP.Graphic3d import Graphic3d_Camera
from OCP.AIS import AIS_InteractiveContext, AIS_Shape
from OCP.Prs3d import Prs3d_LineAspect
from OCP.Aspect import Aspect_TOL_SOLID

from cad_widgets.enums import ViewDirection, ProjectionType, DisplayMode


class ShapeInfo:
    """Information about a displayed shape."""

    def __init__(
        self,
        shape_id: str,
        ais_shape: AIS_Shape,
        color: Optional[Tuple[float, float, float]] = None,
        visible: bool = True,
    ):
        self.shape_id = shape_id
        self.ais_shape = ais_shape
        self.color = color
        self.visible = visible


class ViewService:
    """Service for managing view operations and geometry display in OCP viewer."""

    def __init__(
        self, view: V3d_View, viewer: V3d_Viewer, context: AIS_InteractiveContext
    ):
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
        self._shapes: Dict[str, ShapeInfo] = {}  # Shape registry
        self._global_transparency: float = 0.0  # Track global transparency setting
        self._current_display_mode: DisplayMode = DisplayMode.SHADED  # Track current display mode
        self._background_color: tuple[float, float, float] = (1.0, 1.0, 1.0)  # Default white
        self._background_gradient: tuple | None = None  # (color1, color2, method) or None

    def setup_initial_view(self):
        """Setup initial view parameters."""
        try:
            if self._background_gradient:
                color1, color2, method = self._background_gradient
                self._view.SetBgGradientColors(
                    Quantity_Color(*color1, Quantity_TOC_RGB),
                    Quantity_Color(*color2, Quantity_TOC_RGB),
                    method,
                    True,
                )
            else:
                self._view.SetBackgroundColor(
                    Quantity_Color(*self._background_color, Quantity_TOC_RGB)
                )

            # Set up trihedron (axis indicator)
            self._setup_trihedron()

            # Set projection to orthographic by default
            self.set_projection_type(ProjectionType.ORTHOGRAPHIC)

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
                V3d_TypeOfVisualization.V3d_WIREFRAME,
            )
        except (TypeError, AttributeError):
            # Try with minimal parameters if signature is different
            try:
                white_color = Quantity_Color(Quantity_NOC_WHITE)
                self._view.TriedronDisplay(
                    Aspect_TypeOfTriedronPosition.Aspect_TOTP_LEFT_LOWER,
                    white_color,
                    0.08,
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

    def _configure_shape_edges(self, ais_shape: AIS_Shape, enable: bool):
        """
        Configure edge display for a shape.

        Args:
            ais_shape: The AIS shape to configure
            enable: True to enable edges (for BOTH mode), False to disable
        """
        drawer = ais_shape.Attributes()
        drawer.SetFaceBoundaryDraw(enable)
        
        if enable:
            # Create line aspect for edges (black solid lines)
            edge_aspect = Prs3d_LineAspect(
                Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB),
                Aspect_TOL_SOLID,
                1.0
            )
            drawer.SetFaceBoundaryAspect(edge_aspect)
        
        ais_shape.SetAttributes(drawer)

    def display_shape(
        self,
        shape,
        shape_id: str,
        color: Optional[Tuple[float, float, float]] = None,
        update: bool = True,
        shape_type: str = "Shape",
        name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Display an OCP shape in the viewer.

        Args:
            shape: OCP TopoDS_Shape object
            color: Tuple of RGB values (0-1) or None for default
            update: Whether to update the display
            shape_type: Type of shape (Box, Sphere, etc.) for identification
            name: Optional name for the shape
            shape_id: Optional specific ID for the shape (auto-generated if None)

        Returns:
            str: Shape ID or None if error
        """
        try:
            # Create AIS shape
            ais_shape = AIS_Shape(shape)

            # Set color if provided
            if color:
                r, g, b = color
                quantity_color = Quantity_Color(r, g, b, Quantity_TOC_RGB)
                ais_shape.SetColor(quantity_color)

            # Apply global transparency
            if self._global_transparency > 0:
                ais_shape.SetTransparency(self._global_transparency)

            # Display the shape - inherits global display mode
            self._context.Display(ais_shape, update)

            # Only handle special attributes for BOTH mode (shaded with edges)
            # Wireframe and Shaded modes are handled globally by the context
            if self._current_display_mode == DisplayMode.BOTH:
                # Enable facet boundaries for shaded with edges
                self._configure_shape_edges(ais_shape, True)
                self._context.Redisplay(ais_shape, update)

            # Store shape information
            shape_info = ShapeInfo(
                shape_id=shape_id,
                ais_shape=ais_shape,
                color=color,
                visible=True,
            )
            self._shapes[shape_id] = shape_info

            return shape_id

        except Exception as e:
            print(f"Error displaying shape: {e}")
            return None

    def set_display_mode(self, mode: DisplayMode):
        """
        Set the display mode globally for all shapes.

        Args:
            mode: DisplayMode enum
        """
        # Store the current display mode
        self._current_display_mode = mode
        
        try:
            if mode == DisplayMode.WIREFRAME:
                # Set global display mode to wireframe
                self._context.SetDisplayMode(0, False)
                # Disable facet boundaries on all shapes (in case they were enabled)
                for shape_info in self._shapes.values():
                    self._configure_shape_edges(shape_info.ais_shape, False)
                    self._context.Redisplay(shape_info.ais_shape, False)
            elif mode == DisplayMode.BOTH:
                # Set global display mode to shaded
                self._context.SetDisplayMode(1, False)
                # Enable facet boundaries on all shapes for shaded with edges
                for shape_info in self._shapes.values():
                    self._configure_shape_edges(shape_info.ais_shape, True)
                    self._context.Redisplay(shape_info.ais_shape, False)
            else:  # shaded
                # Set global display mode to shaded
                self._context.SetDisplayMode(1, False)
                # Disable facet boundaries on all shapes
                for shape_info in self._shapes.values():
                    self._configure_shape_edges(shape_info.ais_shape, False)
                    self._context.Redisplay(shape_info.ais_shape, False)
            self._context.UpdateCurrentViewer()
        except Exception as e:
            print(f"Error setting display mode: {e}")

    def erase_all(self):
        """Remove all shapes from the display."""
        try:
            self._context.RemoveAll(True)
            self._shapes.clear()
        except Exception as e:
            print(f"Error erasing all shapes: {e}")

    def erase_shape(self, shape_id: str, update: bool = True):
        """
        Remove a specific shape from the display.

        Args:
            shape_id: ID of the shape to remove
            update: Whether to update display
        """
        try:
            if shape_id in self._shapes:
                shape_info = self._shapes[shape_id]
                self._context.Remove(shape_info.ais_shape, update)
                del self._shapes[shape_id]
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
        update: bool = True,
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

    def set_background_color(self, color: tuple[float, float, float]):
        """
        Set the background to a solid color, clearing any gradient.

        Args:
            color: RGB tuple (0.0 - 1.0) e.g. (1.0, 1.0, 1.0) for white.
        """
        try:
            self._background_color = color
            self._background_gradient = None
            self._view.SetBackgroundColor(Quantity_Color(*color, Quantity_TOC_RGB))
            self._view.Redraw()
        except Exception as e:
            print(f"Error setting background color: {e}")

    def set_background_gradient(
        self,
        color1: tuple[float, float, float],
        color2: tuple[float, float, float],
        method: Aspect_GradientFillMethod = Aspect_GradientFillMethod.Aspect_GradientFillMethod_Vertical,
    ):
        """
        Set the background to a two-color gradient.

        Args:
            color1: First color RGB tuple (0.0 - 1.0), top for vertical gradients.
            color2: Second color RGB tuple (0.0 - 1.0), bottom for vertical gradients.
            method: Aspect_GradientFillMethod (Vertical, Horizontal, Diagonal1/2, Corner1-4).
        """
        try:
            self._background_gradient = (color1, color2, method)
            self._view.SetBgGradientColors(
                Quantity_Color(*color1, Quantity_TOC_RGB),
                Quantity_Color(*color2, Quantity_TOC_RGB),
                method,
                True,
            )
            self._view.Redraw()
        except Exception as e:
            print(f"Error setting background gradient: {e}")

    def set_global_transparency(self, transparency: float, update: bool = True):
        """
        Set transparency for all shapes globally.

        Args:
            transparency: Float 0-1 for transparency (0 = opaque, 1 = fully transparent)
            update: Whether to update display
        """
        try:
            # Store the global transparency setting
            self._global_transparency = transparency
            
            # Apply to all existing shapes
            for shape_info in self._shapes.values():
                shape_info.ais_shape.SetTransparency(transparency)
                if update:
                    self._context.Redisplay(shape_info.ais_shape, False)
            
            if update:
                # Single update after all changes
                self._context.UpdateCurrentViewer()
        except Exception as e:
            print(f"Error setting global transparency: {e}")

    # Shape registry methods

    def get_all_shapes(self) -> Dict[str, ShapeInfo]:
        """
        Get all registered shapes.

        Returns:
            Dictionary mapping shape IDs to ShapeInfo objects
        """
        return self._shapes.copy()

    def get_shape_info(self, shape_id: str) -> Optional[ShapeInfo]:
        """
        Get information about a specific shape.

        Args:
            shape_id: ID of the shape

        Returns:
            ShapeInfo object or None if not found
        """
        return self._shapes.get(shape_id)

    def set_shape_visibility(self, shape_id: str, visible: bool, update: bool = True):
        """
        Set the visibility of a shape.

        Args:
            shape_id: ID of the shape
            visible: True to show, False to hide
            update: Whether to update display
        """
        try:
            if shape_id in self._shapes:
                shape_info = self._shapes[shape_id]
                if visible and not shape_info.visible:
                    self._context.Display(shape_info.ais_shape, update)
                    shape_info.visible = True
                elif not visible and shape_info.visible:
                    self._context.Erase(shape_info.ais_shape, update)
                    shape_info.visible = False
        except Exception as e:
            print(f"Error setting shape visibility: {e}")

    def is_shape_visible(self, shape_id: str) -> bool:
        """
        Check if a shape is visible.

        Args:
            shape_id: ID of the shape

        Returns:
            True if visible, False otherwise
        """
        if shape_id in self._shapes:
            return self._shapes[shape_id].visible
        return False

    def get_shape_count(self) -> int:
        """
        Get the number of shapes currently managed.

        Returns:
            Number of shapes
        """
        return len(self._shapes)
