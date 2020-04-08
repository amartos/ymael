# -*- coding: utf-8 -*-

import notify2
import datetime


class Notifier:

    def __init__(self, watch_list, charname, rps, icon, date_format="", null_notif=False, notify=True):
        self.watch_list = watch_list
        self._charname = charname
        self._icon = icon
        self._null_notif = null_notif
        self._total = 0
        self._to_notify = dict()
        self._smiley = "😭"
        self._message = "Patience... 😉"

        if self.watch_list:
            for url in self.watch_list.keys():
                if bool(rps[url]["posts"]):
                    self._update(url, rps[url], date_format)
        else:
            self._notify(no_url=True)
            notify = False

        if notify:
            self._notify()

    def _update(self, url, rps, date_format):
        dates = [datetime.datetime.strptime(d, date_format) for d in rps["posts"].keys()]
        dates.sort()

        last_date = datetime.datetime.strftime(dates[-1], date_format)

        new_posts = 0
        if self.watch_list[url]:
            last_read_date = datetime.datetime.strptime(self.watch_list[url][0], date_format)
            last_read_index = dates.index(last_read_date) + 1
            new_posts = len(dates[last_read_index:])

        self.watch_list[url] = (last_date, rps["title"])
        last_author = rps["posts"][last_date]["author"][0]

        if new_posts > 0 and not self._charname in last_author:
            self._total += new_posts
            self._to_notify[url] = (new_posts, rps["title"], last_author)

    def _notify(self, no_url=False):
        if self._to_notify:
            self._smiley = "😄"
            messages = list()
            for url in self._to_notify:
                site = url.split("//")[1]
                site = site.replace("www.", "")
                site = site.split(".")[0]
                count, title, last_author = self._to_notify[url]
                messages.append("{} : {} dans \"{}\" (dernier par {})".format(site, count, title, last_author))
                self._message = "\n".join(messages)
        elif not self._to_notify and not self._null_notif:
            return
        elif no_url:
            self._smiley = "😶"
            self._message = "Pas d'url à surveiller..."

        self._show_popup()

    def _show_popup(self):
        notify2.init("Ymael")
        notifier = notify2.Notification(
                "{} nouveau(x) post(s) ! {}".format(self._total, self._smiley),
                self._message,
                self._icon
            )
        notifier.show()
        return
