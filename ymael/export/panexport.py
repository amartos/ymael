# -*- coding: utf-8 -*-

import pypandoc
import os
import tempfile
import shutil
import logging
logger = logging.getLogger(__name__)


from .markdown import MDMaker


class PanExporter:

    def __init__(self, filename, rps):
        filename, ext = os.path.splitext(filename)
        if not ext in [".pdf",".odt",".docx",".md"]:
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
        tmp_file = tempfile.mkstemp(text=True)[1]
        MDMaker(tmp_file, rps, add_before)
        try:
            pypandoc.convert_file(tmp_file, self._format, format="markdown",
                    outputfile=filename,
                    extra_args=['--pdf-engine', 'xelatex'])
        except AttributeError:
            shutil.move(tmp_file, filename+".md")
            raise
