"""
Selection Toolbar Component for OCP Widget
A reusable toolbar providing selection controls for 3D CAD entities
"""

from typing import Union, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QComboBox, QGroupBox, QFrame, QCheckBox
)
from PySide6.QtCore import Signal

from ..enums import SelectionMode


class SelectionToolbar(QWidget):
    """
    Toolbar component for controlling 3D selection settings.
    
    Signals:
        selection_mode_changed(str): Emitted when selection mode changes (volume, surface, edge, vertex)
        selection_enabled_changed(bool): Emitted when selection is enabled/disabled
        clear_selection_requested(): Emitted when clear selection button is clicked
    """
    
    # Define signals
    selection_mode_changed = Signal(str)
    selection_enabled_changed = Signal(bool)
    clear_selection_requested = Signal()
    
    def __init__(self, parent=None, orientation='horizontal'):
        """
        Initialize the selection toolbar.
        
        Args:
            parent: Parent widget
            orientation: 'horizontal' or 'vertical' layout
        """
        super().__init__(parent)
        self._orientation = orientation
        self._selection_enabled = True
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout: Union[QVBoxLayout, QHBoxLayout]
        if self._orientation == 'vertical':
            main_layout = QVBoxLayout(self)
        else:
            main_layout = QHBoxLayout(self)
        
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Selection enable/disable checkbox
        self._enable_checkbox = QCheckBox("Enable Selection")
        self._enable_checkbox.setChecked(True)
        self._enable_checkbox.toggled.connect(self._on_selection_enabled_toggled)
        main_layout.addWidget(self._enable_checkbox)
        
        # Separator
        separator = QFrame()
        if self._orientation == 'vertical':
            separator.setFrameShape(QFrame.Shape.HLine)
        else:
            separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Selection mode group
        selection_mode_group = self._create_selection_mode_group()
        main_layout.addWidget(selection_mode_group)
        
        # Separator
        separator2 = QFrame()
        if self._orientation == 'vertical':
            separator2.setFrameShape(QFrame.Shape.HLine)
        else:
            separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator2)
        
        # Actions group
        actions_group = self._create_actions_group()
        main_layout.addWidget(actions_group)
        
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
    
    def _create_actions_group(self):
        """Create action buttons group."""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        
        # Clear selection button
        clear_btn = QPushButton("Clear Selection")
        clear_btn.setToolTip("Clear all selected entities")
        clear_btn.clicked.connect(self._on_clear_selection)
        layout.addWidget(clear_btn)
        
        return group
    
    def _on_mode_combo_changed(self, index: int):
        """Handle selection mode combo box change."""
        if self._selection_enabled:
            mode_value = self._mode_combo.itemData(index)
            self.selection_mode_changed.emit(mode_value)
    
    def _on_selection_enabled_toggled(self, checked: bool):
        """Handle selection enable/disable toggle."""
        self._selection_enabled = checked
        
        # Enable/disable mode combo box
        self._mode_combo.setEnabled(checked)
        
        self.selection_enabled_changed.emit(checked)
    
    def _on_clear_selection(self):
        """Handle clear selection button click."""
        self.clear_selection_requested.emit()
    
    def get_current_mode(self) -> Optional[SelectionMode]:
        """
        Get the currently selected mode.
        
        Returns:
            Current SelectionMode or None if selection is disabled
        """
        if not self._selection_enabled:
            return None
        
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
    
    def is_selection_enabled(self) -> bool:
        """
        Check if selection is currently enabled.
        
        Returns:
            True if selection is enabled, False otherwise
        """
        return self._selection_enabled
    
    def set_selection_enabled(self, enabled: bool):
        """
        Enable or disable selection.
        
        Args:
            enabled: True to enable, False to disable
        """
        self._enable_checkbox.setChecked(enabled)
