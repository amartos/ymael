# -*- coding: utf-8 -*-

from .edenya_v3 import EdenyaV3
from .edenya_v4 import EdenyaV4


class EdenyaParser(EdenyaV3, EdenyaV4):

    def __new__(cls, url, secrets, rps_dir):
        if "v4.edenya.net" in url:
            return EdenyaV4(url, secrets, rps_dir)
        else:
            return EdenyaV3(url, secrets, rps_dir)
