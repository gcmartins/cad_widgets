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
    QSizePolicy,
)
from PySide6.QtCore import Qt

from cad_widgets import (
    OCPWidget,
    ViewToolbar,
    SelectionToolbar,
    GeometryTreeWidget,
    PropertyEditorWidget,
    ViewDirection,
    ProjectionType,
    DisplayMode,
    SelectionMode,
    ShapeType,
    GeometryManager,
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
    Translation,
    Rotation,
)


class CADViewerWindow(QMainWindow):
    """Main window for the CAD viewer example using modular components."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCP PySide6 3D Viewer - Modular Example")
        self.setGeometry(100, 100, 1400, 700)

        # Create geometry manager
        self.geometry_manager = GeometryManager()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create splitter for left panel and main viewer area
        splitter = QSplitter(Qt.Horizontal)

        # Create left panel with geometry tree and property editor
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Add geometry tree widget
        self.geometry_tree = GeometryTreeWidget()
        left_layout.addWidget(self.geometry_tree, stretch=1)

        # Add property editor widget
        self.property_editor = PropertyEditorWidget()
        left_layout.addWidget(self.property_editor, stretch=1)

        splitter.addWidget(left_panel)

        # Create right panel with toolbars and viewer stacked vertically
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal layout for toolbars side by side
        toolbars_layout = QHBoxLayout()
        
        # Create the view toolbar (horizontal orientation)
        self.view_toolbar = ViewToolbar(orientation="horizontal", show_projection_type=False)
        self.view_toolbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.view_toolbar.setMaximumHeight(self.view_toolbar.sizeHint().height())
        toolbars_layout.addWidget(self.view_toolbar)

        # Create the selection toolbar (horizontal orientation)
        self.selection_toolbar = SelectionToolbar(orientation="horizontal")
        self.selection_toolbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.selection_toolbar.setMaximumHeight(self.selection_toolbar.sizeHint().height())
        toolbars_layout.addWidget(self.selection_toolbar)
        
        toolbars_layout.addStretch()  # Push toolbars to the left
        
        right_layout.addLayout(toolbars_layout)

        # Create the OCP widget below toolbars
        self.viewer = OCPWidget()
        right_layout.addWidget(self.viewer)

        splitter.addWidget(right_panel)

        # Set main splitter sizes (left panel width, right panel width)
        splitter.setSizes([350, 1050])

        main_layout.addWidget(splitter)

        # Connect toolbar signals to viewer
        self._connect_signals()

        # Set initial display mode to match toolbar state
        self.viewer.set_display_mode(DisplayMode.SHADED)

        # Load example shapes automatically
        self.load_example_shapes()

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

        # Connect geometry tree signals
        self.geometry_tree.shape_visibility_changed.connect(
            self._on_shape_visibility_changed
        )
        self.geometry_tree.shape_selected.connect(self._on_shape_selected)
        self.geometry_tree.shape_creation_requested.connect(
            self._on_shape_creation_requested
        )
        self.geometry_tree.shape_deleted.connect(
            self._on_shape_deleted
        )
        self.geometry_tree.shapes_union_requested.connect(
            self._on_shapes_union_requested
        )
        self.geometry_tree.shapes_subtract_requested.connect(
            self._on_shapes_subtract_requested
        )

        # Connect property editor signals
        self.property_editor.properties_changed.connect(self._on_properties_changed)
        
        # Connect geometry manager signals to components
        self.geometry_manager.shape_created.connect(self.viewer.on_shape_created)
        self.geometry_manager.shape_created.connect(self.geometry_tree.on_shape_created)
        self.geometry_manager.shape_updated.connect(self.viewer.on_shape_updated)
        self.geometry_manager.shape_updated.connect(self.geometry_tree.on_shape_updated)
        self.geometry_manager.shape_removed.connect(self.viewer.on_shape_removed)
        self.geometry_manager.shape_removed.connect(self.geometry_tree.on_shape_removed)
        self.geometry_manager.all_cleared.connect(self.viewer.on_all_cleared)
        self.geometry_manager.all_cleared.connect(self.geometry_tree.on_all_cleared)
        self.geometry_manager.all_cleared.connect(self.property_editor.clear_shape)

    def _on_shape_visibility_changed(self, shape_id: str, visible: bool):
        """Handle shape visibility changes from the geometry tree."""
        self.viewer.set_shape_visibility(shape_id, visible)

    def _on_shape_selected(self, shape_id: str):
        """Handle shape selection in the tree."""
        managed_shape = self.geometry_manager.get_shape(shape_id)
        if managed_shape:
            self.property_editor.set_shape(
                shape_id,
                managed_shape.shape_type,
                managed_shape.properties.to_dict()
            )
    
    def _on_shape_creation_requested(self, shape_type: ShapeType):
        """
        Handle shape creation request from context menu.
        Creates a new shape with default properties.
        
        Args:
            shape_type: Type of shape to create
        """
        import uuid
        
        # Generate unique ID
        shape_id = f"{shape_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Default fixed color (light gray-blue)
        color = (0.7, 0.75, 0.8)
        
        # Create properties based on shape type (using defaults)
        properties_map = {
            ShapeType.BOX: BoxProperties(),
            ShapeType.SPHERE: SphereProperties(),
            ShapeType.CYLINDER: CylinderProperties(),
            ShapeType.CONE: ConeProperties(),
            ShapeType.TORUS: TorusProperties(),
        }
        
        properties = properties_map.get(shape_type, BoxProperties())
        
        # Create shape name
        shape_name = f"{shape_type.value.title()} {len(self.geometry_manager._shapes) + 1}"
        
        # Create the shape via geometry manager
        self.geometry_manager.create_shape(
            shape_id=shape_id,
            shape_type=shape_type,
            name=shape_name,
            color=color,
            properties=properties
        )
    
    def _on_shape_deleted(self, shape_id: str):
        """
        Handle shape deletion request from context menu.
        
        Args:
            shape_id: ID of the shape to delete
        """
        # Remove shape via geometry manager (this will emit shape_removed signal)
        self.geometry_manager.remove_shape(shape_id)
        
        # Clear property editor if this shape was being edited
        self.property_editor.clear_shape()

    def _on_properties_changed(self, shape_id: str, properties_dict: dict):
        """Handle property changes from the editor."""
        managed_shape = self.geometry_manager.get_shape(shape_id)
        if not managed_shape:
            return

        try:
            # Convert dict to properties object
            properties = self.geometry_manager.properties_from_dict(
                managed_shape.shape_type,
                properties_dict
            )
            
            # Update the shape (this will emit shape_updated signal)
            self.geometry_manager.update_shape(shape_id, properties)

        except Exception as e:
            print(f"Failed to update shape properties: {e}")

    def _on_clear_all(self):
        """Handle clear all request from UI."""
        self.geometry_manager.clear_all()  # This will emit all_cleared signal

    def _on_shapes_union_requested(self, shape_ids: list):
        """
        Handle union request from geometry tree.
        
        Args:
            shape_ids: List of shape IDs to union
        """
        result_id = self.geometry_manager.union_shapes(shape_ids)
        if result_id:
            # Fit view to show result
            self.viewer.fit_all()
            # Clear property editor since original shapes are removed
            self.property_editor.clear_shape()
        else:
            print("Union operation failed")

    def _on_shapes_subtract_requested(self, shape_ids: list):
        """
        Handle subtract request from geometry tree.
        
        Args:
            shape_ids: List of shape IDs (first is base, rest subtracted)
        """
        result_id = self.geometry_manager.subtract_shapes(shape_ids)
        if result_id:
            # Fit view to show result
            self.viewer.fit_all()
            # Clear property editor since original shapes are removed
            self.property_editor.clear_shape()
        else:
            print("Subtract operation failed")

    def load_example_shapes(self):
        """Load example 3D shapes into the viewer."""
        # Clear existing shapes
        self._on_clear_all()

        # Create shapes - signals will automatically update viewer and tree

        # 1. Box at origin
        self.geometry_manager.create_shape(
            shape_id="box_1",
            shape_type=ShapeType.BOX,
            name="Red Box",
            color=(0.7, 0.2, 0.2),
            properties=BoxProperties(
                width=50, height=50, depth=50,
                translation=Translation(x=0, y=0, z=0),
                rotation=Rotation(x=0, y=0, z=0)
            )
        )

        # 2. Sphere
        self.geometry_manager.create_shape(
            shape_id="sphere_1",
            shape_type=ShapeType.SPHERE,
            name="Green Sphere",
            color=(0.2, 0.7, 0.2),
            properties=SphereProperties(
                radius=30,
                translation=Translation(x=100, y=0, z=25),
                rotation=Rotation(x=0, y=0, z=0)
            )
        )

        # 3. Cylinder
        self.geometry_manager.create_shape(
            shape_id="cylinder_1",
            shape_type=ShapeType.CYLINDER,
            name="Blue Cylinder",
            color=(0.2, 0.2, 0.7),
            properties=CylinderProperties(
                radius=20, height=60,
                translation=Translation(x=0, y=100, z=0),
                rotation=Rotation(x=0, y=0, z=0)
            )
        )

        # 4. Cone
        self.geometry_manager.create_shape(
            shape_id="cone_1",
            shape_type=ShapeType.CONE,
            name="Yellow Cone",
            color=(0.7, 0.7, 0.2),
            properties=ConeProperties(
                radius=30, height=70,
                translation=Translation(x=100, y=100, z=0),
                rotation=Rotation(x=0, y=0, z=0)
            )
        )

        # 5. Torus
        self.geometry_manager.create_shape(
            shape_id="torus_1",
            shape_type=ShapeType.TORUS,
            name="Magenta Torus",
            color=(0.7, 0.2, 0.7),
            properties=TorusProperties(
                radius=25, length=10,
                translation=Translation(x=-80, y=0, z=30),
                rotation=Rotation(x=0, y=90, z=0)
            )
        )

        # 6. Transparent box
        self.geometry_manager.create_shape(
            shape_id="box_2",
            shape_type=ShapeType.BOX,
            name="Cyan Box (Transparent)",
            color=(0.2, 0.7, 0.7),
            properties=BoxProperties(
                width=40, height=40, depth=80,
                translation=Translation(x=-80, y=-80, z=0),
                rotation=Rotation(x=0, y=0, z=0)
            ),
            transparency=0.6
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