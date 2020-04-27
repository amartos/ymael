# -*- coding: utf-8 -*-

import os
import platform
from datetime import datetime

from .parser import *
from .notification import *
from .export import *
from .files import *
from .interface import *
from .rp_manager import *


class Ymael:

    @classmethod
    def from_command_line(cls):
        cls._cli = CommandLine()
        cls._secrets = {
                "pseudo":cls._cli.login,
                "password":cls._cli.password
            }

        return cls()

    def __init__(self, cli=True):
        os_system = platform.system()
        if os_system == "Linux":
            self._filemanager = FileManager.linux_system_init()
        elif os_system == "Windows":
            self._filemanager = FileManager.windows_system_init()

        self._parsers = {
                "edenya.net":EdenyaParser,
            }

        self._exporters = {
                ".pdf":PanExporter.pdf,
                ".odt":PanExporter.odt,
                ".docx":PanExporter.docx,
                ".md":PanExporter.md
            }

        self._notifier_config = Config.load_watch_list(
                self._filemanager.watch_list,
                self._filemanager.charname_file)

        if cli:
            self._cli.treat(self._export, self._notify)
        else:
            GUI(self._export, self._notify)

    def _export(self, url, filename, extension=""):
        self._extraction(url)
        filename, ext = os.path.splitext(filename)
        if extension:
            ext = extension
        assert ext in self._exporters.keys(), "Output format not supported."
        if not self._extract.rp.is_posts_empty():
            self._exporters[ext](filename, self._extract.rp)

    def _notify(self, null_notif, url="", delete=False):
        new_rps = []
        self._watcher = Watcher(self._filemanager.rps)
        if url and not delete:
            self._extraction(url)
            retrieved_date = self._extract.rp.get_current_date()
            title = self._extract.rp.get_title()
            self._watcher.watch(retrieved_date, title, url)
        elif url and delete:
            self._watcher.unwatch(url)
        else:
            if self._watcher.are_urls_to_check():
                urls = self._watcher.get_urls_to_check()
                for url in urls:
                    self._extraction(url)
                    retrieved_date = self._extract.rp.get_current_date()
                    title = self._extract.rp.get_title()
                    self._watcher.watch(retrieved_date, title, url, replace=True)
                    if self._extract.rp.are_new_posts():
                        u, t, count, authors = self._extract.rp.get_news_infos()
                        new_rps.append((url, title, count, authors))
                    self._extract.rp.close_db() # avoid ClosedDB issues

            if new_rps or null_notif:
                Notifier(new_rps, self._filemanager.ymael_icon)

    def _extraction(self, url):
        for key in self._parsers:
            if key in url:
                self._extract = self._parsers[key](
                        url,
                        self._secrets,
                        self._filemanager.rps
                        )
