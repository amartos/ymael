# -*- coding: utf-8 -*-

import os, platform

from .parser import *
from .notification import *
from .export import *
from .interface import *
from .rp_manager import *


class Ymael:

    def __init__(self, cli=True):
        if platform.system() == "Windows":
            local = os.getenv('%LOCALAPPDATA%')
            self._data_folder = local+"/ymael/"
        else:
            self._data_folder = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))+"/ymael/"

        self._rps_folder = self._data_folder+"rps/"
        for folder in [self._data_folder,self._rps_folder]:
            if not os.path.exists(folder):
                os.mkdir(folder)

        self._ymael_icon = ""

        self._parsers = {
                "www.edenya.net":EdenyaV3Parser,
                "v4.edenya.net":EdenyaV4Parser,
            }

        if cli:
            self._launch_cli()

    def _launch_cli(self):
        self._cli = CommandLine()
        self._secrets = self._cli.get_secrets()
        url = self._cli.get_url()
        if self._cli.do_export():
            filename = self._cli.get_filename()
            self._export(url, filename)
        else:
            null_notif = self._cli.get_null_notif()
            delete_url = self._cli.get_delete_url()
            self._watch(null_notif, url, delete_url)

    def _export(self, url, filename):
        self._extraction([url])
        domain = self._get_domain(url)
        if not self._extract[domain].rps[url].is_posts_empty():
            PanExporter(filename, self._extract[domain].rps[url])

    def _watch(self, null_notif, url, delete):
        self._watcher = Watcher(self._rps_folder)
        if url and not delete:
            self._set_in_watcher(url)
        elif url and delete:
            self._watcher.unwatch(url)
        else:
            self._notify(null_notif)

    def _set_in_watcher(self):
        self._extraction([url])
        domain = self._get_domain(url)
        retrieved_date = self._extract[domain].rps[url].get_current_date()
        title = self._extract[domain].rps[url].get_title()
        self._watcher.watch(retrieved_date, title, url)

    def _notify(self, null_notif):
        new_rps = []
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
            Notifier(new_rps, self._ymael_icon)

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
                    self._rps_folder
                    )

    def _get_domain(self, url):
        for key in self._parsers.keys():
            if key in url:
                return key
        return None
