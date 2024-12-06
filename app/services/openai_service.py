import openai
from typing import List, Dict, Any, Optional
from app.services.settings_manager import SettingsManager
from app.config.openai_config import OPENAI_CONFIG

class OpenAIService:
    """Service for handling OpenAI API interactions."""

    def __init__(self, settings_manager: SettingsManager):
        self.settings_manager = settings_manager
        self.api_key = None
        self.client = None
        self.available_models = []
        self.current_settings = self._load_settings()

    def initialize(self, api_key: str = None) -> bool:
        if api_key is None:
            api_key = self.settings_manager.get("openai.api_key")
        if not api_key:
            return False
        
        try:
            self.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            return True
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            self.client = None
            self.api_key = None
            return False

    def is_initialized(self) -> bool:
        return self.client is not None

    def get_chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        if not self.is_initialized():
            raise ValueError("OpenAI client not initialized")

        try:
            settings = self.current_settings.copy()
            if model:
                settings['model'] = model

            if settings['model'].startswith('o1'):
                o1_config = OPENAI_CONFIG["model_specific_settings"]["o1"]
                settings.update(o1_config.get("default_values", {}))
                supported_params = o1_config["supported_params"]
                settings = {k: v for k, v in settings.items() if k in supported_params or k == 'model'}
                if 'max_tokens' in settings:
                    settings['max_completion_tokens'] = settings.pop('max_tokens')

            response = self.client.chat.completions.create(
                messages=messages,
                **settings
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting chat completion: {e}")
            return None

    def _load_settings(self) -> Dict[str, Any]:
        openai_settings = self.settings_manager.get('openai', {})
        if not openai_settings:
            openai_settings = OPENAI_CONFIG["default_settings"]
            self.settings_manager.set('openai', openai_settings)
        
        model = openai_settings.get('model', 'gpt-4')
        
        base_settings = {'model': model}
        
        if model.startswith('o1'):
            base_settings.update({
                'temperature': 1,
                'max_completion_tokens': openai_settings.get('max_tokens', 4000)
            })
        else:
            base_settings.update({
                'temperature': openai_settings.get('temperature', 0.7),
                'max_tokens': openai_settings.get('max_tokens', 4000),
                'top_p': openai_settings.get('top_p', 1.0),
                'frequency_penalty': openai_settings.get('frequency_penalty', 0.0),
                'presence_penalty': openai_settings.get('presence_penalty', 0.0)
            })
        
        return base_settings
