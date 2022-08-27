import sys 
from PySide2.QtWidgets import (QWidget, QApplication, QPushButton, QMainWindow, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout)
from PySide2.QtCore import (Qt, QRect, QTimer, Slot, Signal)
from PySide2.QtGui import (QPainter, QColor, QFont)


class Overlay(QWidget):
    overlayClosed = Signal(str, object)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.setStyleSheet("""
            color: #EFEFEF;
            background-color: rgba(0, 0, 0, 0.4);

        """)
        font = QFont()
        font.setPixelSize(48)

        self.current_pos = (0, 0)
        self.pos_label = QLabel("(0, 0)", self)
        self.pos_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pos_label.setFont(font)
        self.pos_label.setAlignment(Qt.AlignCenter)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.main_layout.addWidget(self.pos_label)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.overlayClosed.emit(self.pos_label.text(), self.current_pos)
            self.close()
        return super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.overlayClosed.emit(self.pos_label.text(), self.current_pos)
            self.close()
        return super().keyPressEvent(event)
    
    def setPosLabel(self, pos):
        self.pos_label.setText(f"({pos[0]}, {pos[1]})")
        self.current_pos = pos 
    
    def getPosition(self):
        return self.pos_label.text()

