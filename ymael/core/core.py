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
        self._cli = False

        self._ymael_icon = ""

        self._parsers = {
                "edenya.net":EdenyaParser,
            }

        self._watcher = Watcher(self._rps_folder)
        self._panexporter = PanExporter()

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
            self._fatal_error("URL or domain not provided.")
            return
        elif not all(secrets):
            self._fatal_error("Login or password incorrect.")
            return
        self._secrets[domain].set_secrets(secrets)

    @staticmethod
    def is_url_valid(url):
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
        if not valid:
            logger.warning("URL is invalid: {}".format(url))

        return valid

    def export(self, urls, filename="", path_ext=tuple()):
        logger.info("Exporting: {} {} {}".format(repr(urls), repr(filename), repr(path_ext)))
        if not filename and not path_ext:
            self._fatal_error("Filename of path+ext was not provided.")
            return
        self._extraction(urls)
        for url in urls:
            domain = self._get_domain(url)
            if not self._extract[domain].rps[url].is_posts_empty():
                if not filename and path_ext:
                    path, ext = path_ext
                    name = self._extract[domain].rps[url].get_current_date(string=True)
                    name += "_"+self._extract[domain].rps[url].get_title()
                    # escaping filename characters for windows
                    name = name.replace(" ", "_").replace(":", "")
                    filename = os.path.join(path,name+ext)
                self._panexporter.convert(filename, self._extract[domain].rps[url])
                filename = None
            else:
                logger.warning("Posts of URL are empty: {}".format(url))
        self._notify_user("Export", "L'export est terminé.")

    def supported_extensions(self):
        return self._panexporter.supported_extensions()

    def export_ready(self):
        return self._panexporter.is_ready()

    def watch(self, null_notif=False, urls=[], delete=False):
        logger.info("Triggering watch. null_notif: {} ; delete: {} ; urls: {}".format(repr(null_notif), repr(delete), repr(urls)))
        if urls and not delete:
            self._set_in_watcher(urls)
        elif urls and delete:
            self._watcher.unwatch(urls)
            self._notify_user("Surveillance", "Les urls ont été correctement supprimées de la base de donnée.")
        else:
            self._watch_db_urls(null_notif)

    def _get_urls_infos(self, urls):
        infos = []
        for url in urls:
            domain = self._get_domain(url)
            if url in self._extract[domain].rps.keys():
                retrieved_date = self._extract[domain].rps[url].get_current_date()
                title = self._extract[domain].rps[url].get_title()
                infos.append((retrieved_date, title, url))
        if not infos:
            self._fatal_error("URLs infos not retrieved.")
        return infos

    def _set_in_watcher(self, urls):
        self._extraction(urls)
        infos = self._get_urls_infos(urls)
        if infos:
            self._watcher.watch(infos)

    def _watch_db_urls(self, null_notif):
        new_rps = []
        if self._watcher.are_urls_to_check():
            urls = self._watcher.get_urls_to_check()
            self._extraction(urls)
            infos = self._get_urls_infos(urls)
            if infos:
                logger.debug("Updating timestamps.")
                self._watcher.watch(infos, replace=True)

            for page in infos:
                null, title, url = page
                domain = self._get_domain(url)
                if self._extract[domain].rps[url].are_new_posts():
                    u, t, count, authors = self._extract[domain].rps[url].get_news_infos()
                    new_rps.append((url, title, count, authors))
        else:
            logger.info("There are no URLs to check.")

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
                self._fatal_error("Extraction: no secrets defined for domain: {}".format(domain))
                continue
            else:
                self._extract[domain] = self._parsers[domain](
                        urls,
                        secrets,
                        self._rps_folder
                        )

    def _get_domain(self, url):
        for key in self._parsers.keys():
            if key in url:
                return key

        logger.warning("URL's domain not supported")

    def _notify_user(self, title, message):
        logger.debug(message)
        self._stdout_message(title, message)

    def _fatal_error(self, error_message):
        logger.error(error_message)
        self._stdout_message("Erreur fatale", "Une erreur fatale s'est produite. Vérifiez les logs.")

    def is_cli(self):
        self._cli = True

    def _stdout_message(self, title, message):
        if self._cli:
            print(message)
        else:
            self._notifier.send(title,message)
