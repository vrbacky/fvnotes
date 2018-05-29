#!/usr/bin/env python3

import hashlib
import string

import os
from PyQt5.QtCore import pyqtSignal, QFile
from PyQt5.QtGui import QPainter, QPen, QColor, QFontMetrics, QFontDatabase, \
    QFont
from PyQt5.QtWidgets import QTextEdit, QMessageBox, QLineEdit, QLabel, \
    QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QFileDialog, QPushButton

from fvnotes.exceptions import CannotSaveFileError
from fvnotes.gui.ui.syntax_highlighter import Highlighter


class TextEditGuide(QTextEdit):
    """This class adds vertical column guides to QTextEdit class of PyQt5

    Parameters
    ----------
    parent : QWidget
        Parent of the new widget
    guides_color : QColor
        Color of the guidelines
    guides_positions : iterable
        Positions of the guidelines in number of average characters
    font : QFont
        Font of the widget


    Attributes
    ----------
    font : QFont
        Font of the widget
    guides_color : QColor
        Color of the guidelines
    line_positions : iterable
        Positions of the guidelines in number of average characters
    current_file : str
        Path to the current file opened in the widget
    first_line : str
        Text of the fist line of the opened file (read only)
    """

    lost_focus = pyqtSignal()

    def __init__(self,
                 parent=None,
                 guides_color=QColor('#AAAAAA'),
                 guides_positions=(72, 80),
                 font=QFont('Ubuntu Mono', 11),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._margin = self.document().documentMargin()
        self._guides_positions = guides_positions
        self.guides_color = guides_color
        self._initialization = True
        self._current_file = None
        self.parent = parent
        self._unchanged_note_hash = None
        self.font = font
        self.highlighter = Highlighter(self.document())

    def _initialize_gui(self):
        self.font = self.currentFont()
        self.guides_positions = self.convert_to_tuple(self._guides_positions)
        self._initialization = False

    @property
    def first_line(self):
        """Text of the fist line of the opened file (read only)

        :type: str
        :getter: Returns the text
        """
        return self.toPlainText().split('\n')[0]

    @property
    def current_file(self):
        """Path to the current file opened in the widget

        :type:
        :getter: Returns the path to the file
        :setter: Opens it in the widget
        """
        return self._current_file

    @current_file.setter
    def current_file(self, file):
        self._current_file = file
        if file is not None:
            try:
                with open(file, 'rt') as f:
                    self.setPlainText(f.read())
                    self.text_has_changed = False
            except Exception as err:
                QMessageBox.critical(
                    self,
                    'File Open Failed',
                    f'This file cannot be opened\n\n{err}')
        else:
            self.setPlainText('')

    @property
    def cursor_position(self):
        """Position of a cursor in the widget

        :type: int
        :getter: Returns the absolute position of the cursor
        :setter: Sets the absolute position of the cursor
        """
        return self.textCursor().position()

    @cursor_position.setter
    def cursor_position(self, position):
        cursor = self.textCursor()
        cursor.setPosition(position)
        self.setTextCursor(cursor)

    @property
    def font(self):
        """Font used in the widget

        :type: QFont
        :getter: Returns the current font
        :setter: Sets the font
        """
        return self._font

    @font.setter
    def font(self, font):
        self.setStyleSheet(f'font-size: {font.pointSize()}pt;'
                           f'font-family: {font.family()}')

        self._font_metrics = QFontMetrics(font)
        self.guides_positions = self._guides_positions
        self._font = font

    @property
    def guides_positions(self):
        """Positions of the vertical guidelines

        :type: tuple
        :getter: Returns the positions
        :setter: Sets the positions
        """
        return self._guides_positions

    @guides_positions.setter
    def guides_positions(self, positions):
        self._guides_positions = positions
        self._guides_positions_pixels = [
            self._font_metrics.width('A' * position)
            for position in self.convert_to_tuple(positions)]
        self.update()

    @property
    def text_has_changed(self):
        """Has a text in the widget been changed since the last reset?

        :type: bool
        :getter: Returns True if the widget contains changes since the last
                 reset
        :setter: Resets status when set to False
        """
        return self.get_current_text_hash() != self._unchanged_note_hash

    @text_has_changed.setter
    def text_has_changed(self, has_changed):
        if has_changed is False:
            self._unchanged_note_hash = self.get_current_text_hash()

    def save_file(self, file_path=None, check_file_exists=False):
        """Save text in the widget

        Text will be saved to the file provided as a parameter.
        Raises CannotSaveFileError, if the file cannot be saved.

        Parameters
        ----------
        file_path : str
            Absolute path of the saved file
        check_file_exists : bool
            Existing file will not be rewritten and message box will be shown,
            if it is set to True. (default: False)
        """
        if file_path is None:
            file_path = self._current_file

        if check_file_exists:
            if QFile(file_path).exists():
                QMessageBox.critical(
                    self,
                    'File Cannot Be Saved',
                    'The file cannot be saved. Try to change its first line.')
                raise CannotSaveFileError

        text = self.toPlainText()
        try:
            with open(file_path, 'wt') as file:
                file.write(text)
        except Exception as err:
            QMessageBox.critical(
                self,
                'File Save Failed',
                f'Cannot write to the file\n\n{err}')
            raise CannotSaveFileError
        return True

    def get_current_text_hash(self):
        return hashlib.sha256(
            self.toPlainText().encode('utf-8')).digest()

    def create_abs_file_path(self, directory=None, filename=None):
        """Create absolute path to a file

        Creates absolute path from provided path to a directory and a filename.
        Omitted parameters will be substituted with strings parsed from
        path of the opened file and text of the widget.

        Parameters
        ----------
        directory : str
            Absolute path to the directory containing the file. If omitted,
            directory of the current_file is used.
        filename : str
            Name of the file. If omitted, the first line of the text will be
            used and .md extension will be added. Empty line will be
            substituted with _ character.

        Returns
        -------
        str
            Absolute path to the file
        """
        if filename is None:
            first_line = self.first_line
            if first_line == '':
                first_line = '_'
            filename = f'{self.convert_text_to_filename(first_line)}.md'

        if directory is None:
            directory = os.path.dirname(self.current_file)

        return os.path.join(directory, filename)

    def paintEvent(self, event):
        if self._initialization:
            self._initialize_gui()
        painter = QPainter(self.viewport())
        q_pen = QPen(QColor(self.guides_color))
        painter.setPen(q_pen)

        if QFontDatabase().isFixedPitch(self._font.family()):
            for line_position in self._guides_positions_pixels:
                painter.drawLine(line_position + self._margin, 0,
                                 line_position + self._margin, self.height())

        super(TextEditGuide, self).paintEvent(event)

    @staticmethod
    def convert_to_tuple(data):
        """Convert provided iterable or uniterable parameter to a tuple"""
        try:
            return tuple(data)
        except TypeError:
            return (data,)

    @staticmethod
    def convert_text_to_filename(text):
        """Convert a string to a valid file name

        Parameters
        ----------
        text : str
            A string to be converted

        Returns
        -------
        str
            A string with all non-valid characters replaced by underscores.
            Only ASCII letters and numbers are considered valid.
        """
        valid_characters = f'-_.(){string.ascii_letters}{string.digits}'
        filename = ''
        for letter in text:
            if letter in valid_characters:
                filename += letter
            else:
                filename += '_'

        return filename


class LabeledWidget(QWidget):
    def __init__(self, widget, parent=None, label='Font size:',
                 width=40, name='', tooltip='', vertical=False):
        super().__init__(parent=parent)

        self.label = QLabel(label)
        self.input_widget = widget
        if tooltip != '':
            self.input_widget.setToolTip(tooltip)
        self.input_widget.setObjectName(name)
        self.input_widget.setMinimumWidth(width)

        if vertical:
            self.layout = QVBoxLayout()
        else:
            self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input_widget, 1)
        self.setLayout(self.layout)


class LabeledText(LabeledWidget):
    def __init__(self, parent=None, label='Font size:', text='',
                 width=40, name='', tooltip='', vertical=False):
        super().__init__(QLineEdit(),
                         parent=parent,
                         label=label,
                         width=width,
                         name=name,
                         tooltip=tooltip,
                         vertical=vertical)
        self.input_widget.setText(text)

    @property
    def text(self):
        return self.text_field.text()

    @text.setter
    def text(self, text):
        self.input_widget.setText(text)


class LabeledComboBox(LabeledWidget):
    def __init__(self, parent=None, label='Font size:', values=[],
                 width=40, name='', tooltip='', vertical=False,
                 editable=False):
        super().__init__(QComboBox(),
                         parent=parent,
                         label=label,
                         width=width,
                         name=name,
                         tooltip=tooltip,
                         vertical=vertical)

        self.input_widget.setEditable(editable)
        self.input_widget.setDuplicatesEnabled(False)
        self._values = values
        self.input_widget.addItems(values)

    @property
    def text(self):
        return self.input_widget.currentText()

    @text.setter
    def text(self, text):
        if text not in self._values:
            self._values.append(text)
            self.input_widget.addItem(text)
        self.input_widget.setCurrentText(text)


class LabeledPath(QWidget):
    def __init__(self, parent=None, label='Font size:', text='',
                 width=40, name='', tooltip='', vertical=False,
                 open_dir=False):
        super().__init__(parent),
        self._open_dir = open_dir
        self.labeled_text = LabeledText(parent, label, text, width, name,
                                        tooltip, vertical)
        self.parent = parent
        self.button = QPushButton('Browse...')
        self.button.clicked.connect(self.open_dialog)
        if tooltip != '':
            self.input_widget.setToolTip(tooltip)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.labeled_text)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

    @property
    def text(self):
        return self.labeled_text.text

    @text.setter
    def text(self, text):
        self.labeled_text.text = text

    def open_dialog(self):
        if self._open_dir:
            path = QFileDialog.getExistingDirectory(parent=self.parent,
                                                    caption='Open Directory')
            self.labeled_text.text = path
        else:
            path = QFileDialog.getOpenFileName(parent=self.parent,
                                               caption='Open Directory')
            self.labeled_text.text = path[0]
