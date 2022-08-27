from PySide2.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QListView, QHBoxLayout, QLabel, QFileDialog, 
                               QPushButton, QAction, QMenu, QMenuBar, QMessageBox)
from PySide2.QtCore import (QThread, QEvent, QTimer)
from PySide2.QtGui import (QStandardItemModel, QStandardItem, QKeySequence)
import pyautogui as a
from overlay import (Overlay, QSizePolicy, Signal, Slot, Qt)
from autotypes import (Mouse, MouseMove, MouseClick, StepTypes, KeyboardTypewrite)
import os 
import csv 

class Settings:
    SAVE_DIR = 'Automation_Saves'

class FileColumns:
    NAME = 0
    class MouseMove:
        X = 1
        Y = 2
        DRAG = 3
    class MouseClick:
        NUMBER_OF_CLICKS = 1
        INTERVAL = 2
        BUTTON = 3

class Window(QMainWindow):
    mouseMoved = Signal()
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.steps = []
        self.saved = False
        self.save_path = "" 

        # Settings
        # --------------------------------------------
        self.setMouseTracking(True)
        self.setWindowTitle("JAuto")
        # --------------------------------------------

        # Auto Settings
        # --------------------------------------------
        a.PAUSE = 1
        a.FAILSAFE = True 
        # --------------------------------------------


        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.overlay_window = Overlay()
        self.setStepsList()
        self.overlay_window.overlayClosed.connect(self.loadMouseMove)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.setLabel)
        self.timer.start(10)

        self.get_pos_button = QPushButton("Set Move Position", self)
        self.get_pos_button.clicked.connect(self.addMouseMove)

        self.add_click_button = QPushButton("Add Mouse Click", self)
        self.add_click_button.clicked.connect(self.loadMouseClick)

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.runSteps)
        self.rmv_button = QPushButton("Remove", self)
        self.rmv_button.clicked.connect(self.removeMove)

        self.main_layout.addWidget(self.steps_list)
        self.main_layout.addWidget(self.get_pos_button)
        self.main_layout.addWidget(self.add_click_button)
        self.main_layout.addWidget(self.rmv_button)
        self.main_layout.addWidget(self.run_button)

        self.setCentralWidget(self.main_widget)
        self.topMenu()
    
    def setStepsList(self):
        self.model = QStandardItemModel(self)
        self.steps_list = QListView(self)
        self.steps_list.setAlternatingRowColors(True)
    
    def addMouseMove(self):
        self.overlay_window.showFullScreen()

    def topMenu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        self.new_action = QAction("New", self)
        
        self.new_action.setShortcut(QKeySequence.New)
        self.open_action = QAction("Open...", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setDisabled(True)
        self.saveAs_action = QAction("Save As...", self)
        self.saveAs_action.setShortcut(QKeySequence.SaveAs)
        self.exit_action = QAction("Exit", self)

        # Set the action methods
        self.new_action.triggered.connect(self.new)
        self.open_action.triggered.connect(self.open)
        self.save_action.triggered.connect(self.save)
        self.saveAs_action.triggered.connect(self.saveAs)
        self.exit_action.triggered.connect(self.close)

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.saveAs_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

    def closeEvent(self, event):
        msg_selection = self.closeWarning()
        if msg_selection == QMessageBox.Cancel:
            event.ignore()
        else:
            event.accept()

    def errorMessageBox(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(str(message))
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        msg_selection = msg.exec_()

    def setNewModel(self):
        self.model = QStandardItemModel(self)
        if len(self.steps):
            for step in self.steps:
                if step.type.name == StepTypes.MOVE.name:
                    item = QStandardItem(f"Move cursor to {str(step.position())}")
                elif step.type.name == StepTypes.CLICK.name:
                    item = QStandardItem("Click Mouse")
                self.model.appendRow(item)
        self.steps_list.setModel(self.model)


    def resetSaved(self):
        self.saved = False
        self.save_path = ""
        self.save_action.setDisabled(True)
    
    def resetSteps(self):
        self.steps.clear()
        self.model = QStandardItemModel(self)
        self.steps_list.setModel(self.model)

    @Slot()
    def new(self):
        try:
            # ERASE WARNING
            if len(self.steps):
                warn_msg = QMessageBox(QMessageBox.Warning, "Erase Steps Warning", "This will overwrite the current steps, proceed?", QMessageBox.Yes | QMessageBox.No, self)
                msg_selection = warn_msg.exec_()
                if msg_selection == QMessageBox.No:
                    return
                else:
                    self.resetSteps()
                    self.resetSaved()

        except Exception as error:
            self.errorMessageBox("New Error", error)

    @Slot()
    def open(self):
        try:
            # ERASE WARNING
            if len(self.steps):
                warn_msg = QMessageBox(QMessageBox.Warning, "Erase Steps Warning", "This will overwrite the current steps, proceed?", QMessageBox.Yes | QMessageBox.No, self)
                msg_selection = warn_msg.exec_()
                if msg_selection == QMessageBox.No:
                    return

            step = None 
            path, _ = QFileDialog.getOpenFileName(self, "Open Automation Steps", Settings.SAVE_DIR, 'CSV (*.csv);')
            if path:
                self.steps.clear()
                self.save_path = path
                with open(self.save_path, 'r', encoding='utf8') as af:
                    reader = csv.reader(af)
                    for line in reader:
                        step_type = line[FileColumns.NAME]
                        if step_type == StepTypes.MOVE.name:
                            step = MouseMove()
                            step.x = int(line[FileColumns.MouseMove.X])
                            step.y = int(line[FileColumns.MouseMove.Y])
                            step.drag = ('True' == line[FileColumns.MouseMove.DRAG])
                        elif step_type == StepTypes.CLICK.name:
                            step = MouseClick()
                            step.number_of_clicks = int(line[FileColumns.MouseClick.NUMBER_OF_CLICKS])
                            step.interval = float(line[FileColumns.MouseClick.INTERVAL])
                            step.button = line[FileColumns.MouseClick.BUTTON]
                        else:
                            continue

                        self.steps.append(step) 
                self.setNewModel()
                self.saved = True 
                self.save_action.setEnabled(True) 
                                
        except Exception as error:
            self.errorMessageBox("Open Error", error)

    @Slot()    
    def save(self):
        try:
            step_row = []
            with open(self.save_path, 'w', encoding='utf8', newline='') as af:
                writer = csv.writer(af)
                for step in self.steps:
                    step_row.append(step.type.name)
                    if step.type == StepTypes.MOVE:
                        step_row.extend([step.x, step.y, step.drag])
                    elif step.type == StepTypes.CLICK:
                        step_row.extend([step.number_of_clicks, step.interval, step.button])
                    elif step.type == StepTypes.TYPEWRITE:
                        pass 
                    writer.writerow(step_row)
                    step_row.clear()    
        except Exception as error:
            self.errorMessageBox("Save Error", error)

    @Slot()
    def saveAs(self):
        # Create Steps dir
        if not os.path.isdir(Settings.SAVE_DIR):
            os.mkdir(Settings.SAVE_DIR)

        path, _ = QFileDialog.getSaveFileName(self, 'Save Automation Steps', Settings.SAVE_DIR, 'CSV (*.csv);')
        if path:
            self.save_path = path
            self.save()
            self.saved = True
            self.save_action.setEnabled(True) 

    @Slot()
    def closeWarning(self):
        msg_selection = QMessageBox.No
        msg = QMessageBox()
        if len(self.steps) and not self.saved:
            msg.setWindowTitle("Save?")
            msg.setText("Automation steps not saved, would you like to save?")
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg_selection = msg.exec_()
            if msg_selection == QMessageBox.Yes:
                if self.save_path:
                    self.save()
                else:
                    self.saveAs()

        return msg_selection

    @Slot(str, object)
    def loadMouseMove(self, mouse_coord_text, mouse_coord):
        item = QStandardItem(f"Move cursor to {mouse_coord_text}")
        self.model.appendRow(item)
        mouse_move = MouseMove()
        mouse_move.x = mouse_coord.x
        mouse_move.y = mouse_coord.y
        self.steps.append(mouse_move)
        self.steps_list.setModel(self.model)
        self.saved = False
    
    @Slot()
    def loadMouseClick(self):
        item = QStandardItem("Click Mouse")
        self.model.appendRow(item)
        mouse_click = MouseClick()
        keyboard = KeyboardTypewrite()
        keyboard.text = "It was quite a day. The world had decided to unleash sadness throughout the land.\nI somehow came out of it unscathed. During this time I have to know my strengths and weaknesses more.\nI need to take more notes when being taught."
        self.steps.append(mouse_click)
        self.steps.append(keyboard)
        self.steps_list.setModel(self.model)
        self.saved = False
        
    @Slot()        
    def setLabel(self):
        self.overlay_window.setPosLabel(a.position())
    
    @Slot()
    def runSteps(self):
        self.hide()
        try:
            for step in self.steps:
                if step.type == StepTypes.MOVE:
                    if step.drag:
                        a.dragTo(step.x, step.y, 1)
                    else:
                        a.moveTo(step.x, step.y, 1)

                elif step.type == StepTypes.CLICK:
                    a.click(clicks=step.number_of_clicks, interval=step.interval, button=step.button)
                elif step.type == StepTypes.TYPEWRITE:
                    a.typewrite(step.text)

        except Exception as error:
            print(error)
        finally:
            self.show()
    
    @Slot()
    def removeMove(self):
        if self.steps_list.selectionModel() is not None:
            if self.steps_list.selectionModel().hasSelection() and len(self.steps):
                index = self.steps_list.selectionModel().currentIndex()
                self.steps.pop(index.row())
                self.setNewModel()



