#!/usr/bin/env python3

from itertools import zip_longest

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes."""

    _color = QColor(f'#{color}')

    _format = QTextCharFormat()
    _format.setForeground(_color)

    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


STYLES = {
    'keyword': format('CC7832'),
    'operator': format('A9B7C6'),
    'brace': format('A9B7C6'),
    'funcname': format('FFC66D', 'bold'),
    'string': format('6A8759'),
    'docstring': format('77B767', 'italic'),
    'comment': format('808080', 'italic'),
    'self': format('8F4F7C'),
    'numbers': format('6897BB'),
}


KEYWORDS = {
    'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
    'del', 'elif', 'else', 'except', 'exec', 'finally',
    'for', 'from', 'global', 'if', 'import', 'in',
    'is', 'lambda', 'None', 'not', 'or', 'pass', 'print',
    'raise', 'return', 'try', 'while', 'yield',
    'True', 'False',
}


OPERATORS = {
    '=',
    '==', '!=', '<', '<=', '>', '>=',
    '\+', '-', '\*', '/', '//', '\%', '\*\*',
    '\+=', '-=', '\*=', '/=', '\%=',
    '\^', '\|', '\&', '\~', '>>', '<<',
}


BRACES = {
    '\{', '\}', '\(', '\)', '\[', '\]',
}


class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.code_block_delimiter = QRegularExpression(r'^\s*```')

        self.docstring_single = QRegularExpression(r"'''")
        self.docstring_double = QRegularExpression(r'"""')

        rules = []

        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in KEYWORDS]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in OPERATORS]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in BRACES]

        rules += [
            (r'\bself\b', 0, STYLES['self']),
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),
            (r'\bdef\b\s*(\w+)', 1, STYLES['funcname']),
            (r'#[^\n]*', 0, STYLES['comment']),
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
                STYLES['numbers']),
        ]

        self.rules = [(QRegularExpression(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def _find_docstring_limits(self, text, regexp, new_state,
                               previous_state=None):
        """Return start positions of docstring limits.

        Add 0, if the docstring continues from the previous line.

        Parameters
        ----------
        text : str
            Text of the current block (line).
        regexp : QRegularExpression
            QRegularExpression instance used to search for a pattern
            in the text.
        new_state : int
            A number showing state of the current block (0 = not to be
            highlighted, 1 = code to be highlighted, 2 = docstring surrounded
            by triple single-quotes, 2 = docstring surrounded by triple
            double-quotes).
        previous_state : int
            A number showing state of the previous block (0 = not to be
            highlighted, 1 = code to be highlighted, 2 = docstring surrounded
            by triple single-quotes, 2 = docstring surrounded by triple
            double-quotes).

        Returns
        -------
        generator
            Generator of tuples containing start positions of triple quotes
            surrounding docstrings in the current block.
        """
        if previous_state is None:
            previous_state = self.previousBlockState()

        if new_state == previous_state:
            yield 0

        regexp_matches = regexp.globalMatch(text)
        while regexp_matches.hasNext():
            yield regexp_matches.next().capturedStart()

    def find_docstrings(self, text, previous_state):
        """Return docstring positions and state at the end of the line.

        Parameters
        ----------
        text : str
            Text of the current block (line).
        previous_state : int
            State of the previous block (line).

        Returns
        -------
        tuple
            The first element contains iterator of tuples containing start
            positions of triple quotes surrounding docstrings in the current
            block. The second element contains number showing, if the block
            ends with an open docstring or not (0 = no docstring,
            1 = docstring surrounded by triple single-quotes, 2 = docstring
            surrounded by triple double-quotes).
        """
        matches_single = self._find_docstring_limits(
            text, self.docstring_single, 2, previous_state)
        matches_double = self._find_docstring_limits(
            text, self.docstring_double, 3, previous_state)

        return self.combine_positions(matches_single,
                                      matches_double,
                                      self.currentBlock().length())

    def _change_code_block_state(self, previous_state):
        if previous_state >= 1:
            return 0
        else:
            return 1

    def highlightBlock(self, text):
        state = self.previousBlockState()
        if self.code_block_delimiter.match(text).capturedStart() >= 0:
            state = self._change_code_block_state(state)

        if state >= 1:
            for expression, nth, format in self.rules:
                re_matches = expression.globalMatch(text)

                while re_matches.hasNext():
                    re_match = re_matches.next()
                    re_start = re_match.capturedStart(nth)
                    re_length = re_match.capturedLength(nth)
                    self.setFormat(re_start, re_length, format)

            docstring_limits, active_docstring = \
                self.find_docstrings(text, state)
            for start, end in docstring_limits:
                length_to_end = end - start + 3
                self.setFormat(start, length_to_end, STYLES['docstring'])
            state = active_docstring + 1

        self.setCurrentBlockState(state)

    @staticmethod
    def combine_positions(positions_1, positions_2, fillvalue=None):
        """Create non-overlapping ranges with limits from the same iterator

        Combine two iterators and return tuples of non-overlapping positions
        limited by the positions from the same iterator. It can be used
        for example to find docstrings surrounded by triple single- or
        double-quotes.

        Parameters
        ----------
        positions_1 : iter
            Positions of the first type (e.g. triple single-quotes).
        positions_2 : iter
            Positions of the second type (e.g. triple double-quotes).
        fillvalue : str
            This value will be used if the last range is open (default: None).

        Returns
        -------
        tuple
            The first element contains iterator of tuples containing opening
            and closing positions of the intervals.
            The second element contains final state (0 = The last tuple is
            closed - contains a value from positions_1 or positions_2
            parameter, 1 = the first element in the last tuple is from
            positions_1 and the second one is fillvalue parameter,
            2 = the first element in the last tuple is from positions_2
            and the second is fillvalue parameter).
        """
        pos1 = [(i, 1) for i in positions_1]
        pos2 = [(i, 2) for i in positions_2]

        positions = sorted(pos1 + pos2, key=lambda x: x[0])
        starts = []
        ends = []

        active_input = 0

        for position in positions:
            if active_input == 0:
                active_input = position[1]
                starts.append(position[0])
            elif active_input == position[1]:
                ends.append(position[0])
                active_input = 0

        return (zip_longest(starts, ends, fillvalue=fillvalue),
                active_input)
