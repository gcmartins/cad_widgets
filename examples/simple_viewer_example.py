from PySide6.QtWidgets import QApplication
from cad_widgets import OCPWidget, GeometryService, DisplayMode

def main():
    app = QApplication([])

    viewer = OCPWidget()
    viewer.resize(800, 600)

    geo = GeometryService()
    box = geo.create_box(100, 100, 100)
    viewer.set_display_mode(DisplayMode.SHADED)
    viewer.display_shape(box, 'box_id', color=(0.8, 0.2, 0.2))
    viewer.fit_all()

    viewer.show()
    app.exec()

if __name__ == "__main__":    
    main()