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
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QIcon, QPixmap


class GeometryTreeWidget(QWidget):
    """
    A tree widget for displaying and managing geometry shapes.
    
    Features:
    - Hierarchical display of shapes
    - Show/hide shapes via checkboxes
    - Color indicators for each shape
    - Selection synchronization with viewer
    - Shape information (type, properties)
    
    Signals:
        shape_visibility_changed(str, bool): Emitted when shape visibility changes (shape_id, visible)
        shape_selected(str): Emitted when a shape is selected in the tree (shape_id)
        shape_deleted(str): Emitted when a shape is deleted (shape_id)
        clear_all_requested(): Emitted when user requests to clear all shapes
    """

    # Qt Signals
    shape_visibility_changed = Signal(str, bool)
    shape_selected = Signal(str)
    shape_deleted = Signal(str)
    clear_all_requested = Signal()

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
        self.tree.setHeaderLabels(["Shape", "Type", "Properties"])
        self.tree.setColumnCount(3)
        
        # Configure tree
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # Set column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Connect tree signals
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.tree)
        
        # Bottom panel with shape count
        button_layout = QHBoxLayout()
        
        # Shape count label
        self.count_label = QLabel("Shapes: 0")
        self.count_label.setStyleSheet("color: #666; padding: 5px;")
        button_layout.addWidget(self.count_label)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def add_shape(
        self,
        shape_id: str,
        shape_type: str = "Shape",
        color: Optional[tuple] = None,
        properties: Optional[Dict] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Add a shape to the tree.
        
        Args:
            shape_id: Unique identifier for the shape
            shape_type: Type of shape (Box, Sphere, Cylinder, etc.)
            color: RGB color tuple (0-1 range)
            properties: Dictionary of shape properties
            name: Display name (auto-generated if None)
            
        Returns:
            str: The shape_id used
        """
        # Generate name if not provided
        if name is None:
            self._shape_counter += 1
            name = f"{shape_type} {self._shape_counter}"
        
        # Create tree item
        item = QTreeWidgetItem([name, shape_type, ""])
        
        # Set checkable
        item.setFlags(
            item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable
        )
        item.setCheckState(0, Qt.CheckState.Checked)
        
        # Store shape_id in item data
        item.setData(0, Qt.ItemDataRole.UserRole, shape_id)
        
        # Set color indicator
        if color:
            color_icon = self._create_color_icon(color)
            item.setIcon(0, color_icon)
        
        # Add properties as child items if provided
        if properties:
            for key, value in properties.items():
                prop_item = QTreeWidgetItem([f"{key}: {value}", "", ""])
                prop_item.setFlags(
                    prop_item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable
                )
                item.addChild(prop_item)
        
        # Add to tree
        self.tree.addTopLevelItem(item)
        
        # Store reference
        self._shapes[shape_id] = item
        
        # Update count
        self._update_count()
        
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
            self._update_count()
            
    def clear_all(self):
        """Clear all shapes from the tree."""
        self.tree.clear()
        self._shapes.clear()
        self._shape_counter = 0
        self._update_count()
        
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
        if shape_id in self._shapes:
            item = self._shapes[shape_id]
            # Remove existing property children
            item.takeChildren()
            # Add updated properties
            for key, value in properties.items():
                prop_item = QTreeWidgetItem([f"{key}: {value}", "", ""])
                prop_item.setFlags(
                    prop_item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable
                )
                item.addChild(prop_item)
                
    def _create_color_icon(self, color: tuple) -> QIcon:
        """
        Create a color icon for the shape.
        
        Args:
            color: RGB color tuple (0-1 range)
            
        Returns:
            QIcon with the specified color
        """
        # Convert color from 0-1 to 0-255
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        
        # Create pixmap
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(r, g, b))
        
        return QIcon(pixmap)
        
    def _update_count(self):
        """Update the shape count label."""
        count = len(self._shapes)
        self.count_label.setText(f"Shapes: {count}")
        
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

    # Geometry Manager signal handlers
    
    def on_shape_created(self, shape_id: str, managed_shape):
        """
        Handle shape creation from geometry manager.
        
        Args:
            shape_id: ID of the created shape
            managed_shape: ManagedShape object
        """
        # Prepare properties for display
        properties = managed_shape.properties.get_formatted_properties()
        if managed_shape.transparency > 0:
            properties["Transparency"] = f"{int(managed_shape.transparency * 100)}%"
        
        # Add to tree
        self.add_shape(
            shape_id,
            shape_type=managed_shape.shape_type.value,
            color=managed_shape.color,
            name=managed_shape.name,
            properties=properties
        )
    
    def on_shape_updated(self, shape_id: str, managed_shape):
        """
        Handle shape update from geometry manager.
        
        Args:
            shape_id: ID of the updated shape
            managed_shape: ManagedShape object with updated data
        """
        # Update properties in tree
        self.update_shape_properties(
            shape_id,
            managed_shape.properties.get_formatted_properties()
        )
    
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
