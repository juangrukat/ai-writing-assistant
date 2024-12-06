import os
from PyQt6.QtWidgets import QApplication
from pathlib import Path

class UIThemeManager:
    """Manages UI themes for the application."""

    def __init__(self, app: QApplication):
        self.app = app
        self.styles_dir = Path(__file__).parent.parent / 'resources' / 'styles'
        self.current_theme = None

    def get_available_themes(self) -> list[str]:
        themes = []
        for file in self.styles_dir.glob('*.qss'):
            if file.stem not in ['base', 'init']:
                themes.append(file.stem.capitalize())
        return sorted(themes)

    def apply_theme(self, theme_name: str) -> bool:
        try:
            theme_file = self.styles_dir / f"{theme_name.lower()}.qss"
            if not theme_file.exists():
                return False

            with open(theme_file, 'r') as f:
                stylesheet = f.read()

            if '@import' in stylesheet:
                base_file = self.styles_dir / 'base.qss'
                with open(base_file, 'r') as f:
                    base_style = f.read()
                stylesheet = stylesheet.replace("@import 'base.qss';", base_style)

            self.app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            return True
        except Exception as e:
            print(f"Error applying theme: {e}")
            return False

    def get_current_theme(self) -> str:
        return self.current_theme
