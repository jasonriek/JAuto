import sys 
from PySide2.QtWidgets import (QApplication)
from window import Window

"""
TO ADD:It was quite a day. The world had decided to unleash sadness throughout the land.
I somehow came out of it unscathed. During this time I have to know my strengths and weaknesses more.
I need to take more notes when being taught.
    -Test move option in right click context menu
"""

def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()