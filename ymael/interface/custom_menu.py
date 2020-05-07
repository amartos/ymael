# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QMenu,QAction


class CustomMenu(QMenu):

    def __init__(self, parent=None):
        super().__init__(parent)
        # This dictionary and its filling method is necessary for the menus to
        # work properly, as the methods will be lost if they are not stored
        self._menus = {self:{}}

    def create_menu(self, menu_dict, parent=None):
        if parent == None:
            parent = self

        for string,action in menu_dict.items():
            if isinstance(action, dict):
                new_menu = self._create_sub_menu(string, parent)
                self.create_menu(action, new_menu)
            else:
                self._create_menu_item(string, action, parent)

    def _create_sub_menu(self, string, parent):
        new_menu = QMenu("&"+string)
        parent.addMenu(new_menu)
        self._menus[new_menu] = {}
        return new_menu

    def _create_menu_item(self, string, action, parent):
        menu_action = QAction(string)
        menu_action.triggered.connect(action)
        self._menus[parent][string] = menu_action
        parent.addAction(menu_action)
