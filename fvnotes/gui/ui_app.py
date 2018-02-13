#!/usr/bin/env python3

import sys

from PyQt5.QtWidgets import QApplication

from fvnotes.gui.ui.main_window import MainWindow

if '-style' not in sys.argv:
    sys.argv = sys.argv + ['-style', 'Fusion']

app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
