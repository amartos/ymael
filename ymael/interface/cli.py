import argparse

from .tools import *


class CommandLine:

    def __init__(self):
        parser = argparse.ArgumentParser(self,
                description="Extract rp infos from the specified URL. "\
                "If FILENAME path is given, it exports the topic to it. "\
                "Else, it adds the URL to a watch list, which notifies the "
                "user for new posts."
            )

        parser.add_argument(
                "login",
                help="login of account to use",
            )

        parser.add_argument(
                "-u", "--url",
                help="url of the topic to be exported/added in watch list, "\
                "which does not need to be the url of the first page of the "\
                "topic"
            )
        parser.add_argument(
                "-f", "--filename",
                help="export the rp topic to the filename in "\
                "one of the supported formats: pdf, odt, docx, md"
            )
        parser.add_argument(
                "-n", "--null_notif",
                help="notify even if there are no new posts",
                action="store_true"
            )
        parser.add_argument(
                "-p", "--password",
                help="change stored password ; "\
                "set on if login is not found in the keyring",
                action="store_true"
            )

        args = parser.parse_args()

        self._url = ""
        if args.url and is_url_valid(args.url):
            self._url = args.url

        self.login = args.login
        self.password = get_secrets(self.login)
        if not self.password or args.password:
            self.password = set_secrets(self.login)

        self.url = args.url
        self.filename = args.filename
        self.null_notif = args.null_notif

    def treat(self, exporter, notifier):
        if self.filename:
            exporter(self.url, self.filename)
        else:
            notifier(self.null_notif, self.url)
