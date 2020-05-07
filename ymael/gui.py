# -*- coding: utf-8 -*-

import sys
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QApplication

from .core import Core
from .interface import *


class GraphicInterface(QApplication):

    def __init__(self, rps_folder, icon_path, exit_func, minimized=False):
        super().__init__(sys.argv)

        self._core = Core(rps_folder, cli=False)
        self.setQuitOnLastWindowClosed(False)

        self._show_tray_icon(icon_path)
        if not minimized:
            self._show_window()

        sys.exit(self._gui_exit(exit_func))

    def _show_tray_icon(self, icon_path):
        tray_menu = {
                "Ouvrir Ymael":self._show_window,
                "Quitter":self.exit
                }
        self._tray = TrayIcon(self._core, icon_path, tray_menu)

    def _show_window(self):
        menu_bar = {
                "Fichier":{
                    "Quitter":self.exit
                    },
                }
        self._window = MainWindow(self._core, menu_bar)

    def _gui_exit(self, exit_func):
        self.exec()
        exit_func()
