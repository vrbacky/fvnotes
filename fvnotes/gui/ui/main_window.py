#!/usr/bin/env python3

import os
from pathlib import Path

from PyQt5.QtCore import QDir, Qt, QTimer, QFile, QSortFilterProxyModel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QSplitter, \
    QWidget, QCalendarWidget, QVBoxLayout, QFileSystemModel, QTreeView, \
    QMessageBox, QAction, QMenu, QInputDialog, QListWidget

from fvnotes import AUTHOR, NAME, VERSION
from fvnotes.exceptions import CannotRenameFileError, CannotSaveFileError, \
    NotFileOrDirError
from fvnotes.gui.ui.preferences import PreferencesDialog
from fvnotes.gui.ui.preferences_manager import PreferencesManager
from fvnotes.path import rmdir_recursive
from fvnotes.gui.ui.bars import MenuBar, ToolBar
from fvnotes.gui.ui.custom_widgets import TextEditGuide

PREFERENCES = PreferencesManager(AUTHOR, NAME)


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
        self.menu_bar.open_preferences.connect(self.open_preferences)
        self.show()
        self.change_color_scheme()

    def open_preferences(self):
        self.preferences = PreferencesDialog(settings=PREFERENCES.general,
                                             themes=PREFERENCES.themes)
        if self.preferences.exec_():
            print('closed')

    def change_color_scheme(self):
        general = PREFERENCES.general
        theme = PREFERENCES.themes[general['Theme']]

        self.setStyleSheet(
            f'QMainWindow{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QMenuBar{{'
            f'background-color: {theme["App_background"]};}}'

            f'QMenuBar::item{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QMenuBar::item::selected{{'
            f'background-color: {theme["Menu_selected"]};}}'

            f'QMenu{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QMenu::item::selected{{'
            f'background-color: {theme["Menu_selected"]};}}'

            f'QToolBar{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QToolButton::hover{{'
            f'background-color: {theme["Menu_selected"]};'
            f'color: {theme["Font_color"]}}}'

            f'QStatusBar{{'
            f'color: {theme["Font_color"]};}}'

            f'QTextEdit{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'font-size: {general["Notes/Font_size"]}pt;'
            f'font-family: {general["Notes/Font"]};}}'

            f'QTreeView{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'font-size: {general["Trees/Font_size"]}pt;'
            f'font: {general["Trees/Font"]};}}'

            f'QListWidget{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'font-size: {general["Trees/Font_size"]}pt;'
            f'font: {general["Trees/Font"]};}}'

            f'QListWidget:active{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'font-size: {general["Trees/Font_size"]}pt;'
            f'font: {general["Trees/Font"]};}}'

            f'QListWidget:item:selected{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'font-size: {general["Trees/Font_size"]}pt;'
            f'font: {general["Trees/Font"]};}}'

            f'QCalendarWidget QWidget{{'
            f'background-color: {theme["Widget_background"]};'
            f'font-size: {general["Journal/Font"]}pt;'
            f'font: {general["Journal/Font"]};}}'

            f'QCalendarWidget QToolButton{{'
            f'color: {theme["Font_color"]}}}'

            f'QCalendarWidget QToolButton::hover{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]}}}'

            f'QCalendarWidget QSpinBox{{'
            f'background-color: {theme["App_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QCalendarWidget QMenu{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};}}'

            f'QCalendarWidget QAbstractItemView:enabled{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_color"]};'
            f'selection-background-color: {theme["App_background"]};'
            f'selection-color: {theme["Font_color"]};}}'

            f'QCalendarWidget QAbstractItemView:disabled{{'
            f'background-color: {theme["Widget_background"]};'
            f'color: {theme["Font_inactive"]};}}'

            f'QCalendarWidget QWidget{{'
            f'alternate-background-color: {theme["App_background"]};}}'

            f'QScrollBar{{'
            f'background-color: {theme["App_background"]};}}'
        )

        self.main_widget.change_vertical_lines(
            general["Notes/Vertical_lines"],
            general["Journal/Vertical_lines"],
            theme["Vertical_line_color"]
        )

    def closeEvent(self, event):
        if self.main_widget.notes_text.current_file is not None:
            self.main_widget.notes_text.save_file()
            try:
                self.main_widget.rename_note()
            except CannotRenameFileError:
                event.ignore()
        self.main_widget.save_journal()
        PREFERENCES.favourites = self.main_widget.favourite_paths


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent

        self.root_dir = PREFERENCES.general['Journal_path']

        self.main_layout = QHBoxLayout()
        self.main_splitter = QSplitter()

        self.files_splitter = QSplitter()
        self.directories_model = QFileSystemModel()
        self.directories_proxy = QSortFilterProxyModel()
        self.directories_view = QTreeView(headerHidden=True)
        self.files_model = QFileSystemModel()
        self.files_proxy = QSortFilterProxyModel()
        self.files_view = QTreeView(headerHidden=True, rootIsDecorated=False)
        self.favourites = QListWidget()
        self.favourite_paths = set(PREFERENCES.favourites)

        notes_font = QFont(PREFERENCES.general['Notes/Font'],
                           PREFERENCES.general['Notes/Font_size'])
        self.notes_text = TextEditGuide(
            parent=self,
            font=notes_font
        )
        self.journal_widget = QWidget()
        self.journal_layout = QVBoxLayout()
        journal_font = QFont(PREFERENCES.general['Journal/Font'],
                             PREFERENCES.general['Journal/Font_size'])
        self.journal_text = TextEditGuide(
            parent=self,
            font=journal_font
        )
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
        self.files_splitter.addWidget(self.favourites)

        self.directories_model.setFilter(
            QDir.Dirs | QDir.NoDotAndDotDot | QDir.Name)
        self.directories_proxy.setSourceModel(self.directories_model)
        self.directories_proxy.setDynamicSortFilter(True)
        directories_model_index = self.directories_model.setRootPath(
            self.root_dir)
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

        self.favourites.setContextMenuPolicy(Qt.CustomContextMenu)
        self.favourites.customContextMenuRequested.connect(
            self.favourites_context_menu)

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
        self.favourites.itemClicked.connect(self._favourite_clicked)
        self.journal_calendar.selectionChanged.connect(
            self.journal_file_changed)

        self._update_favourites()
        self.timer.singleShot(1, self.select_first_dir)

    def files_context_menu(self, position):
        index = self.files_view.indexAt(position)
        file_path = self.get_path_to_file(index)
        if file_path != '':
            short_file_path = os.path.relpath(file_path, start=self.root_dir)

        menu = QMenu()
        delete_file_action = QAction('Delete the file')
        add_to_favourites_action = QAction('Add to favourites')
        if index.data() is None:
            delete_file_action.setEnabled(False)
            add_to_favourites_action.setEnabled(False)
        delete_file_action.triggered.connect(lambda: self.delete_note(index))
        add_to_favourites_action.triggered.connect(
            lambda: self._add_to_favourites(short_file_path))
        menu.addAction(delete_file_action)
        menu.addAction(add_to_favourites_action)
        menu.exec_(self.files_view.viewport().mapToGlobal(position))

    def favourites_context_menu(self, position):
        item = self.favourites.itemAt(position)

        menu = QMenu()
        delete_favourite_action = QAction('Remove the file')
        delete_favourite_action.triggered.connect(
                lambda: self._remove_from_favourites(item.text()))
        if item is None:
            delete_favourite_action.setEnabled(False)
        menu.addAction(delete_favourite_action)
        menu.exec_(self.favourites.viewport().mapToGlobal(position))

    def dirs_context_menu(self, position):
        index = self.directories_view.indexAt(position)

        menu = QMenu()
        create_dir_action = QAction("Create a directory")
        create_dir_action.triggered.connect(
            lambda: self._create_dir(parent_index=index))
        delete_dir_action = QAction("Delete the directory")
        if index.data() is None:
            delete_dir_action.setEnabled(False)
        delete_dir_action.triggered.connect(lambda: self.delete_dir(index))
        menu.addAction(create_dir_action)
        menu.addAction(delete_dir_action)
        menu.exec_(self.directories_view.viewport().mapToGlobal(position))

    def change_vertical_lines(self, notes_positions, journal_positions, color):
        self.notes_text.guides_positions = notes_positions
        self.journal_text.guides_positions = journal_positions
        self.notes_text.guides_color = color
        self.journal_text.guides_color = color

    def select_first_dir(self):
        """Select the first child of the root directory"""
        first_child_index = self.directories_model.index(
            self.root_dir).child(0, 0)
        proxy_index = self.directories_proxy.mapFromSource(first_child_index)
        self.directories_view.setCurrentIndex(proxy_index)

    def _rename_window(self, title=None):
        if title is None:
            title = self.parent.window_title
            if self.notes_text.current_file is not None:
                short_current_file = os.path.relpath(
                    self.notes_text.current_file,
                    start=self.root_dir)
                title += f' - {short_current_file}'
            if self.notes_text.text_has_changed:
                title = f'{title}*'
        self.parent.setWindowTitle(title)

    def _dir_changed(self):
        source_index = self.files_model.setRootPath(self.get_path_to_dir())
        proxy_index = self.files_proxy.mapFromSource(source_index)
        self.files_view.setRootIndex(proxy_index)
        if self.files_view.isColumnHidden(0):
            self.files_view.setColumnHidden(0, False)
        self.files_model.setFilter(QDir.NoFilter)
        self.files_model.setFilter(QDir.Files | QDir.NoDotAndDotDot)

    def save_and_create_note(self):
        if (self.notes_text.toPlainText() != '' or
                self.notes_text.current_file is not None):
            self.save_note()
        self.create_note()

    def clear_file_selection(self):
        note_abspath = self.get_path_to_file()
        is_file = os.path.isfile(note_abspath)
        is_in_notes = Path(self.root_dir) in Path(note_abspath).parents
        if is_file and is_in_notes:
            self.files_view.clearSelection()

    def create_note(self, clear_selection=True):
        if clear_selection:
            self.clear_file_selection()
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
                directory=self.get_path_to_dir())
            try:
                self.notes_text.save_file(new_filename, check_file_exists=True)
            except CannotSaveFileError:
                return False
            self.notes_text.current_file = new_filename
            self._rename_window()
            self.select_file_by_name(new_filename)
        else:
            self.notes_text.save_file()
            try:
                self.rename_note(selection_changed)
            except CannotRenameFileError:
                return False

        self.notes_text.text_has_changed = False
        self._rename_window()
        self.notes_text.cursor_position = cursor_position
        return True

    def delete_note(self, current_index):
        current_filename = self.get_path_to_file(current_index)

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
            self.notes_text.current_file = self.get_path_to_file()
            self.notes_text.text_has_changed = False
            self._rename_window()

    def rename_note(self, selection_changed=True):
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

    def get_path_to_dir(self, index=None):
        """Get a path to a directory specified by its index

        Parameters
        ----------
        index : QModelIndex
            Index of the directory in the directories_view widget whose path
            is returned. A current index of the directories_view widget
            will be used if not specified.

        Returns
        -------
        str
           Path to the directory specified by the index parameter.
        """
        if index is None:
            index = self.directories_view.currentIndex()
        model_index = self.directories_proxy.mapToSource(index)
        return self.directories_model.filePath(model_index)

    def get_path_to_file(self, index=None):
        """Get a path to a file specified by its index

        Parameters
        ----------
        index : QModelIndex
            Index of the file in the files_view widget whose path is returned.
            A current index of the files_view widget will be used if not
            specified.

        Returns
        -------
        str
           Path to the file specified by the index parameter.
        """
        if index is None:
            index = self.files_view.currentIndex()
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
            selected_dir = self.get_path_to_dir(parent_index)
            if selected_dir == '':
                self.directories_view.clearSelection()
                selected_dir = self.root_dir
        else:
            selected_dir = self.root_dir
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
        current_directory = self.get_path_to_dir(index)
        new_index = self.index_of_sibling_or_parent(index)
        if self.get_path_to_dir(new_index) == self.root_dir:
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
        path_to_journal = os.path.join(self.root_dir,
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
        calendar_dir = os.path.join(self.root_dir, '.journal__')
        if not QDir().exists(calendar_dir):
            QDir().mkpath(calendar_dir)

    def _favourite_clicked(self, item):
        short_path = item.text()
        if self.save_note(selection_changed=True):
            abs_path = os.path.join(self.root_dir, short_path)
            if os.path.isfile(abs_path):
                self.select_dir_by_path(os.path.dirname(abs_path))
                self.select_file_by_name(abs_path)
                self.file_changed()

            else:
                QMessageBox.critical(
                    self,
                    "File doesn't exist",
                    (f"File {abs_path} doesn't exist.\n"
                     "It will be removed from favourites."))
                self._remove_from_favourites(
                    self.favourites.currentItem().text())

    def _update_favourites(self):
        """Clear favourities and fill in paths in favourite_paths"""
        self.favourites.clear()
        for i, item in enumerate(self._sort_paths(self.favourite_paths)):
            self.favourites.addItem(item)

    def _remove_from_favourites(self, path):
        """Remove the path from favourite_paths"""
        self.favourite_paths.remove(path)
        self._update_favourites()

    def _add_to_favourites(self, path):
        """Add the path to self.favourite_paths"""
        self.favourite_paths.add(path)
        self._update_favourites()

    @staticmethod
    def _sort_paths(paths):
        """Hierarchically sort the paths

        Parameters
        ----------
        paths : list
            A list of paths to be sorted.

        Returns
        -------
        generator
            Hierarchically sorted paths.
        """
        sorted_paths = sorted(paths, key=lambda path: (os.path.dirname(path),
                                                       os.path.basename(path)))
        return (path for path in sorted_paths)

    @staticmethod
    def _hide_unnecessary_columns(view):
        for column in range(1, 4):
            view.setColumnHidden(column, True)

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
