#!/usr/bin/env python3

from collections import defaultdict

from PyQt5.QtCore import QSettings


class PreferencesManager:
    def __init__(self, author, app_name):
        author = author.replace(' ', '_').lower()
        app_name = app_name.replace(' ', '_').lower()
        self._general_settings = QSettings(author, app_name)
        self._themes_settings = QSettings(author, f'{app_name}-themes')
        self._code_highlight_settings = QSettings(author,
                                                  f'{app_name}-code_highlight')
        self._favourites_path =\
            QSettings(author, f'{app_name}-favourites').fileName()

        self.general_defaults = {
            'Theme': ('Dark', str),
            'Journal_path': ('/home/fv-user/notes', str),
            'Notes/Font': ('Ubuntu Mono', str),
            'Notes/Font_size': (11, int),
            'Notes/Vertical_lines': ([72, 80], int),
            'Trees/Font': ('Ubuntu', str),
            'Trees/Font_size': (10, int),
            'Journal/Font': ('Ubuntu', str),
            'Journal/Font_size': (10, int),
            'Journal/Vertical_lines': ([80], int),
        }

        self.themes_defaults = {
            'Dark/App_background': ('#202020', str),
            'Dark/Menu_selected': ('#454545', str),
            'Dark/Widget_background': ('#101010', str),
            'Dark/Font_color': ('#B5B5B5', str),
            'Dark/Font_inactive': ('#2F2F2F', str),
            'Dark/Vertical_line_color': ('#353535', str),
            'Light/App_background': ('#D0D0D0', str),
            'Light/Menu_selected': ('#A0A0A0', str),
            'Light/Widget_background': ('#F5F5F5', str),
            'Light/Font_color': ('#050505', str),
            'Light/Font_inactive': ('#A0A0A0', str),
            'Light/Vertical_line_color': ('#C0C0C0', str),
        }

        self.highlights_defaults = {
            'Dark/keyword': ('CC7832', str),
            'Dark/operator': ('A9B7C6', str),
            'Dark/brace': ('A9B7C6', str),
            'Dark/funcname': ('FFC66D bold', str),
            'Dark/string': ('6A8759', str),
            'Dark/docstring': ('77B767 italic', str),
            'Dark/comment': ('808080 italic', str),
            'Dark/self': ('8F4F7C', str),
            'Dark/numbers': ('6897BB', str),
        }

        self._general = self._read_config(self._general_settings,
                                          self.general_defaults,
                                          deep=False)
        self._themes = self._read_config(self._themes_settings,
                                         self.themes_defaults)
        self._code_highlights = self._read_config(
            self._code_highlight_settings,
            self.highlights_defaults)

        if self._general['Theme'] not in self._themes:
            self._general['Theme'] = list(self._themes.keys())[0]

    def _read_config(self, settings, defaults, deep=True):
        if len(settings.allKeys()) == 0:
            self._create_default_config(settings, defaults)
        if deep:
            func = self._get_deep_config
        else:
            func = self._get_config
        return func(settings, defaults)

    @staticmethod
    def _create_default_config(settings, default_values):
        for key, (default_value, default_type) in default_values.items():
            settings.setValue(key, default_value)

    def _get_config(self, settings, defaults):
        keys = settings.allKeys()
        values = defaultdict(dict)
        for key in keys:
            default_value, default_type = defaults.get(key, ('', str))
            value = settings.value(key, type=default_type)
            if isinstance(default_value, list):
                value = self.get_iterable_value(value)
            values[key] = value
        return values

    def _get_deep_config(self, settings, defaults):
        temp_values = self._get_config(settings, defaults)
        values = defaultdict(dict)
        for key, value in temp_values.items():
            keys = key.split('/', maxsplit=1)
            values[keys[0]][keys[1]] = value
        return values

    @staticmethod
    def get_iterable_value(value):
        try:
            return [i for i in value]
        except TypeError:
            return [value]

    @staticmethod
    def set_iterable_value(value):
        try:
            iter(value)
            if len(value) < 2:
                return value[0]
            return [i for i in value]
        except TypeError:
            return value

    @property
    def general(self):
        return self._general

    @general.setter
    def general(self, new_settings):
        self._general = new_settings
        for key, value in new_settings.items():
            if isinstance(self.general_defaults[key][0], list):
                value = self.set_iterable_value(value)
            self._general_settings.setValue(key, value)

    @property
    def themes(self):
        return self._themes

    @themes.setter
    def themes(self, new_settings):
        self._themes = new_settings
        self._set_deep_settings(self._themes_settings, new_settings)

    @property
    def code_highlights(self):
        return self._code_highlights

    @code_highlights.setter
    def code_highlights(self, new_settings):
        self._code_highlights = new_settings
        self._set_deep_settings(self._code_highlight_settings,
                                new_settings)

    @property
    def favourites(self):
        try:
            with open(self._favourites_path, 'r') as f:
                for line in f.readlines():
                    yield line.strip()
        except FileNotFoundError:
            return []

    @favourites.setter
    def favourites(self, new_favourites):
        with open(self._favourites_path, 'w') as f:
            for fav in new_favourites:
                print(fav, file=f)
