from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QHBoxLayout, QGroupBox, QFormLayout, QCheckBox
from PyQt6.QtCore import QThread, pyqtSignal
from app.services.settings_manager import SettingsManager
from app.services.secure_storage_service import SecureStorageService
from app.services.ui_theme_manager import UIThemeManager
from app.config.chat_config import CHAT_CONFIG
import json

class ModelFetchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            models_response = client.models.list()
            
            model_info = []
            excluded_terms = {'realtime', 'audio', 'vision'}
            
            for model in models_response.data:
                if (model.id.startswith(('gpt-3.5', 'gpt-4', 'o1')) and 
                    not any(term in model.id.lower() for term in excluded_terms)):
                    model_info.append({
                        'id': model.id,
                        'name': model.id.replace('-', ' ').title(),
                        'description': self._get_model_description(model.id)
                    })
            self.finished.emit(model_info)
        except Exception as e:
            self.error.emit(str(e))

    def _get_model_description(self, model_id: str) -> str:
        descriptions = {
            'gpt-4': 'Most capable GPT-4 model, better at complex tasks',
            'gpt-4-turbo-preview': 'Latest GPT-4 model with improved performance',
            'gpt-3.5-turbo': 'Fast and efficient for simpler tasks',
            'gpt-3.5-turbo-16k': 'Same capabilities as standard GPT-3.5 but with 4x the context length'
        }
        return descriptions.get(model_id, 'Standard model for general use')

class SettingsTab(QWidget):
    """Settings tab for application configuration."""

    def __init__(self, settings_manager: SettingsManager, ui_theme_manager: UIThemeManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.ui_theme_manager = ui_theme_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.ui_theme_manager.get_available_themes())
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        main_layout.addWidget(self.theme_combo)

        main_layout.addWidget(QLabel("OpenAI API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        main_layout.addWidget(self.api_key_input)

        main_layout.addWidget(QLabel("OpenAI Model:"))
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.refresh_models_button = QPushButton("Refresh Models")
        self.refresh_models_button.clicked.connect(self.fetch_and_update_models)
        
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.refresh_models_button)
        main_layout.addLayout(model_layout)

        self.test_api_button = QPushButton("Test API Key")
        self.test_api_button.clicked.connect(self.test_api_key)
        main_layout.addWidget(self.test_api_button)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_button)

        chat_group = QGroupBox("Chat Settings")
        chat_layout = QVBoxLayout()

        welcome_layout = QFormLayout()
        self.welcome_message_input = QLineEdit()
        self.welcome_message_input.setText(
            self.settings_manager.get(
                "chat.welcome_message",
                CHAT_CONFIG["default_settings"]["welcome_message"]
            )
        )
        
        self.display_welcome_checkbox = QCheckBox("Show welcome message")
        self.display_welcome_checkbox.setChecked(
            self.settings_manager.get(
                "chat.display_welcome",
                CHAT_CONFIG["default_settings"]["display_welcome"]
            )
        )

        self.welcome_style_combo = QComboBox()
        self.welcome_style_combo.addItems(["formal", "casual", "minimal", "custom"])
        
        welcome_layout.addRow("Welcome Message:", self.welcome_message_input)
        welcome_layout.addRow("Style:", self.welcome_style_combo)
        welcome_layout.addRow(self.display_welcome_checkbox)

        self.welcome_message_input.textChanged.connect(self._on_welcome_message_changed)
        self.welcome_style_combo.currentTextChanged.connect(self._on_welcome_style_changed)
        self.display_welcome_checkbox.toggled.connect(self._on_display_welcome_changed)

        chat_layout.addLayout(welcome_layout)
        chat_group.setLayout(chat_layout)
        main_layout.addWidget(chat_group)
        main_layout.addStretch()

    def load_settings(self):
        current_theme = self.settings_manager.get("app.theme", "Clean")
        if current_theme:
            index = self.theme_combo.findText(current_theme.capitalize())
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
                self.ui_theme_manager.apply_theme(current_theme)

        api_key = self.settings_manager.get("openai.api_key", "")
        if api_key:
            self.api_key_input.setText(api_key)

        saved_models = self.settings_manager.get("openai.available_models", [])
        selected_model = self.settings_manager.get("openai.model", "")
        
        if saved_models:
            self.model_combo.clear()
            model_ids = [model['id'] for model in saved_models]
            self.model_combo.addItems(model_ids)
            if selected_model:
                index = self.model_combo.findText(selected_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)

    def on_theme_changed(self, theme_name: str):
        if self.ui_theme_manager.apply_theme(theme_name):
            self.settings_manager.set("app.theme", theme_name)

    def test_api_key(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            QMessageBox.information(self, "Success", "API key is valid!")
        else:
            QMessageBox.warning(self, "Error", "Please enter an API key.")

    def fetch_and_update_models(self):
        api_key = self.api_key_input.text().strip()
        
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key first.")
            return

        self.worker = ModelFetchWorker(api_key)
        self.worker.finished.connect(self._handle_models_fetched)
        self.worker.error.connect(self._handle_fetch_error)
        
        self.refresh_models_button.setEnabled(False)
        self.refresh_models_button.setText("Fetching...")
        
        self.worker.start()

    def _handle_models_fetched(self, model_info):
        self.model_combo.clear()
        self.model_combo.addItems([model['id'] for model in model_info])
        
        self.settings_manager.set("openai.available_models", model_info)
        self.refresh_models_button.setEnabled(True)
        self.refresh_models_button.setText("Refresh Models")
        QMessageBox.information(self, "Success", "Models updated successfully!")

    def _handle_fetch_error(self, error_message):
        self.refresh_models_button.setEnabled(True)
        self.refresh_models_button.setText("Refresh Models")
        QMessageBox.warning(self, "Error", f"Failed to fetch models: {error_message}")

    def save_settings(self):
        api_key = self.api_key_input.text().strip()
        selected_model = self.model_combo.currentText()

        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key.")
            return

        self.settings_manager.set("openai.api_key", api_key)
        if selected_model:
            self.settings_manager.set("openai.model", selected_model)

        QMessageBox.information(self, "Success", "Settings saved successfully!")

    def _on_welcome_message_changed(self, text: str):
        self.settings_manager.set("chat.welcome_message", text)

    def _on_welcome_style_changed(self, style: str):
        if style != "custom":
            message = CHAT_CONFIG["message_types"]["welcome"][style]
            self.welcome_message_input.setText(message)
            self.welcome_message_input.setEnabled(False)
        else:
            self.welcome_message_input.setEnabled(True)

    def _on_display_welcome_changed(self, checked: bool):
        self.settings_manager.set("chat.display_welcome", checked)
