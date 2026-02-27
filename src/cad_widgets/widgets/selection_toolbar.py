"""
Selection Toolbar Component for OCP Widget
A reusable toolbar providing selection controls for 3D CAD entities
"""

from typing import Union, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QRadioButton, QGroupBox, QFrame, QCheckBox
)
from PySide6.QtCore import Signal

from .enums import SelectionMode


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
        
        # Create button group for mutually exclusive selection
        self._mode_button_group = QButtonGroup(self)
        
        # Volume selection
        self._volume_radio = QRadioButton("Volumes")
        self._volume_radio.setToolTip("Select solid volumes/bodies")
        self._volume_radio.setChecked(True)
        self._mode_button_group.addButton(self._volume_radio)
        layout.addWidget(self._volume_radio)
        
        # Surface selection
        self._surface_radio = QRadioButton("Surfaces")
        self._surface_radio.setToolTip("Select faces/surfaces")
        self._mode_button_group.addButton(self._surface_radio)
        layout.addWidget(self._surface_radio)
        
        # Edge selection
        self._edge_radio = QRadioButton("Edges")
        self._edge_radio.setToolTip("Select edges")
        self._mode_button_group.addButton(self._edge_radio)
        layout.addWidget(self._edge_radio)
        
        # Vertex selection
        self._vertex_radio = QRadioButton("Vertices")
        self._vertex_radio.setToolTip("Select vertices/points")
        self._mode_button_group.addButton(self._vertex_radio)
        layout.addWidget(self._vertex_radio)
        
        # Connect signals
        self._volume_radio.toggled.connect(lambda checked: 
            self._on_mode_changed(SelectionMode.VOLUME) if checked else None)
        self._surface_radio.toggled.connect(lambda checked: 
            self._on_mode_changed(SelectionMode.SURFACE) if checked else None)
        self._edge_radio.toggled.connect(lambda checked: 
            self._on_mode_changed(SelectionMode.EDGE) if checked else None)
        self._vertex_radio.toggled.connect(lambda checked: 
            self._on_mode_changed(SelectionMode.VERTEX) if checked else None)
        
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
    
    def _on_mode_changed(self, mode: SelectionMode):
        """Handle selection mode change."""
        if self._selection_enabled:
            self.selection_mode_changed.emit(mode.value)
    
    def _on_selection_enabled_toggled(self, checked: bool):
        """Handle selection enable/disable toggle."""
        self._selection_enabled = checked
        
        # Enable/disable mode buttons
        self._volume_radio.setEnabled(checked)
        self._surface_radio.setEnabled(checked)
        self._edge_radio.setEnabled(checked)
        self._vertex_radio.setEnabled(checked)
        
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
        
        if self._volume_radio.isChecked():
            return SelectionMode.VOLUME
        elif self._surface_radio.isChecked():
            return SelectionMode.SURFACE
        elif self._edge_radio.isChecked():
            return SelectionMode.EDGE
        elif self._vertex_radio.isChecked():
            return SelectionMode.VERTEX
        
        return SelectionMode.VOLUME  # Default
    
    def set_mode(self, mode: SelectionMode):
        """
        Set the selection mode programmatically.
        
        Args:
            mode: SelectionMode to set
        """
        if mode == SelectionMode.VOLUME:
            self._volume_radio.setChecked(True)
        elif mode == SelectionMode.SURFACE:
            self._surface_radio.setChecked(True)
        elif mode == SelectionMode.EDGE:
            self._edge_radio.setChecked(True)
        elif mode == SelectionMode.VERTEX:
            self._vertex_radio.setChecked(True)
    
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
