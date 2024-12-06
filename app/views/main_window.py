from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from app.views.left_panel import LeftPanel
from app.views.middle_panel import MiddlePanel
from app.views.right_panel import RightPanel
from app.services.settings_manager import SettingsManager
from app.services.ui_theme_manager import UIThemeManager
import os

class MainWindow(QMainWindow):
    """Main window of the application."""

    def __init__(self, app: QApplication, settings_manager: SettingsManager):
        super().__init__()
        self.app = app
        self.settings_manager = settings_manager
        self.setWindowTitle("AI Writing Assistant")
        self.setMinimumSize(1024, 768)

        # Configure default font
        self._configure_fonts()

        # Initialize UI theme manager
        self.ui_theme_manager = UIThemeManager(app)

        self.init_ui()
        self._restore_window_state()
        self._restore_panel_sizes()

    def _configure_fonts(self):
        default_font = QFont("Helvetica", 10)
        self.app.setFont(default_font)
        
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'fonts', 'Roboto-Regular.ttf')
        
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
        
        QFont.insertSubstitution("System", "Helvetica")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.left_panel = LeftPanel(self.settings_manager)
        self.middle_panel = MiddlePanel(self.settings_manager)
        self.right_panel = RightPanel(self.settings_manager, self.ui_theme_manager)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.middle_panel)
        self.splitter.addWidget(self.right_panel)
        
        self.splitter.splitterMoved.connect(self._save_panel_sizes)

        layout = QHBoxLayout()
        layout.addWidget(self.splitter)
        central_widget.setLayout(layout)

        self.left_panel.setMinimumWidth(200)
        self.middle_panel.setMinimumWidth(300)
        self.right_panel.setMinimumWidth(200)

    def _save_panel_sizes(self):
        sizes = self.splitter.sizes()
        self.settings_manager.set("app.panel_sizes", sizes)

    def _restore_panel_sizes(self):
        default_sizes = [250, 500, 250]
        saved_sizes = self.settings_manager.get("app.panel_sizes", default_sizes)
        
        if len(saved_sizes) == 3 and all(isinstance(size, int) for size in saved_sizes):
            self.splitter.setSizes(saved_sizes)
        else:
            self.splitter.setSizes(default_sizes)

    def closeEvent(self, event):
        self._save_window_state()
        super().closeEvent(event)

    def _save_window_state(self):
        self.settings_manager.set("app.window.size", [self.size().width(), self.size().height()])
        self.settings_manager.set("app.window.pos", [self.pos().x(), self.pos().y()])
        self.settings_manager.set("app.window.maximized", self.isMaximized())

    def _restore_window_state(self):
        default_size = [1024, 768]
        default_pos = [100, 100]
        
        size = self.settings_manager.get("app.window.size", default_size)
        pos = self.settings_manager.get("app.window.pos", default_pos)
        is_maximized = self.settings_manager.get("app.window.maximized", False)
        
        if len(size) == 2 and all(isinstance(x, int) and x > 0 for x in size):
            self.resize(QSize(size[0], size[1]))
        
        if len(pos) == 2 and all(isinstance(x, int) for x in pos):
            available_geometry = self.screen().availableGeometry()
            if (pos[0] < available_geometry.right() - 100 and 
                pos[1] < available_geometry.bottom() - 100 and
                pos[0] > available_geometry.left() and 
                pos[1] > available_geometry.top()):
                self.move(QPoint(pos[0], pos[1]))
        
        if is_maximized:
            self.showMaximized()
