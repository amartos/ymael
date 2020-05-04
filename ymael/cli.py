import argparse
import logging
logger = logging.getLogger(__name__)


from .core import Core
from .gui import GraphicInterface


class CommandLine(Core):

    def __init__(self, rps_folder, login_file, exit_func):
        super().__init__(rps_folder, login_file)
        self._define_args_parser()
        self._parse_args()

        if self._gui:
            GraphicInterface(rps_folder, login_file, exit_func)
        else:
            if self._do_export:
                self.export([self._url], self._filename)
            else:
                self.watch(self._null_notif, self._url, self._delete_url)
            exit_func()

    def _define_args_parser(self):
        self._args_parser = argparse.ArgumentParser(self,
                description="Extract rp infos from the specified URL. "\
                "If FILENAME path is given, it exports the topic to it. "\
                "Else, it adds the URL to a watch list, which notifies the "
                "user for new posts."
            )

        self._args_parser.add_argument(
                "-a", "--account-secrets",
                help="Login and password of account to use. If it has not been already defined, it is mandatory. "\
                "The last couple login/password used will be remembered and used as default if this option is not "\
                "used afterwards. The default can be changed with this option." \
                "The secrest are given in the form of login:password. You also need to provide a url of the "\
                "associated website via the -u option.",
            )

        self._args_parser.add_argument(
                "-u", "--url",
                help="url of the topic to be exported/added in watch list, "\
                "which does not need to be the url of the first page of the "\
                "topic"
            )
        self._args_parser.add_argument(
                "-f", "--filename",
                help="export the rp topic to the filename in "\
                "one of the supported formats: pdf, odt, docx, md"
            )
        self._args_parser.add_argument(
                "-n", "--null_notif",
                help="notify even if there are no new posts",
                action="store_true"
            )
        self._args_parser.add_argument(
                "-d", "--delete_url",
                help="remove url from watched urls database",
                action="store_true"
            )
        self._args_parser.add_argument(
                "-l", "--log_level",
                help="Set log level. Values can either be 1 (WARNING), 2 (INFO) or 3 (DEBUG)."
            )

        self._args_parser.add_argument(
                "-g", "--gui",
                help="Launch graphic user interface. Except for logging level, "\
                "all other options are ignored.",
                action="store_true"
            )

    def _parse_args(self):
        self._args = self._args_parser.parse_args()
        self._define_logging_level()
        self._gui_or_cli()
        if not self._gui:
            self._define_url()
            self._define_secrets()
            self._export_or_notify()

    def _gui_or_cli(self):
        self._gui = self._args.gui

    def _define_logging_level(self):
        if self._args.log_level:
            # ValueError exception is not handled here as it will be raised and
            # will stop the program - which is what is wanted. It will be
            # logged by logger, see main file.
            level = int(self._args.log_level)

            if level > 3 or level < 1:
                raise ValueError("Debugging level can only be between 1 and 3.")

            if level == 1:
                logging.getLogger(__name__).parent.setLevel(logging.WARNING)
            elif level == 2:
                logging.getLogger(__name__).parent.setLevel(logging.INFO)
            elif level == 3:
                logging.getLogger(__name__).parent.setLevel(logging.DEBUG)

    def _define_url(self):
        self._url = ""
        if self._args.url and self.is_url_valid(self._args.url):
            self._url = self._args.url

    def _define_secrets(self):
        if self._args.account_secrets:
            secrets = tuple(self._args.account_secrets.split(":"))
            if all(secrets) and len(secrets) == 2 and self._url:
                self.set_domain_secrets(secrets, url=self._url)
            else:
                raise ValueError("You need to provide a login, password and url to set secrets.")

    def _export_or_notify(self):
        # if not export, notify
        self._do_export = False
        self._null_notif = self._args.null_notif

        self._delete_url = self._args.delete_url
        if self._delete_url and not self._url:
            raise ValueError("No url to delete specified.")

        self._filename = self._args.filename
        if self._url and self._filename:
            self._do_export = True
