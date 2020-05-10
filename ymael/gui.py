# -*- coding: utf-8 -*-

import sys
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtWidgets import QApplication,QMessageBox
from PyQt5.QtGui import QIcon

from .core import Core
from .interface import *


class GraphicInterface(QApplication):

    def __init__(self, infos, rps_folder, icon_path, exit_func, minimized=False):
        super().__init__(sys.argv)

        self._license,self._license_short,null = infos
        self._core = Core(rps_folder, cli=False)
        self.setQuitOnLastWindowClosed(False)
        self._icon = QIcon(icon_path)
        self.setWindowIcon(self._icon)

        self._show_tray_icon()
        if not minimized:
            self._show_window()

        sys.exit(self._gui_exit(exit_func))

    def _show_tray_icon(self):
        tray_menu = {
                "Ouvrir Ymael":self._show_window,
                "Quitter":self.exit
                }
        self._tray = TrayIcon(self._core, self._icon, tray_menu)

    def _show_window(self):
        menu_bar = {
                "Fichier":{
                    "Quitter":self.exit
                    },
                "Aide":{
                    "À propos":self.about
                    },
                }
        self._window = MainWindow(self._core, menu_bar)

    def about(self):
        about_box = QMessageBox()
        about_box.setIcon(QMessageBox.Information)
        about_box.setWindowTitle("À propos")
        about_box.setText(self._license_short)
        about_box.setDetailedText(self._license)
        about_box.exec()

    def _gui_exit(self, exit_func):
        self.exec()
        exit_func()
