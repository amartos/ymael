# -*- coding: utf-8 -*-

import pypandoc
import os
import tempfile

from .markdown import MDMaker


class PanExporter:

    def __init__(self, filename, rps):
        filename, ext = os.path.splitext(filename)
        if not ext in [".pdf",".odt",".docx"]:
            ext = ".md"

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
        try:
            output = filename+ext
            tmp_file = tempfile.mkstemp(text=True)[1]
            MDMaker(tmp_file, rps, add_before)
            pypandoc.convert_file(tmp_file, self._format, format="markdown",
                    outputfile=output,
                    extra_args=['--pdf-engine', 'xelatex'])
        except AttributeError:
            md_file = filename+".md"
            MDMaker(md_file, rps)
