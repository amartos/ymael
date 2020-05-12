# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import QThread, QObject, pyqtSignal


class Timer(QObject):

    time_is_up = pyqtSignal()

    def __init__(self, minutes=60):
        super().__init__()
        self._running = False
        self._seconds = minutes*60
        self._delay = 0
        self._tick = 0

    def run(self):
        while self._running:
            logger.info("Time is up.")
            self.time_is_up.emit()
            self._wait()

    def _wait(self):
        self._tick = self._get_tick()[0]
        while self._get_tick()[1] > 0:
            QThread.sleep(1)
            self._tick -= 1
        self._delay = 0

    def _get_tick(self):
        total = self._seconds+self._delay
        remaining = self._tick
        elapsed = total - remaining
        return (total,remaining,elapsed)

    def change_times(self, minutes, delay):
        seconds = minutes*60
        elapsed = self._get_tick()[-1]
        if delay:
            msg = "Delaying auto-watch interval of {} minutes.".format(minutes)
            self._delay = seconds
        else:
            msg = "Changing auto-watch interval to every {} minutes.".format(minutes)
            self._seconds = seconds
        logger.info(msg)
        self._tick = self._get_tick()[0] - elapsed

    def start(self):
        minutes = int(self._seconds/60)
        logger.info("Starting auto-watch timer every {} minutes.".format(minutes))
        self._running = True

    def stop(self):
        logger.info("Stopping auto-watch.")
        self._running = False
        self._delay = 0
