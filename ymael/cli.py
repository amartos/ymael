import argparse
import logging
logger = logging.getLogger(__name__)


from .core import Core
from .gui import GraphicInterface


class CommandLine(Core):

    def __init__(self, infos, rps_folder, icon_path, exit_func):
        super().__init__(rps_folder)
        null,self._license_short,self._version = infos

        self._define_args_parser()
        self._parse_args()

        if self._args.version:
            print("Ymael version {}".format(self._version))
        elif self._gui:
            GraphicInterface(infos, rps_folder, icon_path, exit_func, self._minimized)
        else:
            if self._do_export:
                self.export(self._urls, self._filename)
            else:
                self.watch(self._null_notif, self._urls, self._delete_url)
            exit_func()

    def _define_args_parser(self):
        self._args_parser = argparse.ArgumentParser(self,
                description="""
Watch for new posts and extract rp infos from the specified URL or stored URLs
in the database. If URL and FILENAME are given, it exports the given URL's RP
into FILENAME with formatting. If only URL is given, it adds it to the watch
database. If no URL or FILENAME is given, the program will look for new posts
in the watched URLs list and will notify the user if there are some.

Important reminder: the first time you export a RP or set a URL to the watcher
from a given domain, you NEED to set the LOGIN:PASSWORD associated to the
domain by using the -a option. See the -a option's help for details.
""",
        usage="""
to look for new posts (needs login and password set for all watched domains):
ymael [-n] [-l LOG_LEVEL]

to add or remove a url listed in the watched database:
ymael -u URL [-a LOGIN:PASSWORD] [-l LOG_LEVEL]

to export a URL to FILENAME:
ymael -u URL -f FILENAME [-a LOGIN:PASSWORD] [-l LOG_LEVEL]

to launch the graphic interface:
ymael -g [-l LOG_LEVEL]

{}""".format(self._license_short))

        self._args_parser.add_argument(
                "-v", "--version",
                help="show the software version.",
                action="store_true")

        self._args_parser.add_argument(
                "-a", "--account-secrets",
                help="""
Argument is passed as LOGIN:PASSWORDS. Both are stored securely in the system's
keyring. For more details see the python's keyring package help.

If a LOGIN:PASSWORD couple has not been already defined for a given domain,
this option is mandatory the first time a URL from the domain is passed. The
last LOGIN:PASSWORD couple stored will then be used as default for the domain
until this option is re-used to set a new couple.

If you want to change the LOGIN:PASSWORD for a given domain, use this option
while either deleting a URL from the watched database, or setting a URL into
watched database (even one that is already watched, which will be eventually
ignored but will trigger the change), or exporting a RP from this domain.
""")

        self._args_parser.add_argument(
                "-u", "--urls",
                help="""
URLs of each topic to be exported/added in watch list, separated by a space.
They do not need to be the urls of the first page of each topic if there are
multiple pages in them.  This option is mandatory to set login and passwords
via the -a option. Beware that the login:password couple will be used for the
domain of the first URL given only, thus all URLs should be from the same
domain.
""")

        self._args_parser.add_argument(
                "-f", "--filename",
                help="""
Export the RP topic to the filename in one of the supported formats: pdf, odt,
docx, or markdown (md).
""")

        self._args_parser.add_argument(
                "-n", "--null_notif",
                help="Notify even if there are no new posts.",
                action="store_true")

        self._args_parser.add_argument(
                "-d", "--delete_url",
                help="Remove the URL given with -u from watched URLs.",
                action="store_true")

        self._args_parser.add_argument(
                "-l", "--log_level",
                help="""
Set log level. Values can either be 1 (WARNING), 2 (INFO) or 3 (DEBUG).
""")

        self._args_parser.add_argument(
                "-g", "--gui",
                help="""
Launch graphic user interface. Except for logging level and start minimized,
all other options are ignored.
""",
                action="store_true")

        self._args_parser.add_argument(
                "-m", "--minimized",
                help="Do not open window, only start in icon tray.",
                action="store_true")

    def _parse_args(self):
        self._args = self._args_parser.parse_args()
        self._define_logging_level()
        self._gui_or_cli()
        if not self._gui:
            self._define_urls()
            self._define_secrets()
            self._export_or_notify()
        else:
            self._start_minimized()

    def _gui_or_cli(self):
        self._gui = self._args.gui

    def _start_minimized(self):
        self._minimized = self._args.minimized

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

    def _define_urls(self):
        self._urls = []
        if self._args.urls:
            urls = self._args.urls.split(" ")
            self._urls = [url for url in urls if self.is_url_valid(url)]

    # TODO: define secrets for each URL even if different
    def _define_secrets(self):
        if self._args.account_secrets:
            secrets = tuple(self._args.account_secrets.split(":"))
            if all(secrets) and len(secrets) == 2 and self._urls:
                self.set_domain_secrets(secrets, url=self._urls[0])
            else:
                raise ValueError("You need to provide a login, password and url to set secrets.")

    def _export_or_notify(self):
        # if not export, notify
        self._do_export = False
        self._null_notif = self._args.null_notif

        self._delete_url = self._args.delete_url
        if self._delete_url and not self._urls:
            raise ValueError("No url to delete specified.")

        self._filename = self._args.filename
        if self._urls and self._filename:
            self._do_export = True
