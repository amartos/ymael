# -*- coding: utf-8 -*-

import os,re
import logging
logger = logging.getLogger(__name__)

from .parser import *
from .export import *
from .rp_manager import *
from .secrets import *


class Core:

    def __init__(self, rps_folder, notifier):
        self._rps_folder = rps_folder
        self._notifier = notifier

        self._ymael_icon = ""

        self._parsers = {
                "edenya.net":EdenyaParser,
            }

        self._secrets = {}
        for domain in self._parsers.keys():
            self._secrets[domain] = Secrets(domain)

    def get_supported_domains(self):
        return sorted(list(self._parsers.keys()))

    def get_domain_secrets(self, domain):
        return self._secrets[domain].get_secrets()

    def set_domain_secrets(self, secrets, domain="", url=""):
        if not domain and url:
            domain = self._get_domain(url)
        elif not domain and not url:
            raise ValueError("Provide either a url or a domain to set secrets.")
        elif not all(secrets):
            raise ValueError("Provide both login and password to set secrets.")
        self._secrets[domain].set_secrets(secrets)

    def is_url_valid(self, url):
        # see https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not/7160778#7160778
        url_regex = re.compile(
                r'^(?:http|ftp)s?://' # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                r'localhost|' #localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                r'(?::\d+)?' # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )
        valid = bool(re.match(url_regex, url))
        if not valid and self._cli:
            raise ValueError("url not valid: %s", url)

        return valid

    def export(self, urls, filename="", path_ext=tuple()):
        if not filename and not path_ext:
            raise ValueError("Filename or (path & extension) is mandatory.")
        self._extraction(urls)
        for url in urls:
            domain = self._get_domain(url)
            if not self._extract[domain].rps[url].is_posts_empty():
                if not filename and path_ext:
                    path, ext = path_ext
                    name = self._extract[domain].rps[url].get_current_date(string=True)
                    name += "_"+self._extract[domain].rps[url].get_title()
                    filename = os.path.join(path,name+ext)
                PanExporter(filename, self._extract[domain].rps[url])
                filename = None

    def supported_extensions(self):
        return PanExporter.supported_extensions()

    def init_watcher(self):
        self._watcher = Watcher(self._rps_folder)

    def watch(self, null_notif=False, urls=[], delete=False):
        try:
            self._watcher.watch
        except (NameError, AttributeError):
            self.init_watcher()

        if urls and not delete:
            self._set_in_watcher(urls)
        elif urls and delete:
            self._watcher.unwatch(urls)
        else:
            logger.info("Watching db URLs.")
            self._notify(null_notif)

    def _set_in_watcher(self, urls):
        self._extraction(urls)
        infos = []
        for url in urls:
            domain = self._get_domain(url)
            retrieved_date = self._extract[domain].rps[url].get_current_date()
            title = self._extract[domain].rps[url].get_title()
            infos.append((retrieved_date, title, url))
        self._watcher.watch(infos)

    def _notify(self, null_notif):
        new_rps = []
        if self._watcher.are_urls_to_check():
            urls = self._watcher.get_urls_to_check()
            self._extraction(urls)
            infos = []
            for url in urls:
                domain = self._get_domain(url)
                retrieved_date = self._extract[domain].rps[url].get_current_date()
                title = self._extract[domain].rps[url].get_title()
                infos.append((retrieved_date, title, url))
                # update new retrieved date
                if self._extract[domain].rps[url].are_new_posts():
                    u, t, count, authors = self._extract[domain].rps[url].get_news_infos()
                    new_rps.append((url, title, count, authors))

        self._watcher.watch(infos, replace=True)

        if new_rps or null_notif:
            title,message = self._build_message(new_rps)
            self._notifier.send(title,message)

    def _build_message(self, new_rps):
        total = 0
        smiley = "😭"
        message = "Patience... 😉"
        if new_rps:
            smiley = "😄"
            messages = list()
            for news in new_rps:
                url, rp_title, new_posts, authors = news
                total += new_posts
                site = self._get_domain(url)
                messages.append("{} : {} dans \"{}\" (par {})".format(site, new_posts, rp_title, ", ".join(authors)))
            message = "\n".join(messages)
        title = "{} nouveau(x) post(s) ! {}".format(total, smiley)
        return title, message

    def _extraction(self, urls):
        site_urls = {}
        for url in urls:
            domain = self._get_domain(url)
            if not domain in site_urls.keys():
                site_urls[domain] = list()
            site_urls[domain].append(url)

        self._extract = {}
        for domain, urls in site_urls.items():
            secrets = self.get_domain_secrets(domain)
            if not all(secrets):
                logger.warning("No login and password defined for {}".format(domain))
                continue
            self._extract[domain] = self._parsers[domain](
                    urls,
                    self.get_domain_secrets(domain),
                    self._rps_folder
                    )

    def _get_domain(self, url):
        for key in self._parsers.keys():
            if key in url:
                return key

        raise ValueError("url not supported: %s", url)
