from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
import markdown2

class AIFeedbackTab(QWidget):
    """AI Feedback tab displaying feedback in Markdown format."""

    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        self.feedback_display = QTextBrowser()
        self.feedback_display.setOpenExternalLinks(True)
        self.feedback_display.setPlaceholderText("Your evaluated writing will be displayed here...")

        layout = QVBoxLayout()
        layout.addWidget(self.feedback_display)
        self.setLayout(layout)

    def display_feedback(self, feedback_markdown: str):
        if feedback_markdown:
            html_content = markdown2.markdown(feedback_markdown)
            self.feedback_display.setHtml(html_content)
        else:
            self.feedback_display.setHtml("<p>Error: No feedback received</p>")
