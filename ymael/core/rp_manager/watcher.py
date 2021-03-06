# -*- coding: utf-8 -*-

import os
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta

from .database import Database


class Watcher:

    def __init__(self, rps_dir):
        self.watcher = {}
        self._to_retrieve = []

        self._db = Database(os.path.join(rps_dir, "watched.db"))
        self._now = datetime.now()
        self._check_watch_table()
        self._load_watched()

    def watch(self, infos, replace=False):
        column_names = ["last_checked", "title", "url"]
        # this ignores if the entry is already in
        self._db.insert_rows("watch", column_names, infos, replace)
        for value in infos:
            retrieved_date, title, url = value
            if not url in self.watcher.keys():
                self.watcher[url] = (retrieved_date, title)
                logger.debug("URL added to watcher: {}".format(url))

    def unwatch(self, urls):
        conditions = [("url", url) for url in urls]
        self._db.delete_rows("watch", conditions, use_or=True)
        for url in urls:
            del self.watcher[url]
            logger.debug("URL removed from watcher: {}".format(url))

    def are_urls_to_check(self):
        self._check_dates()
        return bool(self._to_retrieve)

    def get_urls_to_check(self):
        return self._to_retrieve

    def get_storage_date_format(self):
        return self._db.get_date_format()

    def is_watched(self, url):
        return url in self.watcher.keys()

    def _check_dates(self):
        self._to_retrieve = []
        for url,infos in self.watcher.items():
            if self._now - timedelta(hours=1) > infos[0]:
                self._to_retrieve.append(url)

    def _check_watch_table(self):
        columns = [
                ("last_checked", "date", "not null"),
                ("title", "text", "not null"),
                ("url", "text", "not null")
                ]
        primary_keys = ["title", "url"]
        foreign_keys = [("title", "rps", "title")]
        if not self._db.is_table("watch"):
            self._db.create_table("watch", columns, primary_keys, foreign_keys)

    def _load_watched(self):
        self._db.search_rows("watch", column_order="last_checked")
        results = self._db.get_results()
        while results != None:
            retrieved_date, rp_title, url = results
            retrieved_date = datetime.strptime(retrieved_date, self._db.get_date_format())
            self.watcher[url] = (retrieved_date, rp_title)
            results = self._db.get_results()
