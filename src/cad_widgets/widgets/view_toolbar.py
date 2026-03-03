"""
View Toolbar Component for OCP Widget
A reusable toolbar providing view controls for 3D CAD visualization
"""

from typing import Union

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QGroupBox,
    QFrame,
    QSlider,
    QLabel,
)
from PySide6.QtCore import Signal, Qt

from cad_widgets.enums import ViewDirection, ProjectionType, DisplayMode


class ViewToolbar(QWidget):
    """
    Toolbar component for controlling 3D view settings.

    Signals:
        projection_changed(str): Emitted when view projection changes (top, front, iso, etc.)
        projection_type_changed(str): Emitted when projection type changes (perspective/orthographic)
        display_mode_changed(str): Emitted when display mode changes (shaded/wireframe)
        transparency_changed(float): Emitted when global transparency changes (0.0-1.0)
        fit_all_requested(): Emitted when fit all button is clicked
        clear_requested(): Emitted when clear button is clicked
    """

    # Define signals
    projection_changed = Signal(str)
    projection_type_changed = Signal(str)
    display_mode_changed = Signal(str)
    transparency_changed = Signal(float)
    fit_all_requested = Signal()

    def __init__(self, parent=None, orientation="horizontal", show_projection_type=True):
        """
        Initialize the view toolbar.

        Args:
            parent: Parent widget
            orientation: 'horizontal' or 'vertical' layout
            show_projection_type: Whether to show projection type selector (default: True)
        """
        super().__init__(parent)
        self._orientation = orientation
        self._show_projection_type = show_projection_type
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

        # Projection type group (optional)
        if self._show_projection_type:
            proj_type_group = self._create_projection_type_group()
            main_layout.addWidget(proj_type_group)

        # Display mode group
        display_mode_group = self._create_display_mode_group()
        main_layout.addWidget(display_mode_group)

        # Transparency group
        transparency_group = self._create_transparency_group()
        main_layout.addWidget(transparency_group)

        # Separator
        separator = QFrame()
        if self._orientation == "vertical":
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
        if self._orientation == "vertical":
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
        self._proj_type_combo.addItem(
            ProjectionType.PERSPECTIVE.value.capitalize(),
            ProjectionType.PERSPECTIVE.value,
        )
        self._proj_type_combo.addItem(
            ProjectionType.ORTHOGRAPHIC.value.capitalize(),
            ProjectionType.ORTHOGRAPHIC.value,
        )
        self._proj_type_combo.setCurrentIndex(1)  # Default to Orthographic
        self._proj_type_combo.currentIndexChanged.connect(
            self._on_projection_type_combo_changed
        )

        layout.addWidget(self._proj_type_combo)

        return group

    def _create_display_mode_group(self):
        """Create the display mode control group."""
        group = QGroupBox("Display Mode")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        # Create combo box
        self._display_mode_combo = QComboBox()
        self._display_mode_combo.addItem(
            DisplayMode.SHADED.value.capitalize(), DisplayMode.SHADED.value
        )
        self._display_mode_combo.addItem(
            DisplayMode.WIREFRAME.value.capitalize(), DisplayMode.WIREFRAME.value
        )
        self._display_mode_combo.setCurrentIndex(0)
        self._display_mode_combo.currentIndexChanged.connect(
            self._on_display_mode_combo_changed
        )

        layout.addWidget(self._display_mode_combo)

        return group

    def _create_transparency_group(self):
        """Create the transparency control group."""
        group = QGroupBox("Transparency")
        layout = QVBoxLayout(group)
        layout.setSpacing(5)

        # Create label
        self._transparency_label = QLabel("0%")
        self._transparency_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._transparency_label)

        # Create slider
        self._transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self._transparency_slider.setMinimum(0)
        self._transparency_slider.setMaximum(100)
        self._transparency_slider.setValue(0)
        self._transparency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._transparency_slider.setTickInterval(10)
        self._transparency_slider.valueChanged.connect(self._on_transparency_changed)
        layout.addWidget(self._transparency_slider)

        return group

    def _create_standard_views_group(self):
        """Create the standard views buttons group."""
        group = QGroupBox("Standard Views")
        layout = (
            QVBoxLayout(group)
            if self._orientation == "vertical"
            else QHBoxLayout(group)
        )
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
        btn_front.clicked.connect(
            lambda: self._on_projection_changed(ViewDirection.FRONT)
        )
        layout.addWidget(btn_front)

        # Right view button
        btn_right = QPushButton(ViewDirection.RIGHT.value.capitalize())
        btn_right.setToolTip("Right view (X+)")
        btn_right.clicked.connect(
            lambda: self._on_projection_changed(ViewDirection.RIGHT)
        )
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

    def _on_transparency_changed(self, value: int):
        """Handle transparency slider change."""
        transparency = value / 100.0
        self._transparency_label.setText(f"{value}%")
        self.transparency_changed.emit(transparency)

    def _on_fit_all_requested(self):
        """Handle fit all request."""
        self.fit_all_requested.emit()

    # Public methods for programmatic control
    def set_projection_type(self, proj_type: ProjectionType):
        """
        Programmatically set the projection type.

        Args:
            proj_type: ProjectionType enum
        """
        if not self._show_projection_type:
            return  # No-op when projection type selector is not shown
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
        if not self._show_projection_type:
            return ProjectionType.ORTHOGRAPHIC.value  # Default when not shown
        return self._proj_type_combo.currentData()

    def get_display_mode(self):
        """Get the current display mode."""
        return self._display_mode_combo.currentData()

    def set_transparency(self, transparency: float):
        """
        Programmatically set the transparency.

        Args:
            transparency: Float 0-1 for transparency
        """
        value = int(transparency * 100)
        self._transparency_slider.setValue(value)

    def get_transparency(self) -> float:
        """Get the current transparency as a float 0-1."""
        return self._transparency_slider.value() / 100.0
