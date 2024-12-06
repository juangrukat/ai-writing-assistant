from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=32, num_dots=8, color="#748FFC"):
        super().__init__(parent)
        
        self.size = size
        self.num_dots = num_dots
        self.color = QColor(color)
        self.rotation = 0
        self.is_spinning = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        
        self.setFixedSize(QSize(size, size))
        self.hide()
    
    def rotate(self):
        self.rotation += 360 / self.num_dots
        self.update()
    
    def start(self):
        self.show()
        self.is_spinning = True
        self.timer.start(100)
    
    def stop(self):
        self.is_spinning = False
        self.timer.stop()
        self.hide()
    
    def paintEvent(self, event):
        if not self.is_spinning:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.rect().center()
        radius = int((self.size - 16) / 2)
        dot_size = 4
        
        painter.translate(center)
        painter.rotate(self.rotation)
        
        for i in range(self.num_dots):
            opacity = 1.0 - (i / self.num_dots)
            color = QColor(self.color)
            color.setAlphaF(opacity)
            
            pen = QPen(color, dot_size, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            
            angle = (360 * i) / self.num_dots
            painter.save()
            painter.rotate(angle)
            painter.drawPoint(int(radius), 0)
            painter.restore()
