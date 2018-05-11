#!/usr/bin/env python3

from PyQt5.QtWidgets import QDialog


class PreferencesDialog(QDialog):
    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.setWindowTitle('Preferences')

        self.pref_list = QListWidget(self)
        self.pref_list.insertItem(0, 'Taxonomy')
        self.pref_list.insertItem(1, 'Trimming')
        self.pref_list.insertItem(2, 'Extract Taxonomy')
        pref_list_width = self.pref_list.sizeHintForColumn(0) + 10
        self.pref_list.setFixedWidth(pref_list_width)


