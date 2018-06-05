#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, \
    QDialogButtonBox, QLineEdit, QComboBox

from fvnotes.gui.ui.custom_widgets import LabeledText, LabeledComboBox, \
    LabeledPath

FONT_SIZES = ('6', '7', '8', '9', '10', '11', '12', '13', '14',
              '15', '16', '18', '20', '22', '24', '26', '28',
              '32', '36', '40', '44', '48', '54', '60', '66',
              '72', '80', '88', '96',
              )


class PreferencesDialog(QDialog):
    def __init__(self, settings, themes):
        super().__init__()

        self.settings = settings
        self.setWindowTitle('Preferences')
        self.path_to_journal = LabeledPath(parent=self,
                                           name='Journal_path',
                                           label='Path to a notebook',
                                           width=300,
                                           open_dir=True)
        self.main_layout = QVBoxLayout()
        self.theme = LabeledComboBox(parent=self,
                                     name='Theme',
                                     values=[str(i) for i in themes],
                                     width=150,
                                     label='Theme')
        self.notes = TextEditPreferences(group_name='Notes')
        self.journal = TextEditPreferences(group_name='Journal')
        self.trees = TextEditPreferences(group_name='Trees', hide_lines=True)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.init_ui()

    def init_ui(self):
        self.main_layout.addWidget(self.path_to_journal)
        self.main_layout.addWidget(self.theme)
        self.main_layout.addWidget(self.notes)
        self.main_layout.addWidget(self.journal)
        self.main_layout.addWidget(self.trees)
        self.main_layout.addWidget(self.buttons)
        self.setLayout(self.main_layout)
        self._fill_values()

    def _fill_values(self):
        children_widgets = (QLineEdit,
                            QComboBox,
                            )
        for widget in self.findChildren(children_widgets):
            widget_name = widget.objectName()
            if isinstance(widget, QLineEdit) and widget_name != '':
                value = self.settings[widget_name]
                if 'Vertical_lines' in widget.objectName():
                    value = ', '.join(str(i) for i in value)
                widget.setText(value)
                widget.setCursorPosition(0)
            elif isinstance(widget, QComboBox) and widget_name != '':
                widget.parent().text = str(self.settings[widget_name])


class TextEditPreferences(QGroupBox):
    def __init__(self, group_name='', hide_lines=False):
        super().__init__(group_name)
        self.database = QFontDatabase()
        self.hide_lines = hide_lines
        self.frame_style = (
            'QGroupBox:title {'
            'subcontrol-origin: margin;'
            'subcontrol-position: top left;'
            'padding: 0 3 0 3;'
            'left: 7;}'
            'QGroupBox {'
            'margin-top: -11px;'
            'padding: 20 0 0 0;}')
        self.setStyleSheet(self.frame_style)
        self.layout = QVBoxLayout()
        self.font_layout = QHBoxLayout()
        self.font = LabeledComboBox(values=self.database.families(),
                                    name=f'{group_name}/Font',
                                    label="Font:",
                                    width=250)
        self.font_size = LabeledComboBox(values=[str(i) for i in FONT_SIZES],
                                         name=f'{group_name}/Font_size',
                                         width=60,
                                         label='',
                                         editable=True)
        if not hide_lines:
            self.lines_positions = LabeledText(
                label="Vertical markers positions:",
                name=f'{group_name}/Vertical_lines',
                width=120)
        self.init_ui()

    def init_ui(self):
        self.layout.setContentsMargins(10, 15, 10, 10)
        self.font_layout.setContentsMargins(0, 0, 0, 0)
        self.font_layout.addWidget(self.font, 1)
        self.font_layout.addWidget(self.font_size)
        self.layout.addLayout(self.font_layout)
        if not self.hide_lines:
            self.layout.addWidget(self.lines_positions)
        self.setLayout(self.layout)
