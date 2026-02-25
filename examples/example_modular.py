"""
Example application demonstrating modular OCP widget with ViewToolbar
Shows various 3D shapes with a clean, modular architecture
"""

import os
import sys

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.theme.gnome=false'

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QSplitter
)
from PySide6.QtCore import Qt

from cad_widgets import OCPWidget, ViewToolbar, ViewDirection, ProjectionType, DisplayMode
from cad_widgets.utils import create_box, create_sphere, create_cylinder, create_cone, create_torus, translate_shape

from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir


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
        
        # Create the OCP widget
        self.viewer = OCPWidget()
        splitter.addWidget(self.viewer)
        
        # Create the view toolbar (vertical orientation)
        self.toolbar = ViewToolbar(orientation='vertical')
        splitter.addWidget(self.toolbar)
        
        # Set splitter sizes (viewer takes most space)
        splitter.setSizes([900, 300])
        
        main_layout.addWidget(splitter)

        # Bottom control panel
        bottom_panel = self._create_bottom_panel()
        main_layout.addWidget(bottom_panel)

        # Connect toolbar signals to viewer
        self._connect_signals()

        # Load example shapes automatically
        self.load_example_shapes()

    def _create_bottom_panel(self):
        """Create the bottom control panel."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Info label
        info_label = QLabel("🖱️ Left Click: Rotate | Middle Click: Pan | Scroll: Zoom")
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
        # Connect projection changes (convert string to enum)
        self.toolbar.projection_changed.connect(
            lambda direction_str: self.viewer.set_projection(ViewDirection(direction_str))
        )
        
        # Connect projection type changes (convert string to enum)
        self.toolbar.projection_type_changed.connect(
            lambda proj_type_str: self.viewer.set_projection_type(ProjectionType(proj_type_str))
        )
        
        # Connect display mode changes (convert string to enum)
        self.toolbar.display_mode_changed.connect(
            lambda mode_str: self.viewer.set_display_mode(DisplayMode(mode_str))
        )
        
        # Connect actions
        self.toolbar.fit_all_requested.connect(self.viewer.fit_all)
        self.toolbar.clear_requested.connect(self.viewer.erase_all)

    def load_example_shapes(self):
        """Load example 3D shapes into the viewer."""
        # Clear existing shapes
        self.viewer.erase_all()

        # Create and display various shapes using utility functions
        
        # 1. Box at origin
        box = create_box(50, 50, 50)
        self.viewer.display_shape(box, color=(0.7, 0.2, 0.2), update=False)

        # 2. Sphere
        sphere = create_sphere(30)
        sphere_translated = translate_shape(sphere, 100, 0, 25)
        self.viewer.display_shape(sphere_translated, color=(0.2, 0.7, 0.2), update=False)

        # 3. Cylinder
        axis = gp_Ax2(gp_Pnt(0, 100, 0), gp_Dir(0, 0, 1))
        cylinder = create_cylinder(20, 60, axis)
        self.viewer.display_shape(cylinder, color=(0.2, 0.2, 0.7), update=False)

        # 4. Cone
        cone_axis = gp_Ax2(gp_Pnt(100, 100, 0), gp_Dir(0, 0, 1))
        cone = create_cone(30, 5, 70, cone_axis)
        self.viewer.display_shape(cone, color=(0.7, 0.7, 0.2), update=False)

        # 5. Torus
        torus_axis = gp_Ax2(gp_Pnt(-80, 0, 30), gp_Dir(0, 1, 0))
        torus = create_torus(25, 10, torus_axis)
        self.viewer.display_shape(torus, color=(0.7, 0.2, 0.7), update=False)

        # 6. Transparent box
        box2 = create_box(40, 40, 80, gp_Pnt(-80, -80, 0))
        self.viewer.display_shape(box2, color=(0.2, 0.7, 0.7), transparency=0.6, update=False)

        # Fit all shapes in view
        self.viewer.fit_all()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = CADViewerWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
