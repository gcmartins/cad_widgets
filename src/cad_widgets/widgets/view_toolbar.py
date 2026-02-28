"""
View Toolbar Component for OCP Widget
A reusable toolbar providing view controls for 3D CAD visualization
"""

from typing import Union

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QComboBox, QGroupBox, QFrame, QLabel
)
from PySide6.QtCore import Signal

from .enums import ViewDirection, ProjectionType, DisplayMode


class ViewToolbar(QWidget):
    """
    Toolbar component for controlling 3D view settings.
    
    Signals:
        projection_changed(str): Emitted when view projection changes (top, front, iso, etc.)
        projection_type_changed(str): Emitted when projection type changes (perspective/orthographic)
        display_mode_changed(str): Emitted when display mode changes (shaded/wireframe)
        fit_all_requested(): Emitted when fit all button is clicked
        clear_requested(): Emitted when clear button is clicked
    """
    
    # Define signals
    projection_changed = Signal(str)
    projection_type_changed = Signal(str)
    display_mode_changed = Signal(str)
    fit_all_requested = Signal()
    clear_requested = Signal()
    
    def __init__(self, parent=None, orientation='horizontal'):
        """
        Initialize the view toolbar.
        
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
        if self._orientation == 'vertical':
            main_layout = QVBoxLayout(self)
        else:
            main_layout = QHBoxLayout(self)
        
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Projection type group
        proj_type_group = self._create_projection_type_group()
        main_layout.addWidget(proj_type_group)
        
        # Display mode group
        display_mode_group = self._create_display_mode_group()
        main_layout.addWidget(display_mode_group)
        
        # Separator
        separator = QFrame()
        if self._orientation == 'vertical':
            separator.setFrameShape(QFrame.Shape.HLine)
        else:
            separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        # Standard views group
        views_group = self._create_standard_views_group()
        main_layout.addWidget(views_group)
        
        # Separator
        separator2 = QFrame()
        if self._orientation == 'vertical':
            separator2.setFrameShape(QFrame.Shape.HLine)
        else:
            separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator2)
        
        # View actions
        actions_group = self._create_actions_group()
        main_layout.addWidget(actions_group)
        
        # Add stretch at the end
        main_layout.addStretch()
    
    def _create_projection_type_group(self):
        """Create the projection type control group."""
        group = QGroupBox("Projection Type")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        
        # Create combo box
        self._proj_type_combo = QComboBox()
        self._proj_type_combo.addItem(ProjectionType.PERSPECTIVE.value.capitalize(), ProjectionType.PERSPECTIVE.value)
        self._proj_type_combo.addItem(ProjectionType.ORTHOGRAPHIC.value.capitalize(), ProjectionType.ORTHOGRAPHIC.value)
        self._proj_type_combo.setCurrentIndex(0)
        self._proj_type_combo.currentIndexChanged.connect(self._on_projection_type_combo_changed)
        
        layout.addWidget(self._proj_type_combo)
        
        return group
    
    def _create_display_mode_group(self):
        """Create the display mode control group."""
        group = QGroupBox("Display Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        
        # Create combo box
        self._display_mode_combo = QComboBox()
        self._display_mode_combo.addItem(DisplayMode.SHADED.value.capitalize(), DisplayMode.SHADED.value)
        self._display_mode_combo.addItem(DisplayMode.WIREFRAME.value.capitalize(), DisplayMode.WIREFRAME.value)
        self._display_mode_combo.setCurrentIndex(0)
        self._display_mode_combo.currentIndexChanged.connect(self._on_display_mode_combo_changed)
        
        layout.addWidget(self._display_mode_combo)
        
        return group
    
    def _create_standard_views_group(self):
        """Create the standard views buttons group."""
        group = QGroupBox("Standard Views")
        layout = QVBoxLayout(group) if self._orientation == 'vertical' else QHBoxLayout(group)
        layout.setSpacing(5)
        
        # ISO view button
        btn_iso = QPushButton(ViewDirection.ISO.value.upper())
        btn_iso.setToolTip("Isometric view")
        btn_iso.clicked.connect(lambda: self._on_projection_changed(ViewDirection.ISO))
        layout.addWidget(btn_iso)
        
        # Top view button
        btn_top = QPushButton(ViewDirection.TOP.value.capitalize())
        btn_top.setToolTip("Top view (Z+)")
        btn_top.clicked.connect(lambda: self._on_projection_changed(ViewDirection.TOP))
        layout.addWidget(btn_top)
        
        # Front view button
        btn_front = QPushButton(ViewDirection.FRONT.value.capitalize())
        btn_front.setToolTip("Front view (Y-)")
        btn_front.clicked.connect(lambda: self._on_projection_changed(ViewDirection.FRONT))
        layout.addWidget(btn_front)
        
        # Right view button
        btn_right = QPushButton(ViewDirection.RIGHT.value.capitalize())
        btn_right.setToolTip("Right view (X+)")
        btn_right.clicked.connect(lambda: self._on_projection_changed(ViewDirection.RIGHT))
        layout.addWidget(btn_right)
        
        return group
    
    def _create_actions_group(self):
        """Create the view actions buttons group."""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        
        # Fit all button
        btn_fit = QPushButton("Fit All")
        btn_fit.setToolTip("Fit all objects in view")
        btn_fit.clicked.connect(self._on_fit_all_requested)
        layout.addWidget(btn_fit)
        
        # Clear button
        btn_clear = QPushButton("Clear")
        btn_clear.setToolTip("Remove all objects from view")
        btn_clear.clicked.connect(self._on_clear_requested)
        layout.addWidget(btn_clear)
        
        return group
    
    # Signal emission methods
    def _on_projection_changed(self, projection: ViewDirection):
        """Handle projection change."""
        self.projection_changed.emit(projection.value)
    
    def _on_projection_type_combo_changed(self, index: int):
        """Handle projection type combo box change."""
        proj_type_value = self._proj_type_combo.itemData(index)
        self.projection_type_changed.emit(proj_type_value)
    
    def _on_display_mode_combo_changed(self, index: int):
        """Handle display mode combo box change."""
        mode_value = self._display_mode_combo.itemData(index)
        self.display_mode_changed.emit(mode_value)
    
    def _on_fit_all_requested(self):
        """Handle fit all request."""
        self.fit_all_requested.emit()
    
    def _on_clear_requested(self):
        """Handle clear request."""
        self.clear_requested.emit()
    
    # Public methods for programmatic control
    def set_projection_type(self, proj_type: ProjectionType):
        """
        Programmatically set the projection type.
        
        Args:
            proj_type: ProjectionType enum
        """
        for i in range(self._proj_type_combo.count()):
            if self._proj_type_combo.itemData(i) == proj_type.value:
                self._proj_type_combo.setCurrentIndex(i)
                break
    
    def set_display_mode(self, mode: DisplayMode):
        """
        Programmatically set the display mode.
        
        Args:
            mode: DisplayMode enum
        """
        for i in range(self._display_mode_combo.count()):
            if self._display_mode_combo.itemData(i) == mode.value:
                self._display_mode_combo.setCurrentIndex(i)
                break
    
    def get_projection_type(self):
        """Get the current projection type."""
        return self._proj_type_combo.currentData()
    
    def get_display_mode(self):
        """Get the current display mode."""
        return self._display_mode_combo.currentData()
