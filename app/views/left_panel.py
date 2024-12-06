from PyQt6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from app.views.tabs.ai_assistant_tab import AIAssistantTab
from app.views.tabs.writing_prompts_tab import WritingPromptsTab
from app.services.settings_manager import SettingsManager

class LeftPanel(QWidget):
    """Left panel containing AI Assistant and Writing Prompts tabs."""

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.ai_assistant_tab = AIAssistantTab(self.settings_manager)
        self.writing_prompts_tab = WritingPromptsTab(self.settings_manager)
        
        self.writing_prompts_tab.prompt_selected.connect(self._handle_prompt_selected)

        self.tabs.addTab(self.ai_assistant_tab, "AI Assistant")
        self.tabs.addTab(self.writing_prompts_tab, "Writing Prompts")

        active_tab = self.settings_manager.get("app.tabs.left_panel.active_tab", 0)
        self.tabs.setCurrentIndex(active_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def _handle_prompt_selected(self, prompt: str):
        main_window = self.window()
        if hasattr(main_window, 'middle_panel'):
            main_window.middle_panel.set_selected_prompt(prompt)

    def _on_tab_changed(self, index: int):
        self.settings_manager.set("app.tabs.left_panel.active_tab", index)
        self.settings_manager.save_settings()
