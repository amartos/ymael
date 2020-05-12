# -*- coding: utf-8 -*-

import re
import textwrap
import logging
logger = logging.getLogger(__name__)

from datetime import datetime


class MDMaker:

    def __init__(self, filename, rp, add_before=""):
        self._filename = filename
        self._rp = rp
        self._header = ""
        self._add_before = add_before
        self._main = """# %s

Par %s

Le %s (%s)

%s

__%s__

"""
        self._template = """
----

## %s

> Titre : %s\\
> Race: %s, Sexe: %s, Apparence: %s, Habillement: %s\\
> EJ le %s --- HJ le %s\\
> Météo: %s\\
> Langue parlée : %s

%s"""
        self._body = ""

        self._fill_body()
        self._fill_header()
        self._write_to_file()

    def _fill_body(self):
        posts = self._rp.get_posts()
        dates = [datetime.strptime(d, self._rp.get_storage_date_format()) for d in posts.keys()]
        dates.sort()
        for date in dates:
            irl_date = datetime.strftime(date, self._rp.get_date_format())
            date = datetime.strftime(date, self._rp.get_storage_date_format())
            post_keys = sorted(list(posts[date].keys()))
            for index in post_keys:
                title = self._set_markups(self._rp.get_post_title(date, index))
                author, race, sex, look, clothes = self._rp.get_post_author_infos(date, index)
                ig_date = self._rp.get_post_ig_date(date, index)
                weather = self._rp.get_post_weather(date, index)
                language = self._rp.get_post_language(date, index)
                text = self._set_markups(self._rp.get_post_text(date, index))
                post = self._template % (
                        author,
                        title,
                        race, sex, look, clothes,
                        ig_date, irl_date,
                        weather,
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
                ("\s*:", " :"),
                ("\s*;", " ;"),
                ("\s*!", " !"),
                ("\s*\?", " ?"),
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
        title = self._set_markups(self._rp.get_title())
        irl_date = self._rp.convert_date(self._rp.get_oldest_date())
        ig_date = self._rp.get_ig_date()
        weather = self._rp.get_weather()
        authors = self._rp.get_authors()
        dm = self._rp.get_dm()
        if dm:
            authors = authors + " & comme MJ : {}".format(dm)
        location = self._rp.get_location()
        self._header = self._main % (
                title,
                authors,
                ig_date,
                irl_date,
                weather,
                location
            )

    def _write_to_file(self):
        final = self._hard_wrap(self._add_before+self._header+self._body)
        # utf-8 precision is needed for windows
        with open(self._filename, "w", encoding="utf-8") as f:
            f.write(final)

    def _hard_wrap(self, text):
        splitted = text.split("\n")
        for index,par in enumerate(splitted):
            wrapped = textwrap.wrap(par, width=90)
            splitted[index] = "\n".join(wrapped)
        text = "\n".join(splitted)
        return text
