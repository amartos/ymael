# -*- coding: utf-8 -*-

import os
import platform

from .parser import *
from .notification import *
from .export import *
from .files import *
from .interface import *


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
                "www.edenya.net":EdenyaParser,
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

    def _notify(self, null_notif, url=""):
        if url:
            if not url in self._notifier_config.watch_list.keys() and "index.php" in url:
                self._notifier_config.watch_list[url] = tuple()

        meta_rps = dict()
        for url in self._notifier_config.watch_list.keys():
            self._extraction(url)
            meta_rps[url] = self._extract.rps

        try:
            date_format = self._extract.date_format
        except AttributeError:
            date_format = None

        notifier = Notifier(
                self._notifier_config.watch_list,
                self._notifier_config.charname,
                meta_rps,
                self._filemanager.ymael_icon,
                date_format,
                null_notif
            )

        self._notifier_config.save(notifier.watch_list)

    def _extraction(self, url):
        for key in self._parsers:
            if key in url:
                self._extract = self._parsers[key](
                        url,
                        self._secrets,
                        self._filemanager.rps
                        )
