# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

try:
    # Linux
    import notify2, dbus
    logger.info("Using notify2 as notifier lib")
except ImportError:
    # Windows
    import win10toast
    logger.info("Using win10toast as notifier lib")


class Notifier:

    def __init__(self, system, soft_name, icons):
        self.system = system
        self.soft = soft_name
        if self.system == "Linux":
            self.icon = icon[0]
            self._os_send = self._linux_send
        elif self.system == "Windows":
            self.icon = icon[1]
            self._notifier = win10toast.ToastNotifier()
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
        self._notifier.show_toast(
                title,
                message,
                icon_path=self.icon,
                threaded=True,
                duration=10
                )
