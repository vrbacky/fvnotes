#!/usr/bin/env python3

from PyQt5.QtCore import QDir, Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QTextEdit, QSplitter, \
    QWidget, QCalendarWidget, QVBoxLayout, QFileSystemModel, QTreeView

from fvnotes import AUTHOR, NAME, VERSION
from fvnotes.gui.ui.bars import MenuBar, ToolBar


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.application = NAME
        self.author = AUTHOR
        self.version = VERSION

        self.window_title = '{} v{}'.format(self.application,
                                            self.version)

        self.menu_bar = self.setMenuBar(MenuBar())
        self.tool_bar = self.addToolBar(ToolBar())
        self.status_bar = self.statusBar()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.window_title)
        self.setCentralWidget(MainWidget(self))

        self.status_bar.showMessage('StatusBar')

        # self.showMaximized()
        self.show()


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.ROOT_DIR = '/home/'

        self.main_layout = QHBoxLayout()
        self.main_splitter = QSplitter()

        self.files_splitter = QSplitter()
        self.directories_model = QFileSystemModel()
        self.root_index = self.directories_model.setRootPath(self.ROOT_DIR)
        self.directories_view = QTreeView(headerHidden=True)
        self.files_model = QFileSystemModel()
        self.files_view = QTreeView(headerHidden=True, rootIsDecorated=False)
        self.files_favourites = QTextEdit('Favourites - to be implemented')

        self.notes_text = QTextEdit('main_text')

        self.journal_widget = QWidget()
        self.journal_layout = QVBoxLayout()
        self.journal_text = QTextEdit('Journal Text')
        self.journal_calendar_wrapper = QWidget()
        self.journal_calendar_layout = QHBoxLayout()
        self.journal_calendar = QCalendarWidget()

        self.timer = QTimer(self)

        self.init_ui()

    def init_ui(self):
        self.main_layout.setContentsMargins(6, 2, 6, 2)
        self.main_layout.addWidget(self.main_splitter)
        self.setLayout(self.main_layout)

        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(self.files_splitter)
        self.main_splitter.addWidget(self.notes_text)
        self.main_splitter.addWidget(self.journal_widget)
        self.main_splitter.setSizes((250, 500, 500))

        self.files_splitter.setOrientation(Qt.Vertical)
        self.files_splitter.setChildrenCollapsible(False)
        self.files_splitter.addWidget(self.directories_view)
        self.files_splitter.addWidget(self.files_view)
        self.files_splitter.addWidget(self.files_favourites)

        self.directories_model.setFilter(
            QDir.Dirs | QDir.NoDotAndDotDot | QDir.Name)
        self.directories_view.setModel(self.directories_model)
        self.directories_view.setRootIndex(self.root_index)
        self._hide_unnecessary_columns(self.directories_view)

        self.files_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.files_view.setModel(self.files_model)
        self._hide_unnecessary_columns(self.files_view)

        self.directories_view.selectionModel().selectionChanged.connect(
            self.dir_changed)
        self.files_view.selectionModel().selectionChanged.connect(
            self.file_changed)
        self.directories_view.setCurrentIndex(self.root_index)

        self.journal_widget.setLayout(self.journal_layout)
        self.journal_layout.setContentsMargins(0, 0, 0, 0)

        self.journal_layout.addWidget(self.journal_text)
        self.journal_layout.addWidget(self.journal_calendar_wrapper)
        self.journal_layout.setStretch(0, 1)
        self.journal_calendar_wrapper.setLayout(self.journal_calendar_layout)
        self.journal_calendar_layout.addStretch()
        self.journal_calendar_layout.setContentsMargins(0, 0, 0, 0)
        self.journal_calendar_layout.addWidget(self.journal_calendar)
        self.journal_calendar_layout.addStretch()

        self._rename_window(self.parent.window_title)
        self.timer.singleShot(1, self.jump_to_index_bellow)

    def _hide_unnecessary_columns(self, view):
        for column in range(1, 4):
            view.setColumnHidden(column, True)

    def jump_to_index_bellow(self, index=None):
        if index is None:
            index = self.root_index

        if self.directories_model.rowCount(index) > 0:
            self.directories_model.sort(1)
            self.directories_view.setCurrentIndex(
                self.directories_view.indexBelow(index))
        else:
            self.directories_view.setCurrentIndex(index)
            self.files_view.hideColumn(0)

    @property
    def _current_dir(self):
        current_index = self.directories_view.selectionModel().currentIndex()
        return self.directories_model.filePath(current_index)

    @property
    def _current_file(self):

        current_index = self.files_view.selectionModel().currentIndex()
        return self.files_model.filePath(current_index)

    def _rename_window(self, title=None):
        if title is None:
            short_current_file = self._current_file.replace(self.ROOT_DIR, '')
            title = (f'{self.parent.window_title} - {short_current_file}')
        self.parent.setWindowTitle(title)

    def dir_changed(self):
        self.files_view.setRootIndex(
            self.files_model.setRootPath(self._current_dir))
        if self.files_view.isColumnHidden(0):
            self.files_view.setColumnHidden(0, False)

    def file_changed(self):
        self._rename_window()
