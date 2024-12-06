from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout, QFileDialog, QLabel, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
import os
from datetime import datetime
from app.services.content_combiner_service import ContentCombinerService
from app.services.ai_feedback_service import AIFeedbackService
from app.services.settings_manager import SettingsManager

class MiddlePanel(QWidget):
    """Middle panel containing the text editor and controls."""
    
    save_location_changed = pyqtSignal(str)

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.save_location = None
        self.content_combiner = ContentCombinerService()
        self.selected_prompt = None
        self._create_ui()
        self._restore_last_folder()
        self._initialize_services()

    def _initialize_services(self):
        self.ai_feedback_service = AIFeedbackService()

    def _create_ui(self):
        layout = QVBoxLayout()

        save_location_layout = QHBoxLayout()
        self.save_location_label = QLabel("Save Location: Not selected")
        self.select_save_location_btn = QPushButton("Select Save Location")
        self.select_save_location_btn.clicked.connect(self.select_save_location)
        save_location_layout.addWidget(self.save_location_label)
        save_location_layout.addWidget(self.select_save_location_btn)
        layout.addLayout(save_location_layout)

        status_layout = QHBoxLayout()
        self.prompt_status_label = QLabel("No Prompt Selected")
        status_layout.addWidget(self.prompt_status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Write here...")
        layout.addWidget(self.text_editor)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_text)

        self.submit_button = QPushButton("Submit for Feedback")
        self.submit_button.clicked.connect(self.submit_for_feedback)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_text)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def _restore_last_folder(self):
        folder = self.settings_manager.get('folders.save_location')
        if folder and os.path.exists(folder):
            self.select_save_location(folder)

    def select_save_location(self, folder: str = None):
        if not folder:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Save Location",
                self.settings_manager.get('folders.save_location', ""),
                QFileDialog.Option.ShowDirsOnly
            )

        if folder and os.path.exists(folder):
            self.save_location = folder
            folder_name = os.path.basename(folder)
            self.save_location_label.setText(f"Save Location: {folder_name}")
            chats_folder = os.path.join(folder, "chats")
            if not os.path.exists(chats_folder):
                os.makedirs(chats_folder)
            self.save_location_changed.emit(chats_folder)
            self.settings_manager.set('folders.save_location', folder)

    def generate_filename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"submission_{timestamp}.txt"

    def save_text(self):
        if not self.save_location:
            QMessageBox.warning(
                self,
                "Save Location Not Set",
                "Please select a save location first."
            )
            return

        text = self.text_editor.toPlainText()
        if not text.strip():
            QMessageBox.warning(
                self,
                "Empty Text",
                "Cannot save empty text."
            )
            return

        try:
            filename = self.generate_filename()
            file_path = os.path.join(self.save_location, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)

            QMessageBox.information(
                self,
                "Success",
                f"File saved successfully as:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )

    def submit_for_feedback(self):
        submission = self.text_editor.toPlainText()
        if not submission.strip():
            QMessageBox.warning(self, "Error", "Please enter some text before requesting feedback.")
            return

        self.submit_button.setEnabled(False)
        self.submit_button.setText("Getting Feedback...")
        self.text_editor.setReadOnly(True)
        
        try:
            right_panel = self.window().right_panel
            if right_panel:
                select_criteria_tab = right_panel.select_criteria_tab
                selected_criteria = select_criteria_tab.get_selected_criteria()
                if not selected_criteria:
                    selected_criteria = "Default criteria"

                feedback = self.ai_feedback_service.get_feedback(
                    submission=submission,
                    criteria=selected_criteria,
                    prompt=self.selected_prompt
                )

                if feedback:
                    ai_feedback_tab = right_panel.ai_feedback_tab
                    if ai_feedback_tab:
                        ai_feedback_tab.display_feedback(feedback)
                    else:
                        QMessageBox.warning(self, "Error", "AI Feedback tab not found.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to get feedback from AI.")
        finally:
            self.submit_button.setEnabled(True)
            self.submit_button.setText("Submit for Feedback")
            self.text_editor.setReadOnly(False)

    def clear_text(self, force: bool = False):
        if not force and self.text_editor.toPlainText().strip():
            reply = QMessageBox.question(
                self,
                "Clear Text",
                "Are you sure you want to clear all text? This cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.text_editor.clear()
        else:
            self.text_editor.clear()

    def set_selected_prompt(self, prompt: str):
        if prompt:
            self.selected_prompt = prompt
            truncated_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt
            self.prompt_status_label.setText(f"Using Prompt: {truncated_prompt}")
            self.prompt_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.selected_prompt = None
            self.prompt_status_label.setText("No Prompt Selected")
            self.prompt_status_label.setStyleSheet("")
            self.clear_text(force=True)
