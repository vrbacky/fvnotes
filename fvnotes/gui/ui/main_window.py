#!/usr/bin/env python3

import os

from PyQt5.QtCore import QDir, Qt, QTimer, QFile, QSortFilterProxyModel
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QTextEdit, QSplitter, \
    QWidget, QCalendarWidget, QVBoxLayout, QFileSystemModel, QTreeView, \
    QMessageBox, QAction, QMenu

from fvnotes import AUTHOR, NAME, VERSION
from fvnotes.exceptions import CannotRenameFileError
from fvnotes.gui.ui.bars import MenuBar, ToolBar
from fvnotes.gui.ui.custom_widgets import TextEditGuide


NOTES_FONT = 'Ubuntu Mono'
NOTES_FONT_SIZE = '11'
TREES_FONT = 'Ubuntu'
TREES_FONT_SIZE = '10'
CALENDAR_FONT = 'Ubuntu'
CALENDAR_FONT_SIZE = '10'

# Light color scheme
APP_BACKGROUND = '#D0D0D0'
MENU_SELECTED = '#A0A0A0'
WIDGET_BACKGROUND = '#F5F5F5'
FONT_COLOR = '#050505'
FONT_INACTIVE = '#A0A0A0'
VERTICAL_LINE_COLOR = '#C0C0C0'

# Dark color scheme
APP_BACKGROUND = '#202020'
MENU_SELECTED = '#454545'
WIDGET_BACKGROUND = '#101010'
FONT_COLOR = '#B5B5B5'
FONT_INACTIVE = '#2F2F2F'
VERTICAL_LINE_COLOR = '#353535'

VERTICAL_LINES_NOTES = {40, 80}
VERTICAL_LINES_JOURNAL = 80


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.application = NAME
        self.author = AUTHOR
        self.version = VERSION

        self.window_title = '{} v{}'.format(self.application,
                                            self.version)
        self.main_widget = MainWidget(self)

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.tool_bar = ToolBar(self)
        self.addToolBar(self.tool_bar)
        self.status_bar = self.statusBar()

        self.init_ui()

    def init_ui(self):
        # self.showMaximized()
        self.change_color_scheme()
        self.setWindowTitle(self.window_title)
        self.setCentralWidget(self.main_widget)
        self.status_bar.showMessage('StatusBar')

        self.menu_bar.create_note.connect(self.main_widget.create_note)
        self.tool_bar.create_note.connect(self.main_widget.create_note)
        self.menu_bar.save_note.connect(self.main_widget.save_note)
        self.tool_bar.save_note.connect(self.main_widget.save_note)

        self.show()

    def change_color_scheme(self):
        self.setStyleSheet(
            f'QMainWindow{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QMenuBar{{'
            f'background-color: {APP_BACKGROUND};}}'

            f'QMenuBar::item{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QMenuBar::item::selected{{'
            f'background-color: {MENU_SELECTED};}}'

            f'QMenu{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QMenu::item::selected{{'
            f'background-color: {MENU_SELECTED};}}'

            f'QToolBar{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QToolButton::hover{{'
            f'background-color: {MENU_SELECTED};'
            f'color: {FONT_COLOR}}}'

            f'QStatusBar{{'
            f'color: {FONT_COLOR};}}'

            f'QTextEdit{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'color: {FONT_COLOR};'
            f'font-size: {NOTES_FONT_SIZE}pt;'
            f'font-family: {NOTES_FONT};}}'

            f'QTreeView{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'color: {FONT_COLOR};'
            f'font-size: {TREES_FONT_SIZE}pt;'
            f'font: {TREES_FONT};}}'

            f'QCalendarWidget QWidget{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'font-size: {CALENDAR_FONT_SIZE}pt;'
            f'font: {CALENDAR_FONT};}}'

            f'QCalendarWidget QToolButton{{'
            f'color: {FONT_COLOR}}}'

            f'QCalendarWidget QToolButton::hover{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR}}}'

            f'QCalendarWidget QSpinBox{{'
            f'background-color: {APP_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QCalendarWidget QMenu{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'color: {FONT_COLOR};}}'

            f'QCalendarWidget QAbstractItemView:enabled{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'color: {FONT_COLOR};'
            f'selection-background-color: {APP_BACKGROUND};'
            f'selection-color: {FONT_COLOR};}}'

            f'QCalendarWidget QAbstractItemView:disabled{{'
            f'background-color: {WIDGET_BACKGROUND};'
            f'color: {FONT_INACTIVE};}}'

            f'QCalendarWidget QWidget{{'
            f'alternate-background-color: {APP_BACKGROUND};}}'

            f'QScrollBar{{'
            f'background-color: {APP_BACKGROUND};}}'
        )

    def closeEvent(self, event):
        if self.main_widget.notes_text.current_file is not None:
            self.main_widget.notes_text.save_file()
            try:
                self.main_widget._rename_note()
            except CannotRenameFileError:
                event.ignore()


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.ROOT_DIR = '/home/fv-user/notes'
        self._note_hash = None
        self.note_has_changed = False

        self.main_layout = QHBoxLayout()
        self.main_splitter = QSplitter()

        self.files_splitter = QSplitter()
        self.directories_model = QFileSystemModel()
        self.root_index = self.directories_model.setRootPath(self.ROOT_DIR)
        self.directories_view = QTreeView(headerHidden=True)
        self.files_model = QFileSystemModel()
        self.files_proxy = QSortFilterProxyModel()
        self.files_view = QTreeView(headerHidden=True, rootIsDecorated=False)
        self.files_favourites = QTextEdit('Favourites - to be implemented')

        self.notes_text = TextEditGuide(
            parent=self,
            guides_color=VERTICAL_LINE_COLOR,
            guides_positions=VERTICAL_LINES_NOTES)

        self.journal_widget = QWidget()
        self.journal_layout = QVBoxLayout()
        self.journal_text = TextEditGuide(
            parent=self,
            guides_color=VERTICAL_LINE_COLOR,
            guides_positions=VERTICAL_LINES_JOURNAL)
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
        self.files_proxy.setSourceModel(self.files_model)
        self.files_proxy.setDynamicSortFilter(True)

        self.files_view.setModel(self.files_proxy)
        self.files_view.setSortingEnabled(True)
        self.files_view.sortByColumn(0, Qt.AscendingOrder)
        self.files_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_view.customContextMenuRequested.connect(
            self.files_context_menu)

        self._hide_unnecessary_columns(self.files_view)

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

        self.notes_text.textChanged.connect(self.note_changed)
        self.directories_view.selectionModel().selectionChanged.connect(
            self._dir_changed)
        self.files_view.selectionModel().selectionChanged.connect(
            self.file_changed)

    def files_context_menu(self, position):
        index = self.files_view.indexAt(position)

        menu = QMenu()
        delete_file_action = QAction("Delete file")
        delete_file_action.triggered.connect(lambda: self.delete_note(index))
        menu.addAction(delete_file_action)
        menu.exec_(self.files_view.viewport().mapToGlobal(position))

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

    def _get_current_dir(self):
        current_index = self.directories_view.selectionModel().currentIndex()
        return self.directories_model.filePath(current_index)

    def _rename_window(self, title=None):
        if title is None:
            title = self.parent.window_title
            if self.notes_text.current_file is not None:
                short_current_file = self.notes_text.current_file.replace(
                    self.ROOT_DIR, '')
                title += f' - {short_current_file}'
            if self.notes_text.text_has_changed:
                title = f'{title}*'
        self.parent.setWindowTitle(title)

    def _dir_changed(self):
        source_index = self.files_model.setRootPath(self._get_current_dir())
        proxy_index = self.files_proxy.mapFromSource(source_index)
        self.files_view.setRootIndex(proxy_index)
        if self.files_view.isColumnHidden(0):
            self.files_view.setColumnHidden(0, False)

    def create_note(self):
        self.files_view.clearSelection()
        if self.notes_text.current_file is not None:
            self.save_note()
        self.notes_text.current_file = None
        self.parent.setWindowTitle(self.parent.window_title)
        self.notes_text.setFocus()
        self.notes_text.text_has_changed = False

    def save_note(self, selection_changed=False):
        if (self.notes_text.toPlainText() == '' or
                not self.notes_text.text_has_changed):
            return 0

        if self.notes_text.current_file is None:
            directory = self._get_current_dir()
            first_line = self.notes_text.first_line
            if first_line == '':
                first_line = '_'
            new_filename = os.path.join(
                directory,
                self.notes_text.convert_text_to_filename(first_line) + '.md')
            if QFile(new_filename).exists():
                QMessageBox.critical(
                    self,
                    'File Cannot Be Saved',
                    'The note file cannot be saved. Try to change '
                    'the first line of the note.')
            else:
                self.notes_text.save_file(new_filename)
                self.notes_text.current_file = new_filename
                self._rename_window()
                self.select_file_by_name(new_filename)
        else:
            self.notes_text.save_file()
            try:
                self._rename_note(selection_changed)
            except CannotRenameFileError:
                pass

        self.notes_text.text_has_changed = False
        self._rename_window()

    def delete_note(self, current_index):
        current_filename = self.get_filename_from_index(current_index)

        if self.files_view.indexBelow(current_index).data() is not None:
            self.files_view.setCurrentIndex(
                self.files_view.indexBelow(current_index))
        elif self.files_view.indexAbove(current_index).data() is not None:
            self.files_view.setCurrentIndex(
                self.files_view.indexAbove(current_index))
        else:
            self.create_note()

        if current_filename != '':
            was_renamed = QFile(current_filename).remove()
            if not was_renamed:
                QMessageBox(
                    self,
                    'File Cannot Be Deleted',
                    'The note file cannot be deleted.')

    def note_changed(self):
        self._rename_window()

    def file_changed(self):
        self.save_note(selection_changed=True)

        current_index = self.files_view.currentIndex()
        current_index = self.files_proxy.mapToSource(current_index)
        self.notes_text.current_file = self.files_model.filePath(
            current_index)
        self.notes_text.text_has_changed = False
        self._rename_window()

    def _rename_note(self, selection_changed=True):
        selected_file_index = self.files_view.currentIndex()
        current_file = self.notes_text.current_file
        dir_of_current_file = os.path.dirname(current_file)

        first_line = self.notes_text.first_line
        if first_line == '':
            first_line = '_'

        new_filename = os.path.join(
            dir_of_current_file,
            self.notes_text.convert_text_to_filename(first_line) + '.md')

        if new_filename != current_file:
            if not QFile(current_file).rename(new_filename):
                QMessageBox.critical(
                    self,
                    'File Cannot Be Renamed',
                    'The note file cannot be renamed. Try to change '
                    'the first line of the note.')
                self.select_file_by_name(current_file)
                raise CannotRenameFileError
            else:
                if selection_changed:
                    self.files_view.setCurrentIndex(selected_file_index)
                else:
                    self.notes_text.current_file = new_filename
                    self.select_file_by_name(new_filename)
                self._rename_window()

    def get_filename_from_index(self, index):
        model_index = self.files_proxy.mapToSource(index)
        return self.files_model.filePath(model_index)

    def select_file_by_name(self, filename):
        self.files_view.selectionModel().selectionChanged.disconnect(
            self.file_changed)
        original_index = self.files_model.index(filename)
        original_proxy_index = self.files_proxy.mapFromSource(
            original_index)
        self.files_view.setCurrentIndex(original_proxy_index)
        self.files_view.selectionModel().selectionChanged.connect(
            self.file_changed)
