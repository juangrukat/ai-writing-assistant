import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from app.controllers.main_controller import MainController
from app.views.main_window import MainWindow
from app.services.settings_manager import SettingsManager

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Create a single instance of SettingsManager
    settings_manager = SettingsManager()
    
    # Pass settings_manager to MainWindow
    main_window = MainWindow(app, settings_manager)
    
    # Create controller with shared instances
    main_controller = MainController(app, main_window, settings_manager)
    main_controller.initialize()
    
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
