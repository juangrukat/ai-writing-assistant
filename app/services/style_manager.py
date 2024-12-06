from PyQt6.QtCore import QFile, QTextStream
import os

class StyleManager:
    """Manages application styles and themes."""

    def __init__(self):
        self.style_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'styles')
        os.makedirs(self.style_dir, exist_ok=True)

    def load_style(self, style_name: str) -> str:
        style_file = os.path.join(self.style_dir, f"{style_name}.qss")
        if os.path.exists(style_file):
            with open(style_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def apply_style(self, widget, style_name: str):
        style = self.load_style(style_name)
        if style:
            widget.setStyleSheet(style)
