#!/usr/bin/env python3

from os import path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenuBar, QToolBar


class MenuBar(QMenuBar):

    save_note = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_menu()

    def init_menu(self):
        file = self.addMenu('File')
        edit = self.addMenu('Edit')

        new_note = QAction('&New Note', self)
        new_note.setShortcut('Ctrl+N')

        save_note = QAction('&Save_Note', self)
        save_note.setShortcut('Ctrl+S')
        save_note.triggered.connect(self.save_note.emit)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')

        preferences_action = QAction('&Preferences', self)
        preferences_action.setShortcut('Ctrl+P')

        file.addAction(new_note)
        file.addAction(save_note)
        file.addAction(quit_action)

        edit.addAction(preferences_action)


class ToolBar(QToolBar):

    save_note = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_menu()

    def init_menu(self):
        script_dir = path.dirname(path.realpath(__file__))
        path_to_icon_dir = path.join(script_dir, "..", "icons")

        self.new_action = QAction(
            QIcon(path.join(path_to_icon_dir, "new_note.png")),
            "New",
            self)
        self.new_action.setStatusTip("Create a new note.")

        self.save_action = QAction(
            QIcon(path.join(path_to_icon_dir, "save_note.png")),
            "Save",
            self)
        self.save_action.setStatusTip("Save the note.")
        self.save_action.triggered.connect(self.save_note.emit)

        self.addAction(self.new_action)
        self.addAction(self.save_action)
