from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from app.views.tabs.ai_feedback_tab import AIFeedbackTab
from app.views.tabs.select_criteria_tab import SelectCriteriaTab
from app.views.tabs.settings_tab import SettingsTab
from app.services.settings_manager import SettingsManager
from app.services.ui_theme_manager import UIThemeManager

class RightPanel(QWidget):
    """Right panel containing AI Feedback, Select Criteria, and Settings tabs."""

    def __init__(self, settings_manager: SettingsManager, ui_theme_manager: UIThemeManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.ui_theme_manager = ui_theme_manager
        
        current_theme = settings_manager.get("app.theme", "Clean")
        ui_theme_manager.apply_theme(current_theme)
        
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        self.select_criteria_tab = SelectCriteriaTab()
        self.ai_feedback_tab = AIFeedbackTab()
        self.settings_tab = SettingsTab(self.settings_manager, self.ui_theme_manager)

        self.tab_widget.addTab(self.ai_feedback_tab, "AI Feedback")
        self.tab_widget.addTab(self.select_criteria_tab, "Select Criteria")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        active_tab = self.settings_manager.get("app.tabs.right_panel.active_tab", 0)
        self.tab_widget.setCurrentIndex(active_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def _on_tab_changed(self, index: int):
        self.settings_manager.set("app.tabs.right_panel.active_tab", index)
        self.settings_manager.save_settings()
