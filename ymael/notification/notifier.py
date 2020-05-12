# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)


class Notifier:

    def __init__(self, system, soft_name, icon):
        self.system = system
        self.soft = soft_name
        self.icon = icon
        if system == "Linux":
            self._define_linux_notifier()
        elif system == "Windows":
            self._define_windows_notifier()
            pass

    def send(self, title, message):
        pass

    def _define_linux_notifier(self):
        logger.info("Using notify2 as notifier lib")
        import notify2
        notify2.init("Ymael")
        def send(self, title, message):
            logger.debug("Notifying: {} - {}".format(title,message))
            notifier = notify2.Notification(
                    title+"\n"+message,
                    self.icon
                )
            notifier.show()
            return

    def _define_windows_notifier(self):
        pass
