from PyQt6.QtWidgets import QMessageBox, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
import markdown2
from app.views.widgets.loading_spinner import LoadingSpinner

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

class LoadingStateManager:
    def __init__(self, parent_widget: QWidget, target_button: QWidget):
        self.parent = parent_widget
        self.target = target_button
        self.overlay = QWidget(parent_widget)
        self.overlay.setLayout(QVBoxLayout())
        self.spinner = LoadingSpinner(self.overlay, size=24, color="#2196F3")
        self.overlay.layout().addWidget(self.spinner)
        self.overlay.hide()
        
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.overlay.setStyleSheet("background: transparent;")
    
    def start_loading(self):
        button_center = self.target.rect().center()
        global_pos = self.target.mapToGlobal(button_center)
        local_pos = self.parent.mapFromGlobal(global_pos)
        
        spinner_size = self.spinner.size
        self.overlay.setGeometry(
            local_pos.x() - spinner_size // 2,
            local_pos.y() - spinner_size // 2,
            spinner_size,
            spinner_size
        )
        
        self.overlay.show()
        self.spinner.start()
    
    def stop_loading(self):
        self.spinner.stop()
        self.overlay.hide()
