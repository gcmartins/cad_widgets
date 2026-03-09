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
    QSplitter,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
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
    GeometryService,
    BoxProperties,
    SphereProperties,
    CylinderProperties,
    ConeProperties,
    TorusProperties,
    ImportedProperties,
    Translation,
    Rotation,
)


class CADViewerWindow(QMainWindow):
    """Main window for the CAD viewer example using modular components."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCP PySide6 3D Viewer - Modular Example")
        self.setGeometry(100, 100, 1400, 700)

        self.geometry_manager = GeometryManager()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._create_left_panel())
        splitter.addWidget(self._create_right_panel())
        splitter.setSizes([350, 1050])

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        QVBoxLayout(central_widget).addWidget(splitter)

        self._connect_signals()

        # Set initial display mode to match toolbar state
        self.viewer.set_display_mode(DisplayMode.SHADED)

        # Load example shapes automatically
        self.load_example_shapes()

    def _create_left_panel(self) -> QWidget:
        """Build the left panel containing the geometry tree and property editor."""
        self.geometry_tree = GeometryTreeWidget()
        self.property_editor = PropertyEditorWidget()

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.geometry_tree, stretch=1)
        layout.addWidget(self.property_editor, stretch=1)
        return panel

    def _create_right_panel(self) -> QWidget:
        """Build the right panel containing the toolbars and the 3D viewer."""
        self.view_toolbar = ViewToolbar(orientation="horizontal", show_projection_type=False)
        self.view_toolbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.view_toolbar.setMaximumHeight(self.view_toolbar.sizeHint().height())

        self.selection_toolbar = SelectionToolbar(orientation="horizontal")
        self.selection_toolbar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.selection_toolbar.setMaximumHeight(self.selection_toolbar.sizeHint().height())

        toolbars_layout = QHBoxLayout()
        toolbars_layout.addWidget(self.view_toolbar)
        toolbars_layout.addWidget(self.selection_toolbar)
        toolbars_layout.addStretch()

        self.viewer = OCPWidget()
        self.viewer.set_background_gradient((0.4, 0.4, 0.4), (0.05, 0.05, 0.05))

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(toolbars_layout)
        layout.addWidget(self.viewer)
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

        self.view_toolbar.transparency_changed.connect(
            self.viewer.set_global_transparency
        )

        self.view_toolbar.fit_all_requested.connect(self.viewer.fit_all)

        # Connect selection toolbar signals
        self.selection_toolbar.selection_mode_changed.connect(
            lambda mode_str: self.viewer.set_selection_mode(SelectionMode(mode_str))
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
        self.geometry_tree.export_step_requested.connect(
            self._on_export_step_requested
        )
        self.geometry_tree.export_iges_requested.connect(
            self._on_export_iges_requested
        )
        self.geometry_tree.import_requested.connect(
            self._on_import_requested
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
                managed_shape.name,
                managed_shape.properties.to_dict()
            )
    
    def _on_shape_creation_requested(self, shape_type: ShapeType):
        """
        Handle shape creation request from context menu.
        Creates a new shape with default properties.
        
        Args:
            shape_type: Type of shape to create
        """
        
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
        
        # Create the shape via geometry manager (name will be auto-generated)
        self.geometry_manager.create_shape(
            shape_type=shape_type,
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

    def _on_export_step_requested(self, shape_id: str):
        """
        Handle STEP export request for a shape.
        
        Args:
            shape_id: ID of the shape to export
        """
        managed_shape = self.geometry_manager.get_shape(shape_id)
        if not managed_shape:
            QMessageBox.warning(self, "Export Error", "Shape not found")
            return
        
        # Show file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export STEP File",
            f"{managed_shape.name}.step",
            "STEP Files (*.step *.stp);;All Files (*)"
        )
        
        if filename:
            # Ensure file has extension
            if not filename.lower().endswith(('.step', '.stp')):
                filename += '.step'
            
            # Export using GeometryService
            geo_service = GeometryService()
            success = geo_service.export_step(managed_shape.shape, filename)
            
            if success:
                QMessageBox.information(self, "Export Success", f"Shape exported to {filename}")
            else:
                QMessageBox.critical(self, "Export Error", f"Failed to export shape to {filename}")

    def _on_export_iges_requested(self, shape_id: str):
        """
        Handle IGES export request for a shape.
        
        Args:
            shape_id: ID of the shape to export
        """
        managed_shape = self.geometry_manager.get_shape(shape_id)
        if not managed_shape:
            QMessageBox.warning(self, "Export Error", "Shape not found")
            return
        
        # Show file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export IGES File",
            f"{managed_shape.name}.iges",
            "IGES Files (*.iges *.igs);;All Files (*)"
        )
        
        if filename:
            # Ensure file has extension
            if not filename.lower().endswith(('.iges', '.igs')):
                filename += '.iges'
            
            # Export using GeometryService
            geo_service = GeometryService()
            success = geo_service.export_iges(managed_shape.shape, filename)
            
            if success:
                QMessageBox.information(self, "Export Success", f"Shape exported to {filename}")
            else:
                QMessageBox.critical(self, "Export Error", f"Failed to export shape to {filename}")

    def _on_import_requested(self):
        """Handle import request for STEP or IGES files."""
        # Show file dialog that accepts both STEP and IGES
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import CAD File",
            "",
            "CAD Files (*.step *.stp *.iges *.igs);;STEP Files (*.step *.stp);;IGES Files (*.iges *.igs);;All Files (*)"
        )
        
        if filename:
            # Import using unified import_shape method (automatically detects format)
            # Name will be auto-generated as "Imported_1", "Imported_2", etc.
            managed_shape = self.geometry_manager.import_shape(
                filename=filename,
                color=(0.6, 0.6, 0.7),
                properties=ImportedProperties()
            )
            
            if managed_shape:
                self.viewer.fit_all()
                QMessageBox.information(self, "Import Success", f"Shape imported from {filename}")
            else:
                QMessageBox.critical(self, "Import Error", f"Failed to import shape from {filename}")


    def load_example_shapes(self):
        """Load example 3D shapes into the viewer."""
        # Clear existing shapes
        self._on_clear_all()

        # Create shapes - signals will automatically update viewer and tree

        # 1. Box at origin
        self.geometry_manager.create_shape(
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
            shape_type=ShapeType.CONE,
            name="Yellow Cone",
            color=(0.7, 0.7, 0.2),
            properties=ConeProperties(
                base_radius=30, top_radius=10, height=70,
                translation=Translation(x=100, y=100, z=0),
                rotation=Rotation(x=0, y=0, z=0)
            )
        )

        # 5. Torus
        self.geometry_manager.create_shape(
            shape_type=ShapeType.TORUS,
            name="Magenta Torus",
            color=(0.7, 0.2, 0.7),
            properties=TorusProperties(
                major_radius=25, 
                minor_radius=10,
                translation=Translation(x=-80, y=0, z=30),
                rotation=Rotation(x=0, y=90, z=0)
            )
        )

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