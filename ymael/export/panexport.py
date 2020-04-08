# -*- coding: utf-8 -*-

import pypandoc
import os
import tempfile

from .markdown import MDMaker


class PanExporter:

    @classmethod
    def pdf(cls, *args, **kwargs):
        cls._format = "pdf"
        return cls(*args, **kwargs)

    @classmethod
    def odt(cls, *args, **kwargs):
        cls._format = "odt"
        return cls(*args, **kwargs)

    @classmethod
    def docx(cls, *args, **kwargs):
        cls._format = "docx"
        return cls(*args, **kwargs)

    @classmethod
    def md(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    def __init__(self, filename, rps):
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
            output = filename+"."+self._format
            tmp_file = tempfile.mkstemp(text=True)[1]
            MDMaker(tmp_file, rps, add_before)
            pypandoc.convert_file(tmp_file, self._format, format="markdown",
                    outputfile=output,
                    extra_args=['--pdf-engine', 'xelatex'])
        except AttributeError:
            md_file = filename+".md"
            MDMaker(md_file, rps)
