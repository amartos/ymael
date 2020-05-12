# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import notify2
logger.info("Using notify2 as notifier lib")


class Notifier:

    def __init__(self, system, soft_name, icon):
        self.system = system
        self.soft = soft_name
        self.icon = icon
        if self.system == "Linux":
            self._os_send = self._linux_send
        elif self.system == "Windows":
            self._os_send = self._windows_send

    def send(self, title, message):
        logger.debug("Notifying: {} - {}".format(title,message))
        self._os_send(title, message)

    def _linux_send(self, title, message):
        notify2.init(self.soft)
        notifier = notify2.Notification(title, message, self.icon)
        notifier.show()
        return

    def _windows_send(self, title, message):
        pass
