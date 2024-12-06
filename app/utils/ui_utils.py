from PyQt6.QtWidgets import QMessageBox
import markdown2

def show_warning(parent, title: str, message: str):
    QMessageBox.warning(parent, title, message)

def show_info(parent, title: str, message: str):
    QMessageBox.information(parent, title, message)

def show_confirmation(parent, title: str, message: str) -> bool:
    reply = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes

def render_markdown(text: str) -> str:
    try:
        return markdown2.markdown(text)
    except Exception as e:
        print(f"Error rendering markdown: {e}")
        return text
