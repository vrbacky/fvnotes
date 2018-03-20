#!/usr/bin/env python3


class FVnotesError(Exception):
    pass


class CannotSaveFileError(FVnotesError):
    pass


class CannotRenameFileError(FVnotesError):
    pass
