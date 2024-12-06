import json
from pathlib import Path
from typing import Optional
from .secure_storage_service import SecureStorageService

class SettingsManager:
    """Manages application settings."""

    def __init__(self):
        self.settings = {}
        self.settings_file = Path.home() / '.aiwritingassistant' / 'settings.json'
        self.secure_storage = SecureStorageService()
        self.load_settings()

    def get(self, key: str, default=None):
        if key == "openai.api_key":
            return self.secure_storage.get_secret("openai_api_key") or default
        
        try:
            value = self.settings
            for part in key.split('.'):
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value) -> None:
        if key == "openai.api_key":
            self.secure_storage.save_secret("openai_api_key", value)
            return

        parts = key.split('.')
        current = self.settings
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
        self.save_settings()

    def load_settings(self) -> None:
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                config_path = Path(__file__).parent.parent / 'config' / 'settings.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        self.settings = json.load(f)
                self.save_settings() 
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {}

    def save_settings(self) -> None:
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_writing_prompts_folder(self) -> Optional[str]:
        return self.get('folders.writing_prompts')
    
    def set_writing_prompts_folder(self, folder: Optional[str]) -> None:
        self.set('folders.writing_prompts', folder)
