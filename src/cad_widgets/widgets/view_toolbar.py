"""
View Toolbar Component for OCP Widget
A reusable toolbar providing view controls for 3D CAD visualization
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QButtonGroup, QRadioButton, QGroupBox, QFrame
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
            separator.setFrameShape(QFrame.HLine)
        else:
            separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Standard views group
        views_group = self._create_standard_views_group()
        main_layout.addWidget(views_group)
        
        # Separator
        separator2 = QFrame()
        if self._orientation == 'vertical':
            separator2.setFrameShape(QFrame.HLine)
        else:
            separator2.setFrameShape(QFrame.VLine)
        separator2.setFrameShadow(QFrame.Sunken)
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
        
        self._proj_type_btn_group = QButtonGroup(self)
        
        # Perspective radio button
        perspective_btn = QRadioButton(ProjectionType.PERSPECTIVE.value.capitalize())
        perspective_btn.setChecked(True)
        perspective_btn.toggled.connect(
            lambda checked: self._on_projection_type_changed(ProjectionType.PERSPECTIVE) if checked else None
        )
        self._proj_type_btn_group.addButton(perspective_btn)
        layout.addWidget(perspective_btn)
        
        # Orthographic radio button
        ortho_btn = QRadioButton(ProjectionType.ORTHOGRAPHIC.value.capitalize())
        ortho_btn.toggled.connect(
            lambda checked: self._on_projection_type_changed(ProjectionType.ORTHOGRAPHIC) if checked else None
        )
        self._proj_type_btn_group.addButton(ortho_btn)
        layout.addWidget(ortho_btn)
        
        return group
    
    def _create_display_mode_group(self):
        """Create the display mode control group."""
        group = QGroupBox("Display Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)
        
        self._display_mode_btn_group = QButtonGroup(self)
        
        # Shaded radio button
        shaded_btn = QRadioButton(DisplayMode.SHADED.value.capitalize())
        shaded_btn.setChecked(True)
        shaded_btn.toggled.connect(
            lambda checked: self._on_display_mode_changed(DisplayMode.SHADED) if checked else None
        )
        self._display_mode_btn_group.addButton(shaded_btn)
        layout.addWidget(shaded_btn)
        
        # Wireframe radio button
        wireframe_btn = QRadioButton(DisplayMode.WIREFRAME.value.capitalize())
        wireframe_btn.toggled.connect(
            lambda checked: self._on_display_mode_changed(DisplayMode.WIREFRAME) if checked else None
        )
        self._display_mode_btn_group.addButton(wireframe_btn)
        layout.addWidget(wireframe_btn)
        
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
    
    def _on_projection_type_changed(self, proj_type: ProjectionType):
        """Handle projection type change."""
        self.projection_type_changed.emit(proj_type.value)
    
    def _on_display_mode_changed(self, mode: DisplayMode):
        """Handle display mode change."""
        self.display_mode_changed.emit(mode.value)
    
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
        for button in self._proj_type_btn_group.buttons():
            if proj_type.value in button.text().lower():
                button.setChecked(True)
                break
    
    def set_display_mode(self, mode: DisplayMode):
        """
        Programmatically set the display mode.
        
        Args:
            mode: DisplayMode enum
        """
        for button in self._display_mode_btn_group.buttons():
            if mode.value in button.text().lower():
                button.setChecked(True)
                break
    
    def get_projection_type(self):
        """Get the current projection type."""
        for button in self._proj_type_btn_group.buttons():
            if button.isChecked():
                return button.text().lower()
        return 'perspective'
    
    def get_display_mode(self):
        """Get the current display mode."""
        for button in self._display_mode_btn_group.buttons():
            if button.isChecked():
                return button.text().lower()
        return 'shaded'
