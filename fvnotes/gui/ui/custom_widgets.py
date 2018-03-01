#!/usr/bin/env python3

from PyQt5.QtGui import QPainter, QPen, QColor, QFontMetrics, QFontDatabase
from PyQt5.QtWidgets import QTextEdit


class TextEditGuide(QTextEdit):
    """This class adds vertical column guides to QTextEdit class of PyQt5

    Parameters
    ----------
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
    """

    def __init__(self,
                 guides_color=QColor('#AAAAAA'),
                 guides_positions=(72, 80),
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._margin = self.document().documentMargin()
        self._guides_positions = guides_positions
        self.guides_color = guides_color
        self._initialization = True

    def _initialize_gui(self):
        self.font = self.currentFont()
        self.guides_positions = self.convert_to_tuple(self._guides_positions)
        self._initialization = False

    @property
    def font(self):
        """Font used in the widget

        :type: QFont
        :getter: Returns the current font
        :setter: Set the font
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
        :setter: Set the positions
        """
        return self._guides_positions

    @guides_positions.setter
    def guides_positions(self, positions):
        self._guides_positions = positions
        self._guides_positions_pixels = [
            self._font_metrics.width('A' * position)
            for position in self.convert_to_tuple(positions)]
        self.update()

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
