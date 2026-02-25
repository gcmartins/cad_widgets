"""
Simple example demonstrating basic OCPWidget usage
Displays a single red box
"""

import os
import sys

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.theme.gnome=false'

from PySide6.QtWidgets import QApplication
from cad_widgets import OCPWidget
from cad_widgets.utils import create_box


def main():
    """Main entry point for the simple example."""
    app = QApplication(sys.argv)
    
    # Create the viewer widget
    viewer = OCPWidget()
    viewer.setWindowTitle("OCP Simple Example - Red Box")
    viewer.resize(800, 600)
    
    # Create and display a box
    box = create_box(100, 100, 100)
    viewer.display_shape(box, color=(0.8, 0.2, 0.2))
    
    # Fit the view
    viewer.fit_all()
    
    # Show the widget
    viewer.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
