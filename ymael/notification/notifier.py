# -*- coding: utf-8 -*-

import notify2


class Notifier:

    def __init__(self, infos, icon, null_notif=False):
        self._infos = infos
        self._icon = icon
        self._null_notif = null_notif
        self._total = 0
        self._smiley = "😭"
        self._message = "Patience... 😉"
        self._build_message()
        self._show_popup()

    def _build_message(self):
        if self._infos:
            self._smiley = "😄"
            messages = list()
            for news in self._infos:
                url, rp_title, new_posts, authors = news
                self._total += new_posts
                # TODO: better parsing of urls to get domains
                site = url.split("//")[1].replace("www.", "").split(".")[0]
                messages.append("{} : {} dans \"{}\" (par {})".format(site, new_posts, rp_title, ", ".join(authors)))
            self._message = "\n".join(messages)
        elif not self._infos and not self._null_notif:
            return

    def _show_popup(self):
        notify2.init("Ymael")
        notifier = notify2.Notification(
                "{} nouveau(x) post(s) ! {}".format(self._total, self._smiley),
                self._message,
                self._icon
            )
        notifier.show()
        return
