# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from functools import partial
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtCore import QThread

from .custom_menu import CustomMenu
from .timer import Timer


class TrayIcon(QSystemTrayIcon):

    def __init__(self, core_instance, qicon, menu_dict={}, parent=None):
        super().__init__(parent)
        self.setIcon(qicon)
        self.setVisible(True)
        self._core = core_instance

        self._thread = QThread()
        self._timer = Timer()
        self._timer.time_is_up.connect(self._work)
        self._timer.moveToThread(self._thread)
        self._thread.started.connect(self._timer.run)
        # self._start_timer() # auto-start watcher

        menu_dict = {
                **menu_dict,
                "Démarrer la surveillance":self._start_timer,
                "Arrêter la surveillance":self._stop_timer,
                "Retarder la surveillance de 30mn":partial(self._change_timer_times, 30, True),
                }

        self._menu = CustomMenu()
        self._menu.create_menu(menu_dict)
        self.setContextMenu(self._menu)
        self.show()

    def _start_timer(self):
        self._timer.start()
        self._thread.start()

    def _stop_timer(self):
        self._timer.stop()
        self._thread.quit()

    def _change_timer_times(self, minutes, delay=False):
        self._timer.change_times(minutes, delay)

    def _work(self):
        logger.debug("Time-triggered watch.")
        self._core.watch(True) # null_notif while debugging
