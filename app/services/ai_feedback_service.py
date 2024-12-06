from app.services.openai_service import OpenAIService
from app.services.content_combiner_service import ContentCombinerService
from app.services.settings_manager import SettingsManager

class AIFeedbackService:
    """Service for getting AI feedback on writing."""

    def __init__(self):
        self.settings_manager = SettingsManager()
        self.openai_service = OpenAIService(self.settings_manager)
        self.content_combiner = ContentCombinerService()
        self._initialize_openai()

    def _initialize_openai(self):
        api_key = self.settings_manager.get("openai.api_key")
        if api_key:
            self.openai_service.initialize(api_key)

    def get_feedback(self, submission: str, criteria: str, prompt: str = "") -> str:
        """Get AI feedback on a writing submission."""
        try:
            # Set the prompt if provided
            if prompt:
                self.content_combiner.set_writing_prompt(prompt)
            
            combined_content = self.content_combiner.combine_content(
                submission=submission,
                criteria=criteria
            )
            
            messages = [
                {"role": "assistant", "content": "I am a writing assistant providing detailed feedback on submissions."},
                {"role": "user", "content": combined_content}
            ]
            
            model = self.settings_manager.get("openai.model", "gpt-3.5-turbo")
            return self.openai_service.get_chat_completion(messages=messages, model=model)
        except Exception as e:
            print(f"Error getting feedback: {str(e)}")
            return ""
