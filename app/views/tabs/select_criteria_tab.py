from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
import os
import json
import logging
from pathlib import Path
from typing import Optional
from app.services.settings_manager import SettingsManager
from app.config.criteria_config import CriteriaConfig

class SelectCriteriaTab(QWidget):
    """Tab for selecting and managing evaluation criteria."""

    criteria_selected = pyqtSignal(str)
    SUPPORTED_EXTENSIONS = ('.txt', '.md', '.json')

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.criteria_folder: Optional[Path] = None
        self.selected_criteria: Optional[str] = None
        self.config = CriteriaConfig()
        self._setup_ui()
        self._restore_last_folder()

    def _setup_ui(self):
        """Initialize and setup the UI components."""
        layout = QVBoxLayout()
        layout.addLayout(self._create_folder_section())
        layout.addLayout(self._create_type_section())
        layout.addLayout(self._create_set_section())
        
        self.criteria_display = QTextEdit()
        self.criteria_display.setReadOnly(True)
        self.criteria_display.setPlaceholderText(self.config.PLACEHOLDER_TEXT)
        layout.addWidget(self.criteria_display)
        
        self.setLayout(layout)

    def select_folder(self, folder: str = None):
        """Handle folder selection for criteria."""
        if not folder:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Criteria Folder",
                self.settings_manager.get('folders.criteria', ""),
                QFileDialog.Option.ShowDirsOnly
            )

        if folder and os.path.exists(folder):
            try:
                self.criteria_folder = folder
                folder_name = os.path.basename(folder)
                self.folder_label.setText(f"Criteria Folder: {folder_name}")
                
                self._save_and_verify_settings('folders.criteria', folder)
                
                self.type_combo.blockSignals(True)
                self.type_combo.clear()
                
                subfolders = [d for d in os.listdir(folder) 
                             if os.path.isdir(os.path.join(folder, d))]
                
                if subfolders:
                    self.type_combo.addItems(subfolders)
                    self.type_combo.blockSignals(False)
                    self.type_combo.setCurrentIndex(0)
                    first_type = self.type_combo.currentText()
                    self._on_type_changed(first_type)
                else:
                    self.type_combo.blockSignals(False)
                    self._update_criteria_sets(folder)
                    
            except Exception as e:
                self.criteria_display.setPlainText(f"Error setting criteria folder: {str(e)}")

    def _on_type_changed(self, criteria_type: str):
        """Handle criteria type selection."""
        if not criteria_type or not self.criteria_folder:
            return

        subfolder_path = os.path.join(self.criteria_folder, criteria_type)
        
        if not os.path.exists(subfolder_path):
            self.criteria_display.setPlainText("Error: Selected criteria type folder no longer exists.")
            self.set_combo.clear()
            self._clear_criteria_settings()
            return

        self._save_and_verify_settings('criteria.last_type', criteria_type)
        self._update_criteria_sets(subfolder_path)

    def _update_criteria_sets(self, folder_path: str, is_restoration: bool = False):
        """Update the criteria sets dropdown based on folder contents."""
        try:
            criteria_files = self._get_criteria_files(folder_path)

            self.set_combo.blockSignals(True)
            self.set_combo.clear()
            
            if criteria_files:
                criteria_sets = [os.path.splitext(f)[0] for f in criteria_files]
                self.set_combo.addItems(criteria_sets)
                
                if is_restoration:
                    last_set = self.settings_manager.get('criteria.last_set', {})
                    if last_set and last_set.get('file_path'):
                        if os.path.exists(last_set['file_path']):
                            name = last_set['name']
                            if name in criteria_sets:
                                index = self.set_combo.findText(name)
                                if index >= 0:
                                    self.set_combo.setCurrentIndex(index)
                                    self._load_criteria_content(last_set['file_path'])

            self.set_combo.blockSignals(False)
            
            # Auto-select first item if none selected
            if self.set_combo.count() > 0 and self.set_combo.currentText() == "":
                self.set_combo.setCurrentIndex(0)
                self._on_set_changed(self.set_combo.currentText())
                
        except Exception as e:
            logging.error(f"Error updating criteria sets: {str(e)}")

    def _on_set_changed(self, criteria_set: str):
        """Handle criteria set selection."""
        if not criteria_set or not self.criteria_folder:
            return

        try:
            current_type = self.type_combo.currentText()
            current_folder = os.path.join(self.criteria_folder, current_type) if current_type else self.criteria_folder
            
            if not os.path.exists(current_folder):
                self.criteria_display.setPlainText("Error: Selected folder no longer exists.")
                self._clear_criteria_settings()
                return

            file_found = False
            for ext in self.SUPPORTED_EXTENSIONS:
                file_path = os.path.join(current_folder, f"{criteria_set}{ext}")
                if os.path.exists(file_path):
                    self._load_criteria_content(file_path)
                    file_found = True
                    break
            
            if not file_found:
                self.criteria_display.setPlainText("Error: Selected criteria file no longer exists.")
                self._clear_criteria_settings()
                self.selected_criteria = None

        except Exception as e:
            print(f"Error loading criteria content: {str(e)}")
            self._clear_criteria_settings()

    def _create_folder_section(self) -> QHBoxLayout:
        """Create the folder selection section of the UI."""
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Criteria Folder: Not selected")
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_folder_btn)
        return folder_layout

    def _create_type_section(self) -> QHBoxLayout:
        """Create the criteria type selection section."""
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Criteria Type:"))
        self.type_combo = QComboBox()
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        return type_layout

    def _create_set_section(self) -> QHBoxLayout:
        """Create the criteria set selection section."""
        set_layout = QHBoxLayout()
        set_layout.addWidget(QLabel("Criteria Set:"))
        self.set_combo = QComboBox()
        self.set_combo.currentTextChanged.connect(self._on_set_changed)
        set_layout.addWidget(self.set_combo)
        return set_layout

    def _save_and_verify_settings(self, key: str, value: any) -> bool:
        """Save settings and verify they were saved correctly."""
        self.settings_manager.set(key, value)
        self.settings_manager.save_settings()
        
        # Verify save
        saved_value = self.settings_manager.get(key)
        if saved_value != value:
            logging.warning(f"Settings save verification failed for {key}. Expected {value}, got {saved_value}")
            # Retry save
            self.settings_manager.set(key, value)
            self.settings_manager.save_settings()
            return False
        return True

    def _get_criteria_files(self, folder_path: Path) -> list[str]:
        """Get list of criteria files in the given folder."""
        return [f for f in os.listdir(folder_path)
                if f.endswith(self.SUPPORTED_EXTENSIONS)]

    def _extract_description(self, content: str, file_type: str) -> str:
        """Extract description from criteria content."""
        if file_type == 'json':
            return content.get('description', '')
        else:
            lines = content.split('\n')
            return lines[0][1:].strip() if lines and lines[0].startswith('#') else ''

    def closeEvent(self, event):
        """Ensure settings are saved before closing."""
        try:
            self.settings_manager.save_settings()
        except Exception as e:
            logging.error(f"Error saving settings on close: {e}")
        super().closeEvent(event)

    def get_selected_criteria(self) -> str:
        """Get the currently selected criteria content."""
        return self.selected_criteria if self.selected_criteria else ""

    def _restore_last_folder(self):
        """Restores the last selected folder and its state."""
        folder = self.settings_manager.get('folders.criteria')
        if folder and os.path.exists(folder):
            self.criteria_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.setText(f"Criteria Folder: {folder_name}")
            
            # Restore type
            last_type = self.settings_manager.get('criteria.last_type')
            last_set = self.settings_manager.get('criteria.last_set', {})
            
            # Update type combo box
            self.type_combo.blockSignals(True)
            self.type_combo.clear()
            
            subfolders = [d for d in os.listdir(folder) 
                         if os.path.isdir(os.path.join(folder, d))]
            if subfolders:
                self.type_combo.addItems(subfolders)
                
                if last_type and last_type in subfolders:
                    index = self.type_combo.findText(last_type)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                else:
                    self.type_combo.setCurrentIndex(0)
                    last_type = self.type_combo.currentText()
            
            self.type_combo.blockSignals(False)
            
            # Now restore the set if we have a valid type
            if last_type:
                subfolder_path = os.path.join(folder, last_type)
                if os.path.exists(subfolder_path):
                    self._update_criteria_sets(subfolder_path, is_restoration=True)

    def _load_criteria_content(self, file_path: str):
        """Load and display criteria content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_type = os.path.splitext(file_path)[1][1:]  # Get extension without dot
                if file_path.endswith('.json'):
                    content = json.load(f)
                    criteria_content = json.dumps(content, indent=2)
                    description = content.get('description', '')
                else:
                    criteria_content = f.read()
                    lines = criteria_content.split('\n')
                    description = lines[0][1:].strip() if lines and lines[0].startswith('#') else ''
                
                self.criteria_display.setPlainText(criteria_content)
                self.selected_criteria = criteria_content
                self.criteria_selected.emit(criteria_content)
                
                # Update settings with full criteria information
                current_type = self.type_combo.currentText()
                criteria_name = os.path.splitext(os.path.basename(file_path))[0]
                
                criteria_info = {
                    "name": criteria_name,
                    "description": description,
                    "category": current_type,
                    "file_path": file_path,
                    "file_type": file_type
                }
                
                self._save_and_verify_settings('criteria.last_set', criteria_info)
                
        except Exception as e:
            print(f"Error loading criteria content: {str(e)}")
            self._clear_criteria_settings()

    def _clear_criteria_settings(self):
        """Helper method to clear criteria settings."""
        empty_set = {
            "name": "",
            "description": "",
            "category": "",
            "file_path": "",
            "file_type": ""
        }
        self._save_and_verify_settings('criteria.last_set', empty_set)
