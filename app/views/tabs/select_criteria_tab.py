from PyQt6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QPushButton, 
    QLabel, 
    QComboBox, 
    QTextEdit, 
    QFileDialog
)
from PyQt6.QtCore import pyqtSignal
import os
import json
from app.services.settings_manager import SettingsManager

class SelectCriteriaTab(QWidget):
    """Tab for selecting and managing content criteria."""

    criteria_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.criteria_folder = None
        self.selected_criteria = None
        self.setup_ui()
        self._restore_last_folder()

    def setup_ui(self):
        layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Criteria Folder: Not selected")
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_folder_btn)
        layout.addLayout(folder_layout)

        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Criteria Type:"))
        self.type_combo = QComboBox()
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        set_layout = QHBoxLayout()
        set_layout.addWidget(QLabel("Criteria Set:"))
        self.set_combo = QComboBox()
        self.set_combo.currentTextChanged.connect(self._on_set_changed)
        set_layout.addWidget(self.set_combo)
        layout.addLayout(set_layout)

        self.criteria_display = QTextEdit()
        self.criteria_display.setReadOnly(True)
        self.criteria_display.setPlaceholderText("Select a criteria set to view details...")
        layout.addWidget(self.criteria_display)

        self.setLayout(layout)

    def _restore_last_folder(self):
        folder = self.settings_manager.get('folders.criteria')
        if folder and os.path.exists(folder):
            self.select_folder(folder)

    def _restore_last_set_with_verification(self, last_set: str, last_file_path: str):
        index = self.set_combo.findText(last_set)
        if index >= 0:
            self.set_combo.setCurrentIndex(index)
            try:
                with open(last_file_path, 'r', encoding='utf-8') as f:
                    if last_file_path.endswith('.json'):
                        criteria_content = json.dumps(json.load(f), indent=2)
                    else:
                        criteria_content = f.read()
                    self.criteria_display.setPlainText(criteria_content)
                    self.selected_criteria = criteria_content
                    self.criteria_selected.emit(criteria_content)
            except Exception as e:
                print(f"Error restoring criteria content: {str(e)}")

    def select_folder(self, folder: str = None):
        if not folder:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Criteria Folder",
                self.settings_manager.get('folders.criteria', ""),
                QFileDialog.Option.ShowDirsOnly
            )

        if folder and os.path.exists(folder):
            try:
                templates_folder = os.path.join(folder, "templates")
                if not os.path.exists(templates_folder):
                    os.makedirs(templates_folder)
                
                self.criteria_folder = folder
                folder_name = os.path.basename(folder)
                self.folder_label.setText(f"Criteria Folder: {folder_name}")
                self._update_criteria_types()
                self.settings_manager.set('folders.criteria', folder)
            except Exception as e:
                print(f"Error setting criteria folder: {str(e)}")
                self.criteria_display.setPlainText(f"Error setting criteria folder: {str(e)}")

    def _update_criteria_types(self):
        self.type_combo.clear()
        self.set_combo.clear()
        if not self.criteria_folder:
            return

        try:
            self.type_combo.blockSignals(True)
            self.set_combo.blockSignals(True)

            subfolders = [d for d in os.listdir(self.criteria_folder) 
                          if os.path.isdir(os.path.join(self.criteria_folder, d))]

            if subfolders:
                self.type_combo.addItems(subfolders)
                last_type = self.settings_manager.get('criteria.last_type')
                if last_type in subfolders:
                    index = self.type_combo.findText(last_type)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                        subfolder_path = os.path.join(self.criteria_folder, last_type)
                        self._update_criteria_sets(subfolder_path, is_restoration=True)
            else:
                self._update_criteria_sets(self.criteria_folder, is_restoration=True)

            self.type_combo.blockSignals(False)
            self.set_combo.blockSignals(False)
                
        except Exception as e:
            print(f"Error updating criteria types: {str(e)}")
            self.criteria_display.setPlainText(f"Error loading criteria types: {str(e)}")

    def _update_criteria_sets(self, folder_path: str, is_restoration: bool = False):
        try:
            criteria_files = [f for f in os.listdir(folder_path)
                              if f.endswith(('.txt', '.md', '.json'))]

            if not is_restoration:
                self.set_combo.blockSignals(True)

            self.set_combo.clear()
            
            if criteria_files:
                criteria_sets = [os.path.splitext(f)[0] for f in criteria_files]
                self.set_combo.addItems(criteria_sets)
                
                if is_restoration:
                    last_set = self.settings_manager.get('criteria.last_set')
                    last_file_path = self.settings_manager.get('criteria.last_file_path')
                    
                    if last_set in criteria_sets:
                        for file in criteria_files:
                            if os.path.splitext(file)[0] == last_set:
                                current_file_path = os.path.join(folder_path, file)
                                if current_file_path == last_file_path or not last_file_path:
                                    index = self.set_combo.findText(last_set)
                                    if index >= 0:
                                        self.set_combo.setCurrentIndex(index)
                                        self._load_criteria_content(current_file_path)

            if not is_restoration:
                self.set_combo.blockSignals(False)
                
        except Exception as e:
            print(f"Error updating criteria sets: {str(e)}")

    def _load_criteria_content(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    criteria_content = json.dumps(json.load(f), indent=2)
                else:
                    criteria_content = f.read()
                
                self.criteria_display.setPlainText(criteria_content)
                self.selected_criteria = criteria_content
                self.criteria_selected.emit(criteria_content)
                self.settings_manager.set('criteria.last_file_path', file_path)
        except Exception as e:
            print(f"Error loading criteria content: {str(e)}")

    def _on_type_changed(self, criteria_type: str):
        if not criteria_type or not self.criteria_folder:
            return

        self.settings_manager.set('criteria.last_type', criteria_type)

        subfolder_path = os.path.join(self.criteria_folder, criteria_type)
        if os.path.exists(subfolder_path):
            self._update_criteria_sets(subfolder_path)

    def _on_set_changed(self, criteria_set: str):
        if not criteria_set or not self.criteria_folder:
            return

        try:
            self.settings_manager.set('criteria.last_set', criteria_set)
            current_type = self.type_combo.currentText()
            current_folder = os.path.join(self.criteria_folder, current_type) if current_type else self.criteria_folder

            for ext in ['.txt', '.md', '.json']:
                file_path = os.path.join(current_folder, f"{criteria_set}{ext}")
                if os.path.exists(file_path):
                    self.settings_manager.set('criteria.last_file_path', file_path)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if ext == '.json':
                            criteria_content = json.dumps(json.load(f), indent=2)
                        else:
                            criteria_content = f.read()
                    
                    self.criteria_display.setPlainText(criteria_content)
                    self.selected_criteria = criteria_content
                    self.criteria_selected.emit(criteria_content)
                    break
            else:
                self.criteria_display.setPlainText("Error: Criteria file not found.")
                self.selected_criteria = None
                self.settings_manager.set('criteria.last_file_path', '')

        except Exception as e:
            print(f"Error loading criteria content: {str(e)}")
            self.criteria_display.setPlainText(f"Error loading criteria: {str(e)}")
            self.selected_criteria = None
            self.settings_manager.set('criteria.last_file_path', '')

    def get_selected_criteria(self) -> str:
        return self.selected_criteria if self.selected_criteria else ""
