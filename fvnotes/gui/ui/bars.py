#!/usr/bin/env python3

from os import path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenuBar, QToolBar


class MenuBar(QMenuBar):

    create_note = pyqtSignal()
    save_note = pyqtSignal()
    save_journal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.init_menu()

    def init_menu(self):
        file = self.addMenu('File')
        edit = self.addMenu('Edit')

        new_note = QAction('&New Note', self)
        new_note.setShortcut('Ctrl+N')
        new_note.triggered.connect(self.create_note.emit)

        save_note = QAction('&Save Note', self)
        save_note.setShortcut('Ctrl+S')
        save_note.triggered.connect(self.save_note.emit)

        save_journal = QAction('Save &Journal', self)
        save_journal.setShortcut('Ctrl+J')
        save_journal.triggered.connect(self.save_journal.emit)

        quit_action = QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')

        preferences_action = QAction('&Preferences', self)
        preferences_action.setShortcut('Ctrl+P')

        file.addAction(new_note)
        file.addAction(save_note)
        file.addAction(save_journal)
        file.addAction(quit_action)

        edit.addAction(preferences_action)


class ToolBar(QToolBar):

    create_note = pyqtSignal()
    save_note = pyqtSignal()
    save_journal = pyqtSignal()

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
        self.new_action.triggered.connect(self.create_note.emit)

        self.save_note_action = QAction(
            QIcon(path.join(path_to_icon_dir, "save_note.png")),
            "Save",
            self)
        self.save_note_action.setStatusTip("Save the note.")
        self.save_note_action.triggered.connect(self.save_note.emit)

        self.save_journal_action = QAction(
            QIcon(path.join(path_to_icon_dir, "save_journal.png")),
            "Save",
            self)
        self.save_journal_action.setStatusTip("Save the journal.")
        self.save_journal_action.triggered.connect(self.save_journal.emit)

        self.addAction(self.new_action)
        self.addAction(self.save_note_action)
        self.addAction(self.save_journal_action)
