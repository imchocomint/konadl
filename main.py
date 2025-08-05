# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication

from app_window import ImageSearchApp

if __name__ == "__main__":
    # Ensure QCoreApplication is created before any widgets
    QCoreApplication.setApplicationName("konadl")
    app = QApplication(sys.argv)
    
    window = ImageSearchApp()
    window.show()
    
    sys.exit(app.exec())