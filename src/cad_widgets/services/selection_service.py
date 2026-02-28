"""
Selection Service
Handles all selection-related operations for OCP viewer
"""

from typing import List, Optional
from OCP.AIS import AIS_InteractiveContext
from OCP.V3d import V3d_View
from OCP.Quantity import Quantity_Color, Quantity_NOC_ORANGE, Quantity_NOC_CYAN1

from cad_widgets.enums import SelectionMode


class SelectionService:
    """Service for managing selection in OCP viewer."""

    def __init__(self, context: AIS_InteractiveContext):
        """
        Initialize the selection service.

        Args:
            context: AIS interactive context
        """
        self._context = context
        self._selection_enabled = True
        self._selection_mode = SelectionMode.VOLUME
        self._configure_selection_colors()

    def _configure_selection_colors(self):
        """Configure stronger highlight and selection colors."""
        try:
            # Get the highlight attributes for dynamic highlighting (hover)
            highlight_drawer = self._context.HighlightStyle()
            if highlight_drawer:
                # Set highlight color to cyan for hover effect
                highlight_color = Quantity_Color(Quantity_NOC_CYAN1)
                highlight_drawer.SetColor(highlight_color)

            # Get the selection attributes for selected entities
            selection_drawer = self._context.SelectionStyle()
            if selection_drawer:
                # Set selection color to a strong orange
                selection_color = Quantity_Color(Quantity_NOC_ORANGE)
                selection_drawer.SetColor(selection_color)

            # Make selection more prominent
            self._context.SetToHilightSelected(True)

        except Exception as e:
            print(f"Error configuring selection colors: {e}")

    def set_mode(self, mode: SelectionMode):
        """
        Set the selection mode for picking entities.

        Args:
            mode: SelectionMode enum (VOLUME, SURFACE, EDGE, VERTEX)
        """
        self._selection_mode = mode

        try:
            # Map selection mode to TopAbs shape types
            if mode == SelectionMode.VOLUME:
                shape_type = 0  # AIS_Shape standard mode for solids
            elif mode == SelectionMode.SURFACE:
                shape_type = 4  # Face selection mode
            elif mode == SelectionMode.EDGE:
                shape_type = 2  # Edge selection mode
            elif mode == SelectionMode.VERTEX:
                shape_type = 1  # Vertex selection mode

            # Deactivate all selection modes first
            self._context.Deactivate()

            # Activate the selected mode for all displayed objects
            if self._selection_enabled:
                self._context.Activate(shape_type, True)

        except Exception as e:
            print(f"Error setting selection mode: {e}")

    def set_enabled(self, enabled: bool):
        """
        Enable or disable selection.

        Args:
            enabled: True to enable selection, False to disable
        """
        self._selection_enabled = enabled

        try:
            if enabled:
                # Re-activate current selection mode
                self.set_mode(self._selection_mode)
            else:
                # Deactivate all selection modes
                self._context.Deactivate()
                # Clear any existing selection
                self._context.ClearSelected(True)
        except Exception as e:
            print(f"Error setting selection enabled: {e}")

    def clear(self):
        """Clear all selected entities."""
        try:
            self._context.ClearSelected(True)
        except Exception as e:
            print(f"Error clearing selection: {e}")

    def move_to(self, x: int, y: int, view: V3d_View, update: bool = True):
        """
        Detect entities at cursor position for hover effect.

        Args:
            x: X coordinate
            y: Y coordinate
            view: V3d view
            update: Whether to update display
        """
        try:
            self._context.MoveTo(x, y, view, update)
        except Exception as e:
            print(f"Error in move to: {e}")

    def select(self, x: int, y: int, view: V3d_View, replace: bool = True):
        """
        Perform selection at given coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
            view: V3d view
            replace: If True, replace current selection; if False, add to selection
        """
        try:
            # Move to position first
            self._context.MoveTo(x, y, view, True)

            # Perform selection
            if replace:
                self._context.Select(True)
            else:
                self._context.ShiftSelect(True)
        except Exception as e:
            print(f"Error handling selection: {e}")

    def get_selected_shapes(self) -> List:
        """
        Get list of currently selected AIS shapes.

        Returns:
            List of selected AIS_Shape objects
        """
        selected = []
        try:
            self._context.InitSelected()
            while self._context.MoreSelected():
                selected.append(self._context.SelectedInteractive())
                self._context.NextSelected()
        except Exception as e:
            print(f"Error getting selected shapes: {e}")

        return selected

    def is_enabled(self) -> bool:
        """
        Check if selection is enabled.

        Returns:
            True if selection is enabled, False otherwise
        """
        return self._selection_enabled

    def get_mode(self) -> SelectionMode:
        """
        Get the current selection mode.

        Returns:
            Current SelectionMode
        """
        return self._selection_mode
