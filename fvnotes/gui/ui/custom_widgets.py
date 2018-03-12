#!/usr/bin/env python3

import string
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QFontMetrics, QFontDatabase
from PyQt5.QtWidgets import QTextEdit, QMessageBox


class TextEditGuide(QTextEdit):
    """This class adds vertical column guides to QTextEdit class of PyQt5

    Parameters
    ----------
    parent : QWidget
        Parent of the new widget
    guides_color : QColor
        Color of the guidelines
    line_positions : iterable
        Positions of the guidelines in number of average characters


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
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._margin = self.document().documentMargin()
        self._guides_positions = guides_positions
        self.guides_color = guides_color
        self._initialization = True
        self._current_file = None
        self.parent = parent

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
            except Exception as err:
                QMessageBox.critical(
                    self,
                    'File Open Failed',
                    f'This file cannot be opened\n\n{err}')
        else:
            self.setPlainText('')

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

    def save_file(self, file_path=None):
        if file_path is None:
            file_path = self._current_file

        text = self.toPlainText()
        try:
            with open(file_path, 'wt') as file:
                file.write(text)
        except Exception as err:
            QMessageBox.critical(
                self,
                'File Save Failed',
                f'Cannot write to the file\n\n{err}')

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
