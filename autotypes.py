from enum import Enum

class StepTypes(Enum):
    MOVE = 0
    CLICK = 1
    TYPEWRITE = 2

class Mouse:
    LEFT_CLICK = "left"
    RIGHT_CLICK = "right" 

class MouseMove:
    def __init__(self):
        self.type = StepTypes.MOVE
        self.x = 0
        self.y = 0
        self.drag = False
    
    def position(self):
        return (self.x, self.y)

class MouseClick:
    def __init__(self):
        self.type = StepTypes.CLICK
        self.number_of_clicks = 1
        self.interval = 1 # Number of seconds between clicks
        self.button = Mouse.LEFT_CLICK

class KeyboardTypewrite:
    def __init__(self):
        self.type = StepTypes.TYPEWRITE
        self.text = ""
        self.key_names = []
        self.interval = 0.5

