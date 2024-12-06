from PyQt6.QtGui import QFontDatabase
from pathlib import Path
import logging

class FontManager:
    def __init__(self):
        self.fonts_dir = Path("app/resources/fonts")
        self.available_fonts = []
        self.load_fonts()

    def load_fonts(self):
        if not self.fonts_dir.exists():
            self.fonts_dir.mkdir(parents=True)
            
        for font_file in self.fonts_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                self.available_fonts.extend(
                    QFontDatabase.applicationFontFamilies(font_id)
                )
                logging.info(f"Loaded font: {font_file.name}")
            else:
                logging.error(f"Failed to load font: {font_file.name}")

    def get_available_fonts(self):
        return self.available_fonts

    def get_system_fonts(self):
        return QFontDatabase().families()

    def get_default_font(self):
        if "Inter" in self.get_system_fonts():
            return "Inter"
        elif "Roboto" in self.get_system_fonts():
            return "Roboto"
        return QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()
