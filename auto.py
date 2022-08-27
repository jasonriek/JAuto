from PySide2.QtCore import (QObject, Signal, Slot)
import pyautogui as a

class Auto(QObject):
    xRead = Signal(int)
    yRead = Signal(int)
    posRead = Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x()
        self.y()

    def x(self):
        self.xRead.emit(int(a.position()[0]))
    
    def y(self):
        self.yRead.emit(int(a.position()[1]))
    
    @Slot()
    def pos(self):
        self.x()
        self.y()


