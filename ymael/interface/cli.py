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

        login = args.login
        password = get_secrets(login)
        if not password or args.password:
            password = set_secrets(login)
        self._secrets = (login, password)

        # if not export, notify
        self._export = False
        self._null_notif = args.null_notif
        if self._url and args.filename:
            self._filename = args.filename
            self._export = True

    def get_url(self):
        return self._url

    def get_filename(self):
        return self._filename

    def get_secrets(self):
        return self._secrets

    def get_null_notif(self):
        return self._null_notif

    def do_export(self):
        return self._export
