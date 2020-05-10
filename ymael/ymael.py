# -*- coding: utf-8 -*-

import logging
import os, sys, platform
from datetime import datetime

from .core import Core
from .interface import CommandLine,GraphicInterface
from .notification import Notifier


class Ymael:

    def __init__(self):
        self.system = platform.system()
        self._system_local_path = self._get_system_local_path()
        self._assets_path,middle = self._get_assets_path()

        self.now = datetime.strftime(datetime.now(), "%Y%m%d-%H%M%S")

        self.VERSION="smart_goblin"
        self.LICENSE, self.LICENSE_SHORT = self._get_license()
        self.icon_path = os.path.join(self._assets_path, middle, "ymael.png")

        self.data_path = os.path.join(self._system_local_path,"ymael")
        self.db_dir_path = os.path.join(self.data_path,"rps")
        self.logs_dir_path = os.path.join(self.data_path,"logs")
        for folder in [self.db_dir_path, self.logs_dir_path]:
            if not os.path.exists(folder):
                os.mkdir(folder)

        self.logger = self._set_up_logging()
        self.notifier = Notifier(self.system, "Ymael", self.icon_path)
        self.core = Core(self.db_dir_path, self.notifier)

        infos = (self.LICENSE,self.LICENSE_SHORT,self.VERSION)
        try:
            self.cli = CommandLine(infos, self.core)
            gui, minimized = self.cli.is_gui()
            if gui:
                del self.cli
                self.gui = GraphicInterface(infos, self.core, self.icon_path, self.clean_logs, minimized)
            else:
                self.cli.run()
        except Exception:
            self._fatal_error()

    def _get_assets_path(self):
        if getattr(sys, 'frozen', False):
            path = sys._MEIPASS
            middle = ""
        else:
            current = os.path.dirname(os.path.abspath(__file__))
            path = os.path.dirname(current)
            middle = os.path.join("assets", "icons")
        return path,middle

    def _get_system_local_path(self):
        if self.system == "Windows":
            local = os.getenv('%LOCALAPPDATA%')
        elif self.system == "Linux":
            local = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        else:
            raise RuntimeError("OS not supported. Please report to gitea.com/amartos/ymael/issues to ask for support.")
        return local

    def _get_license(self):
        LICENSE_SHORT="""
Ymael version {} Copyright (C) 2020 Alexandre Martos
Ymael's icon Copyright (C) 2020 Xen

This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
are welcome to redistribute it under certain conditions. For details see the
LICENSE file with the -w/--license command line option, or via the "help>about"
menu in the graphic interface, or the file available at:

https://gitea.com/amartos/ymael
""".format(self.VERSION)

        license_file = os.path.join(self._assets_path,"LICENSE")
        with open(license_file, "r") as f:
            LICENSE=f.read()
        return LICENSE, LICENSE_SHORT

    def _set_up_logging(self):
        self.log_file = os.path.join(self.data_path,"logs", self.now)
        str_format = "[%(asctime)s] [{}] %(name)s (%(levelname)s): %(message)s".format(self.VERSION)
        logging.basicConfig(filename=self.log_file, level=logging.WARNING, format=str_format)
        logger = logging.getLogger(__name__)
        return logger

    def clean_logs(self):
        # remove empty log file
        logging.shutdown()
        if os.stat(self.log_file).st_size == 0:
            os.remove(self.log_file)

    def _fatal_error(self):
            self.logger.exception("A fatal error occurred.")
            title = "Une erreur fatale s'est produite."
            message = "Plus de détails dans le log: {}".format(self.log_file)
            try:
                self.cli.run
                print(title+"\n"+message)
            except (NameError,AttributeError):
                self.notifier.send(title,message)
            sys.exit(1)
