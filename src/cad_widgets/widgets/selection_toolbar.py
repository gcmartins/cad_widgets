"""
Selection Toolbar Component for OCP Widget
A reusable toolbar providing selection controls for 3D CAD entities
"""

from typing import Union, Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QGroupBox,
)
from PySide6.QtCore import Signal

from ..enums import SelectionMode


class SelectionToolbar(QWidget):
    """
    Toolbar component for controlling 3D selection settings.

    Signals:
        selection_mode_changed(str): Emitted when selection mode changes (volume, surface, edge, vertex)
    """

    # Define signals
    selection_mode_changed = Signal(str)

    def __init__(self, parent=None, orientation="horizontal"):
        """
        Initialize the selection toolbar.

        Args:
            parent: Parent widget
            orientation: 'horizontal' or 'vertical' layout
        """
        super().__init__(parent)
        self._orientation = orientation
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout: Union[QVBoxLayout, QHBoxLayout]
        if self._orientation == "vertical":
            main_layout = QVBoxLayout(self)
        else:
            main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(5, 5, 5, 5)

        # Selection mode group
        selection_mode_group = self._create_selection_mode_group()
        main_layout.addWidget(selection_mode_group)

        # Add stretch at the end
        main_layout.addStretch()

    def _create_selection_mode_group(self):
        """Create the selection mode control group."""
        group = QGroupBox("Selection Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        # Create combo box for selection modes
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Volumes", SelectionMode.VOLUME.value)
        self._mode_combo.addItem("Surfaces", SelectionMode.SURFACE.value)
        self._mode_combo.addItem("Edges", SelectionMode.EDGE.value)
        self._mode_combo.addItem("Vertices", SelectionMode.VERTEX.value)
        self._mode_combo.setCurrentIndex(0)

        # Set tooltips for the combo box
        self._mode_combo.setToolTip("Select entity type to pick")

        # Connect signal
        self._mode_combo.currentIndexChanged.connect(self._on_mode_combo_changed)

        layout.addWidget(self._mode_combo)

        return group

    def _on_mode_combo_changed(self, index: int):
        """Handle selection mode combo box change."""
        mode_value = self._mode_combo.itemData(index)
        self.selection_mode_changed.emit(mode_value)

    def get_current_mode(self) -> Optional[SelectionMode]:
        """
        Get the currently selected mode.

        Returns:
            Current SelectionMode
        """
        mode_value = self._mode_combo.currentData()

        # Map string value back to enum
        for mode in SelectionMode:
            if mode.value == mode_value:
                return mode

        return SelectionMode.VOLUME  # Default

    def set_mode(self, mode: SelectionMode):
        """
        Set the selection mode programmatically.

        Args:
            mode: SelectionMode to set
        """
        for i in range(self._mode_combo.count()):
            if self._mode_combo.itemData(i) == mode.value:
                self._mode_combo.setCurrentIndex(i)
                break
