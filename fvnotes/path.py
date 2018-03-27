#!/usr/bin/env python3

import os
from PyQt5.QtCore import QDirIterator, QDir

from fvnotes.exceptions import NotFileOrDirError


def _create_recursive_dir_content(directory):
    """Create a list of items to be recursively deleted

    It creates a list containing directories and files that they can be
    deleted securely from the end (directories will be emptied before
    deletion).

    Parameters
    ----------
    directory : str
        A path to the directory.

    Returns
    -------
    list
        A list containing ordered items to be deleted.
    """
    to_be_deleted = [directory]

    subdirs = QDirIterator(directory, QDir.Dirs | QDir.NoDotAndDotDot)
    files = QDirIterator(directory, QDir.Files)

    while files.hasNext():
        to_be_deleted.append(files.next())

    while subdirs.hasNext():
        subdir = subdirs.next()
        to_be_deleted.extend(_create_recursive_dir_content(subdir))
    return to_be_deleted


def _delete_item(path, dir_model=None, file_model=None):
    """Delete a file or a directory

    Parameters
    ----------
    path : str
        A path to the file or the directory to be deleted.
    dir_model : QFileSystemModel
        A model whose rmdir() method will be used to remove directories.
        os.rmdir() method will be used, if the model is not specified.
    file_model : QFileSystemModel
        A model whose remove() method will be used to remove files.
        os.remove() method will be used, if the model is not specified.

    Returns
    -------
    bool
        Returns True if successful.
    """
    if os.path.isfile(path):
        if file_model is None:
            os.remove(path)
        else:
            file_model.remove(file_model.index(path))
    elif os.path.isdir(path):
        if dir_model is None:
            os.rmdir(path)
        else:
            dir_model.rmdir(dir_model.index(path))
    else:
        raise NotFileOrDirError
    return True


def rmdir_recursive(directory, dir_model=None, file_model=None):
    """Remove a directory recursively

    Parameters
    ----------
    directory : str
        A path to the directory to be deleted.
    dir_model : QFileSystemModel
        A model whose rmdir() method will be used to remove directories.
        os.rmdir() method will be used, if the model is not specified.
    file_model : QFileSystemModel
        A model whose remove() method will be used to remove files.
        os.remove() method will be used, if the model is not specified.

    Returns
    -------
    bool
        Returns True if successful.
    """
    paths_to_delete = _create_recursive_dir_content(directory)
    while paths_to_delete:
        path = paths_to_delete.pop()
        _delete_item(path, dir_model=dir_model, file_model=file_model)
    return True
