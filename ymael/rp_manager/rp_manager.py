# -*- coding: utf-8 -*-

from datetime import datetime

from .database import Database

class RPmanager:

    def __init__(self, rps_dir, date_format):
        self.rp = {
                "title":"",
                "location":"",
                "oldest":"",
                "authors":"",
                "dm":"",
                "date format":date_format,
                "posts":{}
                }

        self._dm_suffix = "_DM"
        self._rps_dir = rps_dir

        self._new_posts = 0
        self._last_authors = list()

        self._db = Database(rps_dir, "rps.db")
        self._now = datetime.strftime(datetime.now(), self.get_storage_date_format())
        self._check_tables()

###############################################################################
# Public functions
###############################################################################

## Watch, save & load

    def save(self):
        self._reference_rp()
        self._save_posts()

    def load(self, title):
        if self._db.is_row("rps", [("title", title)]):
            result = self._db.get_row("rps", [("title", title)])
            creation_date, title, location, dms = result

            self.set_metadata(location, title=title, date=creation_date, dm=dms)

            self._db.search_rows("posts", [("rp_title", title)])
            results = self._db.get_results()
            while results != None:
                rp_title, irl_date, ig_date, post_title, name, race, sex, \
                        look, clothes, language, text, retrieved_date = results
                author_infos = (name,race,sex,look,clothes)
                self.create_post(irl_date, ig_date, post_title, author_infos, language, text, date=retrieved_date)
                results = self._db.get_results()
        else:
            return False
        return True

    def close_db(self):
        self._db.close()

## Booleans

    def is_posts_empty(self):
        return not bool(self.rp["posts"])

    def is_post_already_in(self, date, title):
        if date in self.rp["posts"].keys():
            for index in self.rp["posts"][date].keys():
                if self.get_post_title(date, index) == title:
                    return True
        else:
            return None
        return False

    def are_new_posts(self):
        self._get_new_posts_infos()
        return bool(self._new_posts)

## Converters

    def convert_name_dm(self, name):
        return name+self._dm_suffix

    def convert_date(self, date):
        # This raises ValueError if the irl_date is not in the storage date format,
        # and converts it in case
        try:
            d = datetime.strptime(date, self.get_storage_date_format())
            oformat = self.get_date_format()
        except ValueError:
            d = datetime.strptime(date, self.get_date_format())
            oformat = self.get_storage_date_format()
        return datetime.strftime(d, oformat)

## Set infos

    def set_metadata(self, location, title="", date="", dm=""):
        self._set_oldest_date(date)
        self._set_title(title)
        self._set_authors_and_dm(dm)
        self._set_location(location)

    def create_post(self, irl_date, ig_date, title, author_infos, language, text, date=""):
        # This raises ValueError if the irl_date is not in the storage date format,
        # and converts it in case
        try:
            datetime.strptime(irl_date, self.get_storage_date_format())
        except ValueError:
            irl_date = self.convert_date(irl_date)

        if not date:
            date = self._now

        name,race,sex,look,clothes = author_infos
        post = {
                "date in game":ig_date,
                "title":title,
                "author":name,
                "race":race,
                "sex":sex,
                "look":look,
                "clothes":clothes,
                "language":language,
                "text":text,
                "retrieved":date
                }

        already_in = self.is_post_already_in(irl_date, title)
        if not already_in:
            if already_in == None:
                self.rp["posts"][irl_date] = {0:post}
            else:
                n = len(self.rp["posts"][irl_date].keys())
                self.rp["posts"][irl_date][n] = post

## Get infos

    def get_current_date(self):
        return datetime.strptime(self._now, self.get_storage_date_format())

    def get_date_format(self):
        return self.rp["date format"]

    def get_storage_date_format(self):
        return self._db.get_date_format()

    def get_location(self):
        return self.rp["location"]

    def get_oldest_date(self):
        return self.rp["oldest"]

    def get_ig_date(self):
        oldest = self.get_oldest_date()
        return self.rp["posts"][oldest][0]["date in game"]

    def get_title(self):
        if not self.rp["title"]:
            self._set_title()
        return self.rp["title"]

    def get_authors(self):
        return self.rp["authors"]

    def get_dm(self):
        return self.rp["dm"]

    def get_last_retrieved_date(self):
        last_date = self._get_last_date()
        last_index = self._get_last_index(last_date)
        return self.get_post_retrieved_date(last_date, last_index)

    def get_posts(self):
        return self.rp["posts"]

    def get_post_title(self, date, index):
        return self.rp["posts"][date][index]["title"]

    def get_post_ig_date(self, date, index):
        return self.rp["posts"][date][index]["date in game"]

    def get_post_author_infos(self, date, index):
        name = self.rp["posts"][date][index]["author"]
        race = self.rp["posts"][date][index]["race"]
        sex = self.rp["posts"][date][index]["sex"]
        look = self.rp["posts"][date][index]["look"]
        clothes = self.rp["posts"][date][index]["clothes"]
        return name, race, sex, look, clothes

    def get_post_language(self, date, index):
        return self.rp["posts"][date][index]["language"]

    def get_post_text(self, date, index):
        return self.rp["posts"][date][index]["text"]

    def get_post_retrieved_date(self, date, index):
        return self.rp["posts"][date][index]["retrieved"]

###############################################################################
# Private functions
###############################################################################

## Tools

    def _get_new_posts_infos(self):
        new_authors = list()
        conditions = [("rp_title", self.get_title()), ("retrieved_date", self._now)]
        self._db.search_rows("posts", conditions, column_order="irl_date", reverse=True)
        results = self._db.get_results()
        while results != None:
            rp_title, irl_date, ig_date, post_title, name, race, sex, \
                    look, clothes, language, text, retrieved_date = results
            self._new_posts += 1
            new_authors.append(name)
            results = self._db.get_results()

        self._last_authors = sorted(list(set(new_authors)), key=str.casefold)

## Set infos


    def _set_oldest_date(self, date=""):
        if not date:
            dates = sorted([datetime.strptime(d, self.get_storage_date_format()) for d in self.rp["posts"].keys()])
            date = dates[0]
            self.rp["oldest"] = datetime.strftime(date, self.get_storage_date_format())
        else:
            self.rp["oldest"] = date


    def _set_title(self, title=""):
        if not title:
            if not self.get_oldest_date():
                self._set_oldest_date()
            date = self.get_oldest_date()
            title = self.rp["posts"][date][0]["title"]
        self.rp["title"] = title

    def _set_authors_and_dm(self, dm=""):
        authors = self._get_all_authors()
        players = [a for a in authors if not self._dm_suffix in a]
        self.rp["authors"] = ", ".join(players)
        if not dm:
            dm = [a.replace(self._dm_suffix, "") for a in authors if self._dm_suffix in a]
            self.rp["dm"] = ", ".join(dm)
        else:
            self.rp["dm"] = dm

    def _set_location(self, location):
        self.rp["location"] = location

## Get infos

    def _get_all_authors(self):
        authors = list()
        for d,v in self.rp["posts"].items():
            for i,p in v.items():
                authors.append(p["author"])
        authors = sorted(list(set(authors)), key=str.casefold)
        return authors

    def _get_last_date(self):
        dates = list(self.rp["posts"].keys())
        dates = [datetime.strptime(d, self.get_storage_date_format()) for d in dates]
        dates.sort()
        dates = [datetime.strftime(d, self.get_storage_date_format()) for d in dates]
        return dates[-1]

    def _get_last_index(self, date):
        indexes = list(self.rp["posts"][date].keys())
        indexes.sort()
        return indexes[-1]

## Database

    def _check_tables(self):
        self._create_rps_table()
        self._create_posts_table()

    def _create_rps_table(self):
        columns = [
                ("creation_date", "date", "not null"),
                ("title", "text", "not null"),
                ("location", "text", "not null"),
                ("dms", "text")
                ]
        primary_keys = ["creation_date", "title", "location"]
        self._create_manager_tables("rps", columns, primary_keys)

    def _create_posts_table(self):
        columns = [
                ("rp_title", "text", "not null"),
                ("irl_date", "date", "not null"),
                ("ig_date", "date", "not null"),
                ("post_title", "text", "not null"),
                ("author", "text", "not null"),
                ("race", "text", "not null"),
                ("sex", "text", "not null"),
                ("look", "text", "not null"),
                ("clothes", "text", "not null"),
                ("language", "text", "not null"),
                ("post", "text", "not null"),
                ("retrieved_date", "date", "not null")
                ]
        primary_keys = ["rp_title", "post_title", "irl_date", "author"]
        foreign_keys = [("rp_title", "rps", "title")]
        self._create_manager_tables("posts", columns, primary_keys, foreign_keys)

    def _create_manager_tables(self, table_name, columns, primary_keys, foreign_keys=[]):
        if not self._db.is_table(table_name):
            self._db.create_table(table_name, columns, primary_keys, foreign_keys)

    def _reference_rp(self):
        columns = ["creation_date", "title", "location", "dms"]
        creation_date = self.get_oldest_date()
        title = self.get_title()
        location = self.get_location()
        dms = self.get_dm()
        values = [(creation_date, title, location, dms)]
        # we need to replace here in case the DMs string has changed
        self._db.insert_rows("rps", columns, values, replace=True)

    def _save_posts(self):
        columns = [
                "rp_title",
                "irl_date",
                "ig_date",
                "post_title",
                "author", "race", "sex", "look", "clothes",
                "language",
                "post",
                "retrieved_date"
                ]

        values = list()

        rp_title = self.get_title()
        posts = self.get_posts()
        for irl_date in posts.keys():
            for index in posts[irl_date].keys():
                ig_date = self.get_post_ig_date(irl_date, index)
                retrieved_date = self.get_post_retrieved_date(irl_date, index)
                post_title = self.get_post_title(irl_date, index)
                author, race, sex, look, clothes = self.get_post_author_infos(irl_date, index)
                language = self.get_post_language(irl_date, index)
                post = self.get_post_text(irl_date, index)
                values.append((
                        rp_title,
                        irl_date,
                        ig_date,
                        post_title,
                        author, race, sex, look, clothes,
                        language,
                        post,
                        retrieved_date))

        self._db.insert_rows("posts", columns, values)
