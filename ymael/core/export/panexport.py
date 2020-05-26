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

    def __init__(self, filename, rps):
        self._subprocess_args = subprocess_args(False)
        version = self.get_pandoc_version()
        logger.info("Pandoc version: {}".format(version))

        filename, ext = os.path.splitext(filename)
        if not ext in self.supported_extensions():
            logger.warning("Output format %s not supported. Switching to .md", ext)
            ext = ".md"

        filename = filename+ext

        add_before = """---
documentclass: article
margin-left: 2.5cm
margin-right: 2.5cm
margin-top: 2.5cm
margin-bottom: 2.5cm
lang: fr
mainfont: FreeSans
---

"""
        tmp_file = filename
        if ext != ".md":
            tmp_file += ".md"
        MDMaker(tmp_file, rps, add_before)
        logger.debug("File is located at {}".format(tmp_file))
        if version and ext != ".md":
            self.convert_file(tmp_file, filename)

    def get_pandoc_version(self):
        try:
            version = subprocess.check_output(
                    ["pandoc", "--version"],
                    **self._subprocess_args
                    )
            version = version.decode("utf-8").split()[1]
            return version
        except FileNotFoundError:
            logger.warning("Pandoc is not installed.")
            return None

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
