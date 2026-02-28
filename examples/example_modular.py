"""
Example application demonstrating modular OCP widget with ViewToolbar
Shows various 3D shapes with a clean, modular architecture
"""

import os
import sys

os.environ["QT_LOGGING_RULES"] = "qt.qpa.theme.gnome=false"

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSplitter,
)
from PySide6.QtCore import Qt

from cad_widgets import (
    OCPWidget,
    ViewToolbar,
    SelectionToolbar,
    ViewDirection,
    ProjectionType,
    DisplayMode,
    SelectionMode,
    GeometryService,
)


class CADViewerWindow(QMainWindow):
    """Main window for the CAD viewer example using modular components."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCP PySide6 3D Viewer - Modular Example")
        self.setGeometry(100, 100, 1200, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("OCP OpenCascade 3D Viewer - Modular Architecture")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Create splitter for viewer and toolbar
        splitter = QSplitter(Qt.Horizontal)

        # Create left panel with viewer and selection toolbar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Create the OCP widget
        self.viewer = OCPWidget()
        left_layout.addWidget(self.viewer)

        # Create the selection toolbar (horizontal orientation)
        self.selection_toolbar = SelectionToolbar(orientation="horizontal")
        left_layout.addWidget(self.selection_toolbar)

        splitter.addWidget(left_panel)

        # Create the view toolbar (vertical orientation)
        self.view_toolbar = ViewToolbar(orientation="vertical")
        splitter.addWidget(self.view_toolbar)

        # Set splitter sizes (viewer takes most space)
        splitter.setSizes([900, 300])

        main_layout.addWidget(splitter)

        # Bottom control panel
        bottom_panel = self._create_bottom_panel()
        main_layout.addWidget(bottom_panel)

        # Connect toolbar signals to viewer
        self._connect_signals()

        # Set initial display mode to match toolbar state
        self.viewer.set_display_mode(DisplayMode.SHADED)

        # Load example shapes automatically
        self.load_example_shapes()

    def _create_bottom_panel(self):
        """Create the bottom control panel."""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Info label
        info_label = QLabel(
            "🖱️ Left Click: Select/Rotate | Middle Click: Pan | Scroll: Zoom | Ctrl/Shift+Click: Multi-select"
        )
        info_label.setStyleSheet("padding: 5px; color: #555;")
        layout.addWidget(info_label)

        layout.addStretch()

        # Load example button
        btn_example = QPushButton("Load Example Shapes")
        btn_example.setStyleSheet("padding: 8px 16px; font-weight: bold;")
        btn_example.clicked.connect(self.load_example_shapes)
        layout.addWidget(btn_example)

        return panel

    def _connect_signals(self):
        """Connect toolbar signals to viewer methods."""
        # Connect view toolbar signals
        self.view_toolbar.projection_changed.connect(
            lambda direction_str: self.viewer.set_projection(
                ViewDirection(direction_str)
            )
        )

        self.view_toolbar.projection_type_changed.connect(
            lambda proj_type_str: self.viewer.set_projection_type(
                ProjectionType(proj_type_str)
            )
        )

        self.view_toolbar.display_mode_changed.connect(
            lambda mode_str: self.viewer.set_display_mode(DisplayMode(mode_str))
        )

        self.view_toolbar.fit_all_requested.connect(self.viewer.fit_all)
        self.view_toolbar.clear_requested.connect(self.viewer.erase_all)

        # Connect selection toolbar signals
        self.selection_toolbar.selection_mode_changed.connect(
            lambda mode_str: self.viewer.set_selection_mode(SelectionMode(mode_str))
        )

        self.selection_toolbar.selection_enabled_changed.connect(
            self.viewer.set_selection_enabled
        )

        self.selection_toolbar.clear_selection_requested.connect(
            self.viewer.clear_selection
        )

    def load_example_shapes(self):
        """Load example 3D shapes into the viewer."""
        # Clear existing shapes
        self.viewer.erase_all()

        # Create a geometry service for shape creation
        geo = GeometryService()

        # Create and display various shapes

        # 1. Box at origin
        box = geo.create_box(50, 50, 50)
        self.viewer.display_shape(box, color=(0.7, 0.2, 0.2), update=False)

        # 2. Sphere
        sphere = geo.create_sphere(30)
        sphere_translated = geo.translate_shape(sphere, 100, 0, 25)
        self.viewer.display_shape(
            sphere_translated, color=(0.2, 0.7, 0.2), update=False
        )

        # 3. Cylinder
        cylinder = geo.create_cylinder(
            20, 60, position=(0, 100, 0), direction=(0, 0, 1)
        )
        self.viewer.display_shape(cylinder, color=(0.2, 0.2, 0.7), update=False)

        # 4. Cone
        cone = geo.create_cone(30, 5, 70, position=(100, 100, 0), direction=(0, 0, 1))
        self.viewer.display_shape(cone, color=(0.7, 0.7, 0.2), update=False)

        # 5. Torus
        torus = geo.create_torus(25, 10, position=(-80, 0, 30), direction=(0, 1, 0))
        self.viewer.display_shape(torus, color=(0.7, 0.2, 0.7), update=False)

        # 6. Transparent box
        box2 = geo.create_box(40, 40, 80, position=(-80, -80, 0))
        self.viewer.display_shape(
            box2, color=(0.2, 0.7, 0.7), transparency=0.6, update=False
        )

        # Fit all shapes in view
        self.viewer.fit_all()

        # Initialize selection mode
        self.viewer.set_selection_mode(SelectionMode.VOLUME)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = CADViewerWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
