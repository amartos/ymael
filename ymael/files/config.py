# -*- coding: utf-8 -*-

import json
import os


class Config:

    @classmethod
    def load_watch_list(cls, watch_list, charname_file):
        try:
            with open(watch_list, "r") as f:
                cls.watch_list = json.load(f)
        except json.decoder.JSONDecodeError:
            cls.watch_list = dict()

        with open(charname_file, "r") as f:
            cls.charname = f.read().strip()

        return cls(watch_list)

    @classmethod
    def load_rp(cls, rp_file):
        if not os.path.exists(rp_file):
            open(rp_file,'w').close()
        try:
            with open(rp_file, "r") as f:
                cls.rp = json.load(f)
        except json.decoder.JSONDecodeError:
            cls.rp = dict()

        return cls(rp_file)

    def save(self, item):
        with open(self._filename, 'w') as f:
            json.dump(item, f, indent=4)

    def __init__(self, filename):
        self._filename = filename
