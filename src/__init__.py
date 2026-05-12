"""
Visual Novel Editor for Yandex Games
Application entry point
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.gui.main_window import MainWindow


def main():
    """Main application entry point"""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Visual Novel Editor")
    app.setOrganizationName("YandexGames")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
