"""
Selection Service
Handles all selection-related operations for OCP viewer
"""

import logging
from typing import List
from OCP.AIS import AIS_InteractiveContext
from OCP.V3d import V3d_View
from OCP.Quantity import Quantity_Color, Quantity_NOC_RED, Quantity_NOC_CYAN1
from OCP.Prs3d import Prs3d_TypeOfHighlight

from cad_widgets.enums import SelectionMode

logger = logging.getLogger(__name__)


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

    def configure_selection_colors(self):
        """Configure stronger highlight and selection colors."""
        try:
            red_color = Quantity_Color(Quantity_NOC_RED)
            cyan_color = Quantity_Color(Quantity_NOC_CYAN1)
            
            # Configure dynamic highlighting (hover) - cyan color
            highlight_drawer = self._context.HighlightStyle(Prs3d_TypeOfHighlight.Prs3d_TypeOfHighlight_Dynamic)
            if highlight_drawer:
                highlight_drawer.SetColor(cyan_color)

            # Configure whole object selection - red color
            selection_drawer = self._context.HighlightStyle(Prs3d_TypeOfHighlight.Prs3d_TypeOfHighlight_Selected)
            if selection_drawer:
                selection_drawer.SetColor(red_color)
            
            # Configure LOCAL DYNAMIC (hover over sub-shapes: faces, edges, vertices) - cyan
            local_dynamic_drawer = self._context.HighlightStyle(Prs3d_TypeOfHighlight.Prs3d_TypeOfHighlight_LocalDynamic)
            if local_dynamic_drawer:
                local_dynamic_drawer.SetColor(cyan_color)
            
            # Configure LOCAL SELECTED (selected sub-shapes: faces, edges, vertices) - RED
            local_selected_drawer = self._context.HighlightStyle(Prs3d_TypeOfHighlight.Prs3d_TypeOfHighlight_LocalSelected)
            if local_selected_drawer:
                local_selected_drawer.SetColor(red_color)
                
            # Make selection more prominent
            self._context.SetToHilightSelected(True)

        except Exception as e:
            logger.error("Error configuring selection colors: %s", e, exc_info=True)

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
                
            # Reconfigure colors after mode change to ensure consistency
            self.configure_selection_colors()

        except Exception as e:
            logger.error("Error setting selection mode: %s", e, exc_info=True)

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
            logger.error("Error setting selection enabled: %s", e, exc_info=True)

    def clear(self):
        """Clear all selected entities."""
        try:
            self._context.ClearSelected(True)
        except Exception as e:
            logger.error("Error clearing selection: %s", e, exc_info=True)

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
            logger.error("Error in move_to: %s", e, exc_info=True)

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
            logger.error("Error handling selection: %s", e, exc_info=True)

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
            logger.error("Error getting selected shapes: %s", e, exc_info=True)

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
