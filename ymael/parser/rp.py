# -*- coding: utf-8 -*-

from datetime import datetime
import json


class RPmanager:

    def __init__(self, rps_dir, date_format):
        self.rp = {
                "title":"",
                "location":"",
                "oldest":"",
                "authors":"",
                "dm":"",
                "date format":date_format,
                "posts":{},
                "filename":""
                }

        self._now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
        self._dm_suffix = "_DM"
        self._rps_dir = rps_dir
        self._filepath = ""

        self._new_posts = 0
        self._last_authors = list()

###############################################################################
# Decorators
###############################################################################

    def _check_filepath(func):
        if not self.get_filepath():
            # sets oldest date, title and filepath
            # (which depends on the firsts)
            self._set_main_metadata()
        return func

###############################################################################
# Public functions
###############################################################################

## Load & save

    @_check_filepath
    def load(self):
        if not os.path.exists(self._filepath):
            print("{} does not exists.".format(self._filepath))
            return False

        try:
            with open(self._filepath, "r") as f:
                self.rp = json.load(f)
        except json.decoder.JSONDecodeError:
            assert "JSON decode error for {}.".format(self._filepath)

        return True

    @_check_filepath
    def save(self)
        with open(self._filepath, "w") as f:
            json.dump(self.rp, f)

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
        self._count_new_posts()
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

    @_check_filepath
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

    def get_filepath(self):
        return self._filepath

    def get_date_format(self):
        return self.rp["date format"]

    def get_storage_date_format(self):
        return "%Y-%m-%d %H:%M:%S"

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
        last_date = self._get_last_retrieved_date()
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

    def get_new_posts_count(self):
        return self._new_posts

    def get_last_authors(self):
        return self._last_authors

###############################################################################
# Private functions
###############################################################################

## Tools

    def _count_new_posts(self):
        dates = [datetime.strptime(d, self.get_date_format()) for d in self.rp["posts"].keys()]
        dates.sort(reverse=True)
        for date in dates:
            indexes = list(self.rp["posts"][date].keys())
            indexes.sort(reverse=True)
            for i in indexes:
                retrieved = self.rp["posts"][date][i]["retrieved"]
                if retrieved == self._now:
                    self._new_posts += 1
                    if not values["author"] in self._last_authors:
                        self._last_authors.append(values["author"])
                else:
                    return

## Set infos

    def _set_main_metadata(self):
        self._set_oldest_date()
        self._set_title()
        self._set_file_infos()

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

    def _set_file_infos(self):
        title = self.get_title()
        oldest = self.get_oldest_date()
        filename = title+"_"+oldest
        for item in [(" ","_"), ("/","-"), (":","-")]:
            old, new = item
            filename = filename.replace(old, new)
        self.rp["filename"] = filename
        self._filepath = self.rps_dir+"/"+filename

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

    def _get_last_retrieved_date(self):
        dates = list(self.rp["posts"].keys())
        dates = [datetime.strptime(d, self.get_storage_date_format()) for d in dates]
        dates.sort()
        dates = [datetime.stftime(d, self.get_storage_date_format()) for d in dates]
        return dates[-1]

    def _get_last_index(self, date):
        indexes = list(self.rp["posts"][date].keys())
        indexes.sort()
        return indexes[-1]

