"""
Property Editor Widget
A widget component for editing geometry shape properties including size, translation, and rotation
"""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QDoubleSpinBox,
    QGroupBox,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Signal

from cad_widgets.enums import ShapeType


class PropertyEditorWidget(QWidget):
    """
    A widget for editing geometry shape properties.
    
    Features:
    - Edit shape size parameters (width, height, depth, radius, etc.)
    - Edit translation (x, y, z)
    - Edit rotation (x, y, z angles in degrees)
    - Changes are applied automatically when values are modified
    
    Signals:
        properties_changed(str, dict): Emitted when properties are changed (shape_id, properties)
    """

    # Qt Signals
    properties_changed = Signal(str, dict)

    def __init__(self, parent=None):
        """Initialize the property editor widget."""
        super().__init__(parent)
        
        # Current shape tracking
        self._current_shape_id: Optional[str] = None
        self._current_shape_type: Optional[ShapeType] = None
        self._loading: bool = False  # Flag to prevent emitting signals during loading
        
        # Setup UI
        self._setup_ui()
        self._set_enabled(False)
        
    def _setup_ui(self):
        """Setup the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_label = QLabel("Property Editor")
        header_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        main_layout.addWidget(header_label)
        
        # Shape info label
        self.shape_info_label = QLabel("No shape selected")
        self.shape_info_label.setStyleSheet(
            "color: #666; padding: 5px; font-style: italic;"
        )
        main_layout.addWidget(self.shape_info_label)
        
        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container widget for scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Size Parameters Group
        self.size_group = QGroupBox("Size Parameters")
        size_layout = QFormLayout()
        size_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # Dynamic size parameters (will be populated based on shape type)
        self.size_spinboxes: Dict[str, QDoubleSpinBox] = {}
        
        # Common size parameters
        self._create_size_parameter("width", "Width:", size_layout)
        self._create_size_parameter("height", "Height:", size_layout)
        self._create_size_parameter("depth", "Depth:", size_layout)
        self._create_size_parameter("radius", "Radius:", size_layout)
        self._create_size_parameter("base_radius", "Base Radius:", size_layout)
        self._create_size_parameter("top_radius", "Top Radius:", size_layout)
        self._create_size_parameter("length", "Length:", size_layout)
        self._create_size_parameter("major_radius", "Major Radius:", size_layout)
        self._create_size_parameter("minor_radius", "Minor Radius:", size_layout)
        
        self.size_group.setLayout(size_layout)
        scroll_layout.addWidget(self.size_group)
        
        # Translation Group
        self.translation_group = QGroupBox("Translation")
        translation_layout = QHBoxLayout()
        translation_layout.setSpacing(5)
        
        self.trans_x = self._create_coordinate_spinbox()
        self.trans_y = self._create_coordinate_spinbox()
        self.trans_z = self._create_coordinate_spinbox()
        
        translation_layout.addWidget(QLabel("X:"))
        translation_layout.addWidget(self.trans_x)
        translation_layout.addSpacing(10)
        translation_layout.addWidget(QLabel("Y:"))
        translation_layout.addWidget(self.trans_y)
        translation_layout.addSpacing(10)
        translation_layout.addWidget(QLabel("Z:"))
        translation_layout.addWidget(self.trans_z)
        translation_layout.addStretch()
        
        self.translation_group.setLayout(translation_layout)
        scroll_layout.addWidget(self.translation_group)
        
        # Rotation Group
        self.rotation_group = QGroupBox("Rotation")
        rotation_layout = QHBoxLayout()
        rotation_layout.setSpacing(5)
        
        self.rot_x = self._create_angle_spinbox()
        self.rot_y = self._create_angle_spinbox()
        self.rot_z = self._create_angle_spinbox()
        
        rotation_layout.addWidget(QLabel("X:"))
        rotation_layout.addWidget(self.rot_x)
        rotation_layout.addSpacing(10)
        rotation_layout.addWidget(QLabel("Y:"))
        rotation_layout.addWidget(self.rot_y)
        rotation_layout.addSpacing(10)
        rotation_layout.addWidget(QLabel("Z:"))
        rotation_layout.addWidget(self.rot_z)
        rotation_layout.addStretch()
        
        self.rotation_group.setLayout(rotation_layout)
        scroll_layout.addWidget(self.rotation_group)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
    def _create_size_parameter(self, param_name: str, label: str, layout: QFormLayout):
        """Create a size parameter spinbox."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(0.01, 10000.0)
        spinbox.setDecimals(2)
        spinbox.setSingleStep(0.1)
        spinbox.setValue(1.0)
        spinbox.setMinimumWidth(80)
        spinbox.editingFinished.connect(self._on_value_changed)
        
        self.size_spinboxes[param_name] = spinbox
        layout.addRow(label, spinbox)
        
    def _create_coordinate_spinbox(self) -> QDoubleSpinBox:
        """Create a coordinate spinbox for translation."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(-10000.0, 10000.0)
        spinbox.setDecimals(2)
        spinbox.setSingleStep(0.1)
        spinbox.setValue(0.0)
        spinbox.setMinimumWidth(80)
        spinbox.editingFinished.connect(self._on_value_changed)
        return spinbox
        
    def _create_angle_spinbox(self) -> QDoubleSpinBox:
        """Create an angle spinbox for rotation."""
        spinbox = QDoubleSpinBox()
        spinbox.setRange(-360.0, 360.0)
        spinbox.setDecimals(1)
        spinbox.setSingleStep(1.0)
        spinbox.setValue(0.0)
        spinbox.setMinimumWidth(80)
        spinbox.setSuffix("°")
        spinbox.editingFinished.connect(self._on_value_changed)
        return spinbox
        
    def set_shape(
        self,
        shape_id: str,
        shape_type: ShapeType,
        shape_name: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Set the shape to edit.
        
        Args:
            shape_id: Unique identifier for the shape
            shape_type: Type of shape (Box, Sphere, Cylinder, etc.)
            properties: Dictionary of current shape properties
        """
        self._current_shape_id = shape_id
        self._current_shape_type = shape_type
        
        # Update UI
        self.shape_info_label.setText(f"Editing: {shape_name}")
        
        # Load properties into UI
        self._load_properties(properties or {})
        
        # Enable UI
        self._set_enabled(True)
        
        # Configure visible size parameters based on shape type
        self._configure_size_parameters(shape_type)
        
    def clear_shape(self):
        """Clear the current shape selection."""
        self._current_shape_id = None
        self._current_shape_type = None
        
        self.shape_info_label.setText("No shape selected")
        self._set_enabled(False)
        
    def _load_properties(self, properties: Dict[str, Any]):
        """Load properties into the UI controls."""
        # Block signals during loading to prevent triggering updates
        self._loading = True
        
        # Load size parameters
        for param_name, spinbox in self.size_spinboxes.items():
            if param_name in properties:
                spinbox.setValue(float(properties[param_name]))
            else:
                spinbox.setValue(1.0)
        
        # Load translation
        translation = properties.get("translation", {"x": 0, "y": 0, "z": 0})
        if isinstance(translation, dict):
            self.trans_x.setValue(translation.get("x", 0))
            self.trans_y.setValue(translation.get("y", 0))
            self.trans_z.setValue(translation.get("z", 0))
        
        # Load rotation
        rotation = properties.get("rotation", {"x": 0, "y": 0, "z": 0})
        if isinstance(rotation, dict):
            self.rot_x.setValue(rotation.get("x", 0))
            self.rot_y.setValue(rotation.get("y", 0))
            self.rot_z.setValue(rotation.get("z", 0))
        
        # Re-enable signal emission
        self._loading = False
            
    def _configure_size_parameters(self, shape_type: ShapeType):
        """Show/hide size parameters based on shape type."""
        # Define which parameters are relevant for each shape type
        parameter_visibility = {
            ShapeType.BOX: ["width", "height", "depth"],
            ShapeType.SPHERE: ["radius"],
            ShapeType.CYLINDER: ["radius", "height"],
            ShapeType.CONE: ["base_radius", "top_radius", "height"],
            ShapeType.TORUS: ["major_radius", "minor_radius"],
            ShapeType.UNION: [],  # No size parameters for boolean operations
            ShapeType.SUBTRACTION: [],  # No size parameters for boolean operations
            ShapeType.IMPORTED: [],  # No size parameters for imported shapes
        }
        
        # Get relevant parameters for this shape type
        relevant_params = parameter_visibility.get(shape_type, [])
        
        # Show/hide parameters
        size_layout = self.size_group.layout()
        if not isinstance(size_layout, QFormLayout):
            return
            
        for i in range(size_layout.rowCount()):
            label_item = size_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            field_item = size_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
            
            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()
                
                if label_widget is None or field_widget is None:
                    continue
                
                # Find which parameter this row represents
                for param_name, spinbox in self.size_spinboxes.items():
                    if spinbox == field_widget:
                        # Show if parameter is relevant, hide otherwise
                        visible = param_name in relevant_params
                        label_widget.setVisible(visible)
                        field_widget.setVisible(visible)
                        break
                        
    def _get_current_properties(self) -> Dict[str, Any]:
        """Get the current property values from the UI."""
        properties: Dict[str, Any] = {}
        
        # Get size parameters (only visible ones)
        for param_name, spinbox in self.size_spinboxes.items():
            if spinbox.isVisible():
                properties[param_name] = spinbox.value()
        
        # Get translation
        properties["translation"] = {
            "x": self.trans_x.value(),
            "y": self.trans_y.value(),
            "z": self.trans_z.value(),
        }
        
        # Get rotation
        properties["rotation"] = {
            "x": self.rot_x.value(),
            "y": self.rot_y.value(),
            "z": self.rot_z.value(),
        }
        
        return properties
        
    def _set_enabled(self, enabled: bool):
        """Enable or disable the editor controls."""
        self.size_group.setEnabled(enabled)
        self.translation_group.setEnabled(enabled)
        self.rotation_group.setEnabled(enabled)
        
    def _on_value_changed(self):
        """Handle value changed in any spinbox."""
        # Don't emit during initial loading
        if self._loading:
            return
            
        if self._current_shape_id:
            properties = self._get_current_properties()
            self.properties_changed.emit(self._current_shape_id, properties)
