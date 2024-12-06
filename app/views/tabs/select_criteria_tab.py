from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
import os
import json
import logging
from pathlib import Path
from app.services.settings_manager import SettingsManager

class SelectCriteriaTab(QWidget):
    """Tab for selecting and managing evaluation criteria."""

    criteria_selected = pyqtSignal(str)
    SUPPORTED_EXTENSIONS = ('.txt', '.md', '.json')

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.criteria_folder: Optional[Path] = None
        self.selected_criteria: Optional[str] = None
        self._setup_ui()
        self._restore_last_folder()

    def _setup_ui(self):
        """Initialize and setup the UI components."""
        layout = QVBoxLayout()
        
        # Folder selection section
        layout.addLayout(self._create_folder_section())
        
        # Criteria type section
        layout.addLayout(self._create_type_section())
        
        # Criteria set section
        layout.addLayout(self._create_set_section())
        
        # Criteria display
        self.criteria_display = QTextEdit()
        self.criteria_display.setReadOnly(True)
        self.criteria_display.setPlaceholderText("Select a criteria set to view details...")
        layout.addWidget(self.criteria_display)
        
        self.setLayout(layout)

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
