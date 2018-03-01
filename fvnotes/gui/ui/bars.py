#!/usr/bin/env python3

from os import path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenuBar, QToolBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_menu()

    def init_menu(self):
        file = self.addMenu('File')
        edit = self.addMenu('Edit')

        new_note = QAction('&New Note', self)
        new_note.setShortcut('Ctrl+N')

        open_note = QAction('&Open Note', self)
        open_note.setShortcut('Ctrl+O')

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')

        preferences_action = QAction('&Preferences', self)
        preferences_action.setShortcut('Ctrl+P')

        file.addAction(new_note)
        file.addAction(open_note)
        file.addAction(quit_action)

        edit.addAction(preferences_action)


class ToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_menu()

    def init_menu(self):
        script_dir = path.dirname(path.realpath(__file__))
        path_to_icon_dir = path.join(script_dir, "..", "icons")
        self.newAction = QAction(
            QIcon(path.join(path_to_icon_dir, "new_note.png")),
            "New",
            self)
        self.newAction.setStatusTip("Create a new note.")
        self.newAction.setShortcut("Ctrl+N")

        self.addAction(self.newAction)
