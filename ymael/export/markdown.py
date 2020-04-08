# -*- coding: utf-8 -*-

import re
import textwrap
from datetime import datetime


class MDMaker:

    def __init__(self, filename, rps, add_before=""):
        self._filename = filename
        self._rps = rps
        self._date_format = self._rps["date format"]
        self._header = ""
        self._add_before = add_before
        self._main = """# %s

Par %s

Le %s (%s)

__%s__

"""
        self._template = """
----

## %s

> Titre : %s\\
> %s %s, Apparence %s, Habillement %s\\
> EJ le %s --- HJ le %s\\
> Langue parlée : %s

%s"""
        self._body = ""

        self._authors = list()
        self._fill_body()
        self._fill_header()
        self._write_to_file()

    def _fill_body(self):
        dates = [datetime.strptime(x, self._date_format) \
                for x in self._rps["posts"].keys()]
        dates.sort()
        while dates:
            date = dates.pop(0)
            date = date.strftime(self._date_format)
            title = self._rps["posts"][date]["title"]
            title = self._set_markups(title)
            author, race, sex, look, clothes = self._rps["posts"][date]["author"]
            self._authors.append(author)
            date_in_game = self._rps["posts"][date]["date in game"]
            language = self._rps["posts"][date]["language"]
            text = self._rps["posts"][date]["text"]
            text = self._set_markups(text)
            post = self._template % (
                    author,
                    title,
                    race, sex, look, clothes,
                    date_in_game, date,
                    language,
                    text
                )
            self._body += post

    def _set_markups(self, text):
        replacements = [
                ("0b00df5945BOLD (.*?) BOLD72800245ef", r"__\1__"),
                ("0b00df5945ITAL (.*?) ITAL72800245ef", r"*\1*"),
                ("0b00df5945CODE (.*?) CODE72800245ef", r"`\1`"),
                ("0b00df5945BLOC\n(.*?)\nBLOC72800245ef", r"```\1```"),
                ("^- ", "--- "),
            ]
        # save all * present in text
        text = text.replace("*", "0b00df5945ASTE72800245ef")
        for couple in replacements:
            old, new = couple
            text = re.sub(old, new, text, flags=re.S | re.M)

        # Add marks at each paragraph end
        for mark in ["*", "__"]:
            splitted = text.split(mark)
            for k,i in enumerate(splitted):
                odd = bool(k % 2)
                if i and len(i.split("\n")) > 1 and odd:
                    splitted[k] = i.replace("\n\n","*\n\n*")
            text = mark.join(splitted)

        # restore * in text
        text = text.replace("0b00df5945ASTE72800245ef", "\*")

        return text

    def _fill_header(self):
        title = self._rps["title"]
        title = self._set_markups(title)
        date_irl = self._rps["oldest"]
        date_in_game = self._rps["posts"][date_irl]["date in game"]
        unique_authors = sorted(list(set(self._authors)))
        authors = ", ".join(unique_authors)
        location = "__\n\n__".join(self._rps["location"])
        self._header = self._main % (
                title,
                authors,
                date_in_game,
                date_irl,
                location
            )

    def _write_to_file(self):
        final = self._hard_wrap(self._add_before+self._header+self._body)
        with open(self._filename, "w") as f:
            f.write(final)

    def _hard_wrap(self, text):
        splitted = text.split("\n")
        for index,par in enumerate(splitted):
            wrapped = textwrap.wrap(par, width=80)
            splitted[index] = "\n".join(wrapped)
        text = "\n".join(splitted)
        return text
