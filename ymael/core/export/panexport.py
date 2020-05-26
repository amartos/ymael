# -*- coding: utf-8 -*-

import subprocess
import os
import shutil
import logging
logger = logging.getLogger(__name__)


from .markdown import MDMaker
from .noconsole_subprocess import subprocess_args


class PanExporter:

    @staticmethod
    def supported_extensions():
        return [".pdf",".odt",".docx",".md"]

    def __init__(self):
        self._subprocess_args = subprocess_args(False)
        pandoc_version, xelatex_version = self.check_install()
        if pandoc_version and xelatex_version:
            logger.info("Pandoc version: {}".format(pandoc_version))
            logger.info("Xelatex version: {}".format(xelatex_version))
            self._ready = True
        else:
            logger.info("Export softwares not available.")
            self._ready = False

        self._add_before = """---
documentclass: article
margin-left: 2.5cm
margin-right: 2.5cm
margin-top: 2.5cm
margin-bottom: 2.5cm
lang: fr
mainfont: FreeSans
---

"""

    def is_ready(self):
        return self._ready

    def convert(self, filename, rps):
        filename, ext = os.path.splitext(filename)
        if not ext in self.supported_extensions():
            logger.warning("Output format %s not supported. Switching to .md", ext)
            ext = ".md"

        filename = filename+ext

        tmp_file = filename
        if ext != ".md":
            tmp_file += ".md"
        MDMaker(tmp_file, rps, self._add_before)
        logger.debug("File is located at {}".format(tmp_file))
        if self._ready and ext != ".md":
            self.convert_file(tmp_file, filename)

    def check_install(self):
        try:
            pandoc_version = subprocess.check_output(
                    ["pandoc", "--version"],
                    **self._subprocess_args
                    )
            pandoc_version = pandoc_version.decode("utf-8").split()[1]
            xelatex_version = subprocess.check_output(
                    ["xelatex", "--version"],
                    **self._subprocess_args
                    )
            xelatex_version = " ".join(xelatex_version.decode("utf-8").split()[1:5])
            return pandoc_version, xelatex_version
        except FileNotFoundError:
            return None,None

    def convert_file(self, input_file, output_file):
        command = [
                "pandoc",
                "-f","markdown+smart",
                "-o",output_file,
                "--pdf-engine", "xelatex",
                "--verbose",
                input_file
                ]
        try:
            out = subprocess.check_output(
                    command,
                    **self._subprocess_args
                    )
            out = out.decode("utf-8")
            logger.debug(out)
            os.remove(input_file)
            logger.info("Conversion successful.")
        except subprocess.CalledProcessError:
            logger.exception("Conversion error.")
