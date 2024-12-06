from app.views.tabs.writing_prompts_tab import WritingPromptsTab
from app.services.content_combiner_service import ContentCombinerService

class MainController:
    def __init__(self, app, view, settings_manager):
        self.app = app
        self.view = view
        self.settings_manager = settings_manager
        self.content_combiner_service = ContentCombinerService()
        self.view.left_panel.writing_prompts_tab.prompt_selected.connect(self._handle_prompt_selected)

    def initialize(self):
        """Initialize the main window with settings."""
        # Additional initialization logic can be added here if needed
        pass

    def _handle_prompt_selected(self, prompt: str):
        if prompt:
            # Update content combiner if needed
            self.content_combiner_service.set_writing_prompt(prompt)
