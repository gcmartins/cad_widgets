"""
Geometry Tree Widget
A widget component for displaying and managing geometry shapes in a tree view
"""

from typing import Optional, Dict, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QHeaderView,
    QMenu,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QAction

from ..enums import ShapeType


class GeometryTreeWidget(QWidget):
    """
    A tree widget for displaying and managing geometry shapes.
    
    Features:
    - Hierarchical display of shapes
    - Show/hide shapes via checkboxes
    - Selection synchronization with viewer
    - Shape information (name, type)
    
    Signals:
        shape_visibility_changed(str, bool): Emitted when shape visibility changes (shape_id, visible)
        shape_selected(str): Emitted when a shape is selected in the tree (shape_id)
        shape_deleted(str): Emitted when a shape is deleted (shape_id)
        clear_all_requested(): Emitted when user requests to clear all shapes
        shape_creation_requested(ShapeType): Emitted when user requests to create a new shape
        shapes_union_requested(list): Emitted when user requests to union selected shapes (list of shape_ids)
        shapes_subtract_requested(list): Emitted when user requests to subtract shapes (list of shape_ids)
        export_step_requested(str): Emitted when user requests to export shape as STEP (shape_id)
        export_iges_requested(str): Emitted when user requests to export shape as IGES (shape_id)
        import_requested(): Emitted when user requests to import a CAD file (STEP or IGES)
    """

    # Qt Signals
    shape_visibility_changed = Signal(str, bool)
    shape_selected = Signal(str)
    shape_deleted = Signal(str)
    clear_all_requested = Signal()
    shape_creation_requested = Signal(object)  # ShapeType
    shapes_union_requested = Signal(list)  # List of shape_ids
    shapes_subtract_requested = Signal(list)  # List of shape_ids
    export_step_requested = Signal(str)  # shape_id
    export_iges_requested = Signal(str)  # shape_id
    import_requested = Signal()  # Unified import signal for STEP/IGES files

    def __init__(self, parent=None):
        """Initialize the geometry tree widget."""
        super().__init__(parent)
        
        # Internal shape tracking
        self._shapes: Dict[str, QTreeWidgetItem] = {}
        self._shape_counter = 0
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_label = QLabel("Geometry Tree")
        header_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        layout.addWidget(header_label)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Shape", "Type"])
        self.tree.setColumnCount(2)
        
        # Configure tree
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        
        # Enable context menu
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        
        # Set column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        # Connect tree signals
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.tree)
        
    def add_shape(
        self,
        shape_id: str,
        shape_type: str = "Shape",
        name: Optional[str] = None,
    ) -> str:
        """
        Add a shape to the tree.
        
        Args:
            shape_id: Unique identifier for the shape
            shape_type: Type of shape (Box, Sphere, Cylinder, etc.)
            color: RGB color tuple (0-1 range) - deprecated, no longer displayed
            properties: Dictionary of shape properties - deprecated, no longer displayed
            name: Display name (auto-generated if None)
            
        Returns:
            str: The shape_id used
        """
        # Generate name if not provided
        if name is None:
            self._shape_counter += 1
            name = f"{shape_type} {self._shape_counter}"
        
        # Create tree item
        item = QTreeWidgetItem([name, shape_type])
        
        # Set checkable
        item.setFlags(
            item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        )
        item.setCheckState(0, Qt.CheckState.Checked)
        
        # Store shape_id in item data
        item.setData(0, Qt.ItemDataRole.UserRole, shape_id)
        
        # Add to tree
        self.tree.addTopLevelItem(item)
        
        # Store reference
        self._shapes[shape_id] = item
        
        return shape_id
        
    def remove_shape(self, shape_id: str):
        """
        Remove a shape from the tree.
        
        Args:
            shape_id: ID of the shape to remove
        """
        if shape_id in self._shapes:
            item = self._shapes[shape_id]
            index = self.tree.indexOfTopLevelItem(item)
            if index >= 0:
                self.tree.takeTopLevelItem(index)
            del self._shapes[shape_id]
            
    def clear_all(self):
        """Clear all shapes from the tree."""
        self.tree.clear()
        self._shapes.clear()
        self._shape_counter = 0
        
    def get_shape_ids(self) -> List[str]:
        """
        Get list of all shape IDs in the tree.
        
        Returns:
            List of shape IDs
        """
        return list(self._shapes.keys())
        
    def is_shape_visible(self, shape_id: str) -> bool:
        """
        Check if a shape is visible.
        
        Args:
            shape_id: ID of the shape
            
        Returns:
            True if visible, False otherwise
        """
        if shape_id in self._shapes:
            item = self._shapes[shape_id]
            return item.checkState(0) == Qt.CheckState.Checked
        return False
        
    def set_shape_visible(self, shape_id: str, visible: bool):
        """
        Set shape visibility.
        
        Args:
            shape_id: ID of the shape
            visible: True to show, False to hide
        """
        if shape_id in self._shapes:
            item = self._shapes[shape_id]
            # Block signals temporarily to avoid triggering visibility change
            self.tree.blockSignals(True)
            item.setCheckState(0, Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked)
            self.tree.blockSignals(False)
            
    def select_shape(self, shape_id: str):
        """
        Select a shape in the tree.
        
        Args:
            shape_id: ID of the shape to select
        """
        if shape_id in self._shapes:
            item = self._shapes[shape_id]
            self.tree.setCurrentItem(item)
            
    def update_shape_properties(self, shape_id: str, properties: Dict):
        """
        Update the properties of a shape.
        
        Args:
            shape_id: ID of the shape
            properties: Dictionary of updated properties
        """
        # Properties are no longer displayed in the tree
        pass
        
    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """
        Handle item changed event (checkbox toggled).
        
        Args:
            item: The changed item
            column: The changed column
        """
        if column == 0:  # Name column with checkbox
            shape_id = item.data(0, Qt.ItemDataRole.UserRole)
            if shape_id:
                visible = item.checkState(0) == Qt.CheckState.Checked
                self.shape_visibility_changed.emit(shape_id, visible)
                
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """
        Handle item clicked event.
        
        Args:
            item: The clicked item
            column: The clicked column
        """
        shape_id = item.data(0, Qt.ItemDataRole.UserRole)
        if shape_id:
            self.shape_selected.emit(shape_id)
    
    def _delete_selected_shapes(self, shape_ids: List[str]):
        """
        Delete multiple selected shapes.
        
        Args:
            shape_ids: List of shape IDs to delete
        """
        for shape_id in shape_ids:
            self.shape_deleted.emit(shape_id)
    
    def _on_context_menu(self, position: QPoint):
        """
        Handle context menu request.
        
        Args:
            position: Position where the context menu was requested
        """
        menu = QMenu(self)
        
        # Get selected shape IDs
        selected_shape_ids = [
            item.data(0, Qt.ItemDataRole.UserRole)
            for item in self.tree.selectedItems()
            if item.data(0, Qt.ItemDataRole.UserRole)
        ]
        
        num_selected = len(selected_shape_ids)
        
        # Actions when shapes are selected
        if num_selected > 0:
            # Delete action
            delete_label = "Delete Shape" if num_selected == 1 else f"Delete {num_selected} Shapes"
            delete_action = QAction(delete_label, self)
            delete_action.triggered.connect(lambda: self._delete_selected_shapes(selected_shape_ids))
            menu.addAction(delete_action)
            menu.addSeparator()
            
            # Boolean operations (2+ shapes)
            if num_selected >= 2:
                union_action = QAction(f"Union ({num_selected} shapes)", self)
                union_action.triggered.connect(lambda: self.shapes_union_requested.emit(selected_shape_ids))
                menu.addAction(union_action)
                
                subtract_action = QAction(f"Subtract ({num_selected} shapes)", self)
                subtract_action.triggered.connect(lambda: self.shapes_subtract_requested.emit(selected_shape_ids))
                menu.addAction(subtract_action)
                menu.addSeparator()
            
            # Export menu (single shape only)
            if num_selected == 1:
                export_menu = menu.addMenu("Export Shape")
                
                export_step_action = QAction("Export as STEP...", self)
                export_step_action.triggered.connect(lambda: self.export_step_requested.emit(selected_shape_ids[0]))
                export_menu.addAction(export_step_action)
                
                export_iges_action = QAction("Export as IGES...", self)
                export_iges_action.triggered.connect(lambda: self.export_iges_requested.emit(selected_shape_ids[0]))
                export_menu.addAction(export_iges_action)
        
        # Actions when clicking on empty space
        else:
            # Create Shape submenu
            create_menu = menu.addMenu("Create Shape")
            shapes = [
                ("Box", ShapeType.BOX),
                ("Sphere", ShapeType.SPHERE),
                ("Cylinder", ShapeType.CYLINDER),
                ("Cone", ShapeType.CONE),
                ("Torus", ShapeType.TORUS),
            ]
            for name, shape_type in shapes:
                action = QAction(name, self)
                action.triggered.connect(lambda _, st=shape_type: self.shape_creation_requested.emit(st))
                create_menu.addAction(action)
            
            # Import action
            import_action = QAction("Import CAD File...", self)
            import_action.triggered.connect(lambda: self.import_requested.emit())
            menu.addAction(import_action)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    # Geometry Manager signal handlers
    
    def on_shape_created(self, shape_id: str, managed_shape):
        """
        Handle shape creation from geometry manager.
        
        Args:
            shape_id: ID of the created shape
            managed_shape: ManagedShape object
        """
        # Add to tree
        self.add_shape(
            shape_id,
            shape_type=managed_shape.shape_type.value,
            name=managed_shape.name
        )
    
    def on_shape_updated(self, shape_id: str, managed_shape):
        """
        Handle shape update from geometry manager.
        
        Args:
            shape_id: ID of the updated shape
            managed_shape: ManagedShape object with updated data
        """
        # Properties are no longer displayed in the tree
        pass
    
    def on_shape_removed(self, shape_id: str):
        """
        Handle shape removal from geometry manager.
        
        Args:
            shape_id: ID of the removed shape
        """
        self.remove_shape(shape_id)
    
    def on_all_cleared(self):
        """Handle all shapes cleared from geometry manager."""
        self.clear_all()
