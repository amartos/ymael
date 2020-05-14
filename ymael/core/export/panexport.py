# -*- coding: utf-8 -*-

import pypandoc
import os
import shutil
import logging
logger = logging.getLogger(__name__)


from .markdown import MDMaker


class PanExporter:

    @staticmethod
    def supported_extensions():
        return [".pdf",".odt",".docx",".md"]

    def __init__(self, filename, rps):
        logger.info("Pandoc version: {}".format(pypandoc.get_pandoc_version()))
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
fontfamily: carlito
fontfamilyoptions: sfdefault
---

"""
        tmp_file = filename
        if ext != ".md":
            tmp_file += ".md"
        MDMaker(tmp_file, rps, add_before)
        if ext != ".md":
            try:
                pypandoc.convert_file(tmp_file, ext.lstrip("."), format="markdown",
                        outputfile=filename,
                        extra_args=['--pdf-engine', 'xelatex'])
                os.remove(tmp_file)
            except OSError:
                logger.warning("Pandoc is not installed.")
            except RuntimeError:
                logger.warning("No latex distribution available.")
            except AttributeError:
                logger.exception("Conversion error.")
            else:
                shutil.move(tmp_file, filename+".md")
                logger.warning("File is located at {}".format(filename+".md"))
