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
                "www.edenya.net":EdenyaV3Parser,
                "v4.edenya.net":EdenyaV4Parser,
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
        self._extraction([url])
        filename, ext = os.path.splitext(filename)
        if extension:
            ext = extension
        assert ext in self._exporters.keys(), "Output format not supported."
        domain = self._get_domain(url)
        if not self._extract[domain].rps[url].is_posts_empty():
            self._exporters[ext](filename, self._extract[domain].rps[url])

    def _notify(self, null_notif, url="", delete=False):
        new_rps = []
        self._watcher = Watcher(self._filemanager.rps)
        if url and not delete:
            self._extraction([url])
            domain = self._get_domain(url)
            retrieved_date = self._extract[domain].rps[url].get_current_date()
            title = self._extract[domain].rps[url].get_title()
            self._watcher.watch(retrieved_date, title, url)
        elif url and delete:
            self._watcher.unwatch(url)
        else:
            if self._watcher.are_urls_to_check():
                urls = self._watcher.get_urls_to_check()
                self._extraction(urls)
                for url in urls:
                    domain = self._get_domain(url)
                    retrieved_date = self._extract[domain].rps[url].get_current_date()
                    title = self._extract[domain].rps[url].get_title()
                    # update new retrieved date
                    self._watcher.watch(retrieved_date, title, url, replace=True)
                    if self._extract[domain].rps[url].are_new_posts():
                        u, t, count, authors = self._extract[domain].rps[url].get_news_infos()
                        new_rps.append((url, title, count, authors))

            if new_rps or null_notif:
                Notifier(new_rps, self._filemanager.ymael_icon)

    def _extraction(self, urls):
        site_urls = {}
        for url in urls:
            domain = self._get_domain(url)
            if not domain in site_urls.keys():
                site_urls[domain] = list()
            site_urls[domain].append(url)

        self._extract = {}
        for domain, urls in site_urls.items():
            self._extract[domain] = self._parsers[domain](
                    urls,
                    self._secrets,
                    self._filemanager.rps
                    )

    def _get_domain(self, url):
        for key in self._parsers.keys():
            if key in url:
                return key
        return None
