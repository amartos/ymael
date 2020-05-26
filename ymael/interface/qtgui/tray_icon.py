# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from functools import partial
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtCore import QThread

from .custom_menu import CustomMenu
from .timer import Timer


class TrayIcon(QSystemTrayIcon):

    def __init__(self, core_instance, qicon, menu_dict={}, parent=None, autostart_timer=False):
        super().__init__(parent)
        self.setIcon(qicon)
        self.setVisible(True)
        self._core = core_instance

        self._thread = QThread()
        self._timer = Timer()
        self._timer.time_is_up.connect(self._work)
        self._timer.moveToThread(self._thread)
        self._thread.started.connect(self._timer.run)
        self._timer_is_on = False
        self._watch_labels = ["Démarrer la surveillance", "Arrêter la surveillance"]

        menu_dict = {
                **menu_dict,
                self._watch_labels[int(self._timer_is_on)]:self._toggle_timer,
                "Retarder la surveillance de 30mn":partial(self._change_timer_times, 30, True),
                }

        self._menu = CustomMenu()
        self._menu.create_menu(menu_dict)
        self.setContextMenu(self._menu)

        if autostart_timer:
            self._toggle_timer()
        self.show()

    def _toggle_timer(self):
        former = self._watch_labels[int(self._timer_is_on)]
        new = self._watch_labels[int(not self._timer_is_on)]
        if self._timer_is_on:
            self._stop_timer()
        else:
            self._start_timer()
        self._menu.change_menu_label(former, new)

    def _start_timer(self):
        self._timer_is_on = True
        self._timer.start()
        self._thread.start()

    def _stop_timer(self):
        self._timer_is_on = False
        self._timer.stop()
        self._thread.quit()

    def _change_timer_times(self, minutes, delay=False):
        self._timer.change_times(minutes, delay)

    def _work(self):
        logger.debug("Time-triggered watch.")
        self._core.watch(True) # null_notif while debugging
