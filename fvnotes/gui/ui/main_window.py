#!/usr/bin/env python3

import os

from PyQt5.QtCore import QDir, Qt, QTimer, QFile, QSortFilterProxyModel
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QTextEdit, QSplitter, \
    QWidget, QCalendarWidget, QVBoxLayout, QFileSystemModel, QTreeView, \
    QMessageBox, QAction, QMenu, QInputDialog

from fvnotes import AUTHOR, NAME, VERSION
from fvnotes.exceptions import CannotRenameFileError, CannotSaveFileError, \
    NotFileOrDirError
from fvnotes.path import rmdir_recursive
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

        self.menu_bar.create_note.connect(
            self.main_widget.save_and_create_note)
        self.tool_bar.create_note.connect(
            self.main_widget.save_and_create_note)
        self.menu_bar.save_note.connect(self.main_widget.save_note)
        self.tool_bar.save_note.connect(self.main_widget.save_note)
        self.menu_bar.save_journal.connect(self.main_widget.save_journal)
        self.tool_bar.save_journal.connect(self.main_widget.save_journal)

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
        self.main_widget.save_journal()


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.ROOT_DIR = '/home/fv-user/notes'
        self._note_hash = None  # TODO: Delete it during a cleanup
        self.note_has_changed = False  # TODO: Delete it during a cleanup

        self.main_layout = QHBoxLayout()
        self.main_splitter = QSplitter()

        self.files_splitter = QSplitter()
        self.directories_model = QFileSystemModel()
        self.directories_proxy = QSortFilterProxyModel()
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
        self.directories_proxy.setSourceModel(self.directories_model)
        self.directories_proxy.setDynamicSortFilter(True)
        directories_model_index = self.directories_model.setRootPath(
            self.ROOT_DIR)
        self.root_index = self.directories_proxy.mapFromSource(
            directories_model_index)
        self.directories_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.directories_view.customContextMenuRequested.connect(
            self.dirs_context_menu)
        self.directories_view.setRootIsDecorated(True)
        self.directories_view.setModel(self.directories_proxy)
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
        self._create_journal_dir()
        self.open_journal(dont_set_focus=True)
        self.notes_text.text_has_changed = False

        self.notes_text.textChanged.connect(self.note_changed)
        self.directories_view.selectionModel().selectionChanged.connect(
            self._dir_changed)
        self.files_view.selectionModel().selectionChanged.connect(
            self.file_changed)
        self.journal_calendar.selectionChanged.connect(
            self.journal_file_changed)

        self.timer.singleShot(1, self.select_first_dir)

    def files_context_menu(self, position):
        index = self.files_view.indexAt(position)

        menu = QMenu()
        delete_file_action = QAction("Delete file")
        delete_file_action.triggered.connect(lambda: self.delete_note(index))
        menu.addAction(delete_file_action)
        menu.exec_(self.files_view.viewport().mapToGlobal(position))

    def dirs_context_menu(self, position):
        index = self.directories_view.indexAt(position)

        menu = QMenu()
        create_dir_action = QAction("Create a directory")
        create_dir_action.triggered.connect(
            lambda: self._create_dir(parent_index=index))
        delete_dir_action = QAction("Delete a directory")
        delete_dir_action.triggered.connect(lambda: self.delete_dir(index))
        menu.addAction(create_dir_action)
        menu.addAction(delete_dir_action)
        menu.exec_(self.directories_view.viewport().mapToGlobal(position))

    def select_first_dir(self):
        """Select the first child of the root directory"""
        first_child_index = self.directories_model.index(
            self.ROOT_DIR).child(0, 0)
        proxy_index = self.directories_proxy.mapFromSource(first_child_index)
        self.directories_view.setCurrentIndex(proxy_index)

    def _hide_unnecessary_columns(self, view):
        for column in range(1, 4):
            view.setColumnHidden(column, True)

    # TODO: Delete it during a cleanup
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
        proxy_index = self.directories_view.selectionModel().currentIndex()
        model_index = self.directories_proxy.mapToSource(proxy_index)
        return self.directories_model.filePath(model_index)

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
        self.files_model.setFilter(QDir.NoFilter)
        self.files_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)

    def save_and_create_note(self):
        if self.notes_text.toPlainText() != '' or self.notes_text.current_file is not None:
            self.save_note()
        self.create_note()

    def create_note(self, clear_selection=True):
        if clear_selection:
            self.files_view.clearSelection()
        self.notes_text.current_file = None
        self.parent.setWindowTitle(self.parent.window_title)
        self.notes_text.setFocus()
        self.notes_text.text_has_changed = False

    def save_note(self, selection_changed=False):
        cursor_position = self.notes_text.cursor_position
        if not self.notes_text.text_has_changed:
            return True

        if self.notes_text.current_file is None:
            new_filename = self.notes_text.create_abs_file_path(
                directory=self._get_current_dir())
            try:
                self.notes_text.save_file(new_filename, check_file_exists=True)
            except CannotSaveFileError:
                return
            self.notes_text.current_file = new_filename
            self._rename_window()
            self.select_file_by_name(new_filename)
        else:
            self.notes_text.save_file()
            try:
                self._rename_note(selection_changed)
            except CannotRenameFileError:
                return False

        self.notes_text.text_has_changed = False
        self._rename_window()
        self.notes_text.cursor_position = cursor_position
        return True

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
                QMessageBox.critical(
                    self,
                    'File Cannot Be Deleted',
                    'The note file cannot be deleted.')

    def note_changed(self):
        self._rename_window()

    def file_changed(self):
        if self.save_note(selection_changed=True):
            current_index = self.files_view.currentIndex()
            current_index = self.files_proxy.mapToSource(current_index)
            self.notes_text.current_file = self.files_model.filePath(
                current_index)
            self.notes_text.text_has_changed = False
            self._rename_window()

    def _rename_note(self, selection_changed=True):
        selected_file_index = self.files_view.currentIndex()
        current_file = self.notes_text.current_file
        new_filename = self.notes_text.create_abs_file_path()

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

    def _create_dir(self,
                    *args,
                    parent_index=None,
                    title='Create a directory',
                    **kwargs):
        """
        Create a directory

        Directory will be created as a subdirectory, if index of an existing
        directory is provided. It will be created in the root directory
        otherwise.

        Parameters
        ----------
        parent_index : QModelIndex
            Index of the parent directory
        title : str
            Title of the input dialog

        Returns
        -------
        bool
            True is returned, if the directory is created. False otherwise.
        """
        current_index = self.directories_view.currentIndex()
        if parent_index is not None:
            selected_dir = self.get_dir_from_index(parent_index)
            if selected_dir == '':
                self.directories_view.clearSelection()
                selected_dir = self.ROOT_DIR
        else:
            selected_dir = self.ROOT_DIR
        dirname, is_ok = QInputDialog.getText(self,
                                              title,
                                              'Directory name:')
        if is_ok:
            dir_path = os.path.join(selected_dir, dirname)
            was_created = QDir().mkdir(dir_path)
            if not was_created:
                QMessageBox.critical(self,
                                     'Directory Cannot Be Created',
                                     'The directory cannot be created.')
                self.directories_view.setCurrentIndex(current_index)
            else:
                self.select_dir_by_path(dir_path)
        else:
            was_created = False
        return is_ok and was_created

    def _create_first_dir(self):
        """Create the first directory, if all have been were deleted"""
        while True:
            if self._create_dir(title='Create the First Directory'):
                break

    def delete_dir(self, index):
        """Delete a directory specified by the index

        A sibling directory below the deleted one will be selected. A sibling
        directory above the deleted one will be selected, if there is no
        directory below it. A parent directory will be selected,
        if the deleted one has no siblings. Input dialog requesting a name
        of the new directory will appear, if the deleted directory was
        the last one in the notes directory.

        Parameters
        ----------
        index : QModelIndex
            Index of the directory to be deleted.
        """
        current_directory = self.get_dir_from_index(index)
        new_index = self.index_of_sibling_or_parent(index)
        if self.get_dir_from_index(new_index) == self.ROOT_DIR:
            self.files_model.setNameFilters([''])
            self.files_model.setNameFilterDisables(False)

            self.directories_view.setCurrentIndex(new_index)
            rmdir_recursive(current_directory,
                            dir_model=self.directories_model)
            while True:
                if self._create_dir():
                    break

            self.files_model.setNameFilters([])
            self.files_model.setNameFilterDisables(True)
        else:
            self.directories_view.setCurrentIndex(new_index)
            try:
                rmdir_recursive(current_directory,
                                dir_model=self.directories_model)
            except NotFileOrDirError:
                QMessageBox.critical(
                    self,
                    'Cannot Be Deleted',
                    'The selected item is not a file nor a directory.')
                self.select_first_dir()

        current_note = self.notes_text.current_file
        if current_note is not None and not os.path.exists(current_note):
            self.create_note(clear_selection=False)

    def get_dir_from_index(self, index):
        """Get an absolute path to the directory under the index

        Parameters
        ----------
        index : QModelIndex
            Index of the directory

        Returns
        -------
        str
            Absolute path of the directory
        """
        model_index = self.directories_proxy.mapToSource(index)
        return self.directories_model.filePath(model_index)

    def _select_item_by_path(self, path, widget):
        """Select the item of a QTreeView widget provided as a path

        Parameters
        ----------
        path : str
            An absolute path to the item
        widget : QTreeView
            A widget, where the item should be selected
        """
        proxy_model = widget.model()
        model = proxy_model.sourceModel()
        original_index = model.index(path)
        original_proxy_index = proxy_model.mapFromSource(original_index)
        widget.setCurrentIndex(original_proxy_index)

    def select_dir_by_path(self, dir_path):
        """Select a directory in the directories_view widget

        Parameters
        ----------
        dir_path : str
            An absolute path to the directory
        """
        self._select_item_by_path(dir_path, self.directories_view)

    def select_file_by_name(self, file_path):
        """Select a file in the files_view widget

        Parameters
        ----------
        file_path : str
            An absolute path to the file
        """
        self.files_view.selectionModel().selectionChanged.disconnect(
            self.file_changed)
        self._select_item_by_path(file_path, self.files_view)
        self.files_view.selectionModel().selectionChanged.connect(
            self.file_changed)

    def open_journal(self, dont_set_focus=False):
        """ Open a journal file, create a new one, if it doesn't exist

        Parameters
        ----------
        dont_set_focus : bool
            It doesn't set focus to journal_text widget, if it's True.
        """
        date = self.journal_calendar.selectedDate()
        year, month, day = (f'{date.year():0>4}',
                            f'{date.month():0>2}',
                            f'{date.day():0>2}',
                            )
        path_to_journal = os.path.join(self.ROOT_DIR,
                                       '.journal__',
                                       year,
                                       month)
        if not QDir().exists(path_to_journal):
            QDir().mkpath(path_to_journal)
        journal_name = f'{year}-{month}-{day}.md'
        journal_file_path = os.path.join(path_to_journal, journal_name)
        cursor_position = 0
        if not QFile.exists(journal_file_path):
            with open(journal_file_path, 'wt') as file:
                file.write(f'{year}-{month}-{day}\n==========\n\n')
            cursor_position = 23

        self.journal_text.current_file = journal_file_path

        if not dont_set_focus:
            self.journal_text.setFocus()
        self.journal_text.cursor_position = cursor_position

    def save_journal(self):
        """Save the journal, if it has changed"""
        if not self.journal_text.text_has_changed:
            return 0
        self.journal_text.save_file()
        self.journal_text.text_has_changed = False

    def journal_file_changed(self):
        """Save an opened journal file and open the selected one"""
        if self.journal_text.current_file is not None:
            self.save_journal()
        self.open_journal()

    def _create_journal_dir(self):
        """Create a journal directory, if it doesn't exist."""
        calendar_dir = os.path.join(self.ROOT_DIR, '.journal__')
        if not QDir().exists(calendar_dir):
            QDir().mkpath(calendar_dir)

    @staticmethod
    def index_of_sibling_or_parent(index):
        """Return index of an item bellow, item above or parent

        Parameters
        ----------
        index : QModelIndex
            Index of an item whose sibling or parent should be returned.

        Returns
        -------
        QModelIndex
            Index of an item bellow, item above or parent item of the item
            specified with the index parameter.
        """
        my_row, my_column = index.row(), index.column()
        new_index = index.sibling(my_row + 1, my_column)
        if new_index.row() >= 0:
            return new_index
        new_index = index.sibling(my_row - 1, my_column)
        if new_index.row() >= 0:
            return new_index
        return index.parent()
