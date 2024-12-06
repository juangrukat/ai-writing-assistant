from PyQt6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QPushButton, 
    QLabel, 
    QComboBox, 
    QTextEdit, 
    QFileDialog, 
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal
import os
from app.services.settings_manager import SettingsManager
from app.services.writing_prompts_service import WritingPromptsService
from app.config.writing_prompts_config import WritingPromptsConfig

class WritingPromptsTab(QWidget):
    prompt_selected = pyqtSignal(str)

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.prompts_service = WritingPromptsService()
        self.selected_prompt = None
        self.setup_ui()
        self._restore_last_folder()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Prompts Folder: Not selected")
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_folder_btn)
        layout.addLayout(folder_layout)

        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        self.prompt_display = QTextEdit()
        self.prompt_display.setReadOnly(True)
        self.prompt_display.setPlaceholderText("Select a category and click 'Get New Prompt'...")
        layout.addWidget(self.prompt_display)

        prompt_buttons_layout = QHBoxLayout()
        
        self.get_prompt_btn = QPushButton("Get New Prompt")
        self.get_prompt_btn.clicked.connect(self._get_new_prompt)
        
        self.use_prompt_btn = QPushButton("Use Selected Prompt")
        self.use_prompt_btn.clicked.connect(self._use_selected_prompt)
        
        self.clear_prompt_btn = QPushButton("Clear Prompt")
        self.clear_prompt_btn.clicked.connect(self._clear_selected_prompt)
        
        prompt_buttons_layout.addWidget(self.get_prompt_btn)
        prompt_buttons_layout.addWidget(self.use_prompt_btn)
        prompt_buttons_layout.addWidget(self.clear_prompt_btn)
        layout.addLayout(prompt_buttons_layout)
        
        self.setLayout(layout)

    def _restore_last_folder(self):
        folder = self.settings_manager.get('folders.writing_prompts')
        if folder and os.path.exists(folder):
            self.select_folder(folder)

    def select_folder(self, folder: str = None):
        if not folder:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Prompts Folder",
                self.settings_manager.get('folders.writing_prompts', ""),
                QFileDialog.Option.ShowDirsOnly
            )

        if folder and os.path.exists(folder):
            try:
                categories_folder = os.path.join(folder, "categories")
                if not os.path.exists(categories_folder):
                    os.makedirs(categories_folder)
                
                self.prompts_service.set_prompt_folder(folder)
                folder_name = os.path.basename(folder)
                self.folder_label.setText(f"Prompts Folder: {folder_name}")
                self._update_categories()
                self.settings_manager.set('folders.writing_prompts', folder)
                saved_folder = self.settings_manager.get('folders.writing_prompts')
                if saved_folder != folder:
                    print(f"Warning: Folder save verification failed. Expected {folder}, got {saved_folder}")
            except Exception as e:
                print(f"Error setting prompts folder: {str(e)}")
                self.prompt_display.setPlainText(f"Error setting prompts folder: {str(e)}")

    def _update_categories(self):
        self.category_combo.clear()
        if not self.prompts_service.get_subfolders():
            return

        categories = self.prompts_service.get_subfolders()
        if categories:
            self.category_combo.addItems(categories)
        else:
            self.prompt_display.setPlainText(
                "No prompt categories found. Please add subdirectories with prompt files."
            )

    def _get_new_prompt(self):
        category = self.category_combo.currentText()
        if not category:
            QMessageBox.warning(self, "Error", "Please select a category first.")
            return
        
        prompt = self.prompts_service.get_new_prompt(category)
        if prompt:
            self.prompt_display.setPlainText(prompt)
        else:
            self.prompt_display.setPlainText("No prompts found in this category.")

    def _on_category_changed(self, category: str):
        if not category or not self.prompts_service.get_prompt_folder():
            return
        self.prompt_display.clear()
        self.prompt_display.setPlaceholderText("Click 'Get New Prompt' to start...")

    def _use_selected_prompt(self):
        prompt = self.prompt_display.toPlainText()
        if prompt and prompt != "No prompts found in this category.":
            self.prompt_selected.emit(prompt)

    def _clear_selected_prompt(self):
        self.prompt_display.clear()
        self.prompt_display.setPlaceholderText("Select a category and click 'Get New Prompt'...")
        
        self.category_combo.setCurrentIndex(-1)
        
        current_category = self.category_combo.currentText()
        if current_category:
            self.prompts_service.reset_tracking(current_category)
        
        self.prompt_selected.emit("")
