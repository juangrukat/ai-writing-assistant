from PyQt6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QTextBrowser, 
    QLineEdit, 
    QPushButton, 
    QHBoxLayout
)
from app.models.chat import Role
from app.services.ai_assistant_service import AIAssistantService
from app.services.settings_manager import SettingsManager
from app.utils.ui_utils import show_warning, show_confirmation, render_markdown

class AIAssistantTab(QWidget):
    """AI Assistant tab with chat interface."""

    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.setObjectName("AIAssistantTab")
        self.settings_manager = settings_manager
        self.ai_assistant_service = AIAssistantService(self.settings_manager)
        self.current_session_id = None
        self._create_ui()
        self._initialize_chat()

    def _initialize_chat(self):
        self.current_session_id = self.ai_assistant_service.initialize_chat()
        messages = self.ai_assistant_service.get_chat_messages(self.current_session_id)
        
        for message in messages:
            sender = "You" if message.role == Role.USER else "AI Assistant"
            self._append_message(sender, message.content)

    def _create_ui(self):
        layout = QVBoxLayout()

        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)

        layout.addLayout(input_layout)
        layout.addWidget(self.clear_button)
        
        self.setLayout(layout)

    def send_message(self):
        if not self.ai_assistant_service.is_initialized():
            show_warning(
                self,
                "API Key Missing",
                "Please set your OpenAI API key in the Settings tab."
            )
            return

        message = self.message_input.text().strip()
        if not message:
            return

        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.send_button.setText("Sending...")
        self.clear_button.setEnabled(False)
        
        self._append_message("System", "Processing request...")
        last_message_index = self.chat_display.document().lineCount() - 2

        try:
            response = self.ai_assistant_service.send_message(
                message=message,
                session_id=self.current_session_id
            )

            self._remove_last_message(last_message_index)

            if response:
                self._append_message("You", message)
                self._append_message("AI Assistant", response)
                self.message_input.clear()
            else:
                self._append_message("System", "Failed to get response from AI.")

        except Exception as e:
            self._remove_last_message(last_message_index)
            self._append_message("System", f"Error: {str(e)}")
        
        finally:
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.send_button.setText("Send")
            self.clear_button.setEnabled(True)
            self.message_input.setFocus()

    def _append_message(self, sender: str, message: str):
        if sender == "AI Assistant":
            message_html = render_markdown(message)
            self.chat_display.append(f"<b>{sender}:</b>")
            self.chat_display.append(message_html)
        else:
            self.chat_display.append(f"<b>{sender}:</b> {message}")

        self.chat_display.append("")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def clear_chat(self):
        if show_confirmation(
            self,
            "Clear Chat",
            "Are you sure you want to clear the chat history?"
        ):
            self.chat_display.clear()
            success = self.ai_assistant_service.clear_all_sessions()
            if not success:
                show_warning(
                    self,
                    "Error",
                    "Failed to clear chat history from storage."
                )
            self.current_session_id = self.ai_assistant_service.initialize_chat()
            
            messages = self.ai_assistant_service.get_chat_messages(self.current_session_id)
            for message in messages:
                sender = "You" if message.role == Role.USER else "AI Assistant"
                self._append_message(sender, message.content)

    def _remove_last_message(self, line_index: int):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        for _ in range(line_index):
            cursor.movePosition(cursor.MoveOperation.NextBlock)
        
        cursor.movePosition(cursor.MoveOperation.NextBlock, 
                            cursor.MoveMode.KeepAnchor, 2)
        cursor.removeSelectedText()
