# -*- coding: utf-8 -*-

import requests
import bs4
import re
from datetime import datetime, timedelta


class EdenyaParser:

    @staticmethod
    def treat_url(url):
        base_url = url.split("_vahal/index.php")[0]
        base_posts_url = base_url+"_vahal/"
        post_login = base_url+"dologin.php"
        return base_url, base_posts_url, post_login

    @classmethod
    def extract_rps(cls, url, secrets, rps_config, rps_dir):
        cls._rps_config = rps_config
        cls._rps_dir = rps_dir

        base_url, base_posts_url, post_login = cls.treat_url(url)

        with requests.Session() as session:
            post = session.post(post_login, data=secrets)

        return cls(base_posts_url, post, session, url)

    def __init__(self, base_url, post, session, url):
        self._base_url = base_url
        self._post = post
        self._session = session
        self._user_url = url
        self.date_format = "%d/%m/%Y %H:%M"

        self.rps = dict()
        self.rps["posts"] = dict()

        self._get_parsed(self._user_url)
        self._get_other_links()

        if len(self._all_links) > 1:
            self._all_links = list(set(self._all_links))
        for url in self._all_links:
            self._get_parsed(url)
            assert self._check_if_rp(), "This is not a rp topic"
            self._get_rps()

        if bool(self.rps["posts"]):
            self.rps["date format"] = self.date_format
            self.rps["oldest"], self.rps["title"] = self._get_rp_title()

            self._merge()
            if not "location" in self.rps:
                self.rps["location"] = self._get_location()

            self._rps_config.save(self.rps)

    def _get_parsed(self, url="", raw_html=""):
        if not raw_html and url:
            raw_html = self._session.get(url).text
        self._parsed = bs4.BeautifulSoup(raw_html,features="lxml")

    def _get_other_links(self):
        pages = [" |{}| ".format(x) for x in range(1,101)]
        self._all_links = list()
        while pages:
            url = None
            page = pages.pop(0)
            test = self._parsed.body.find_all('a', text=page)
            if test:
                for item in test:
                    url = self._base_url+item.get("href")
                self._all_links.append(url)
            elif not test:
                break

    def _check_if_rp(self):
        return "Voir une discussion" in self._get_page_title()

    def _get_page_title(self):
        title = self._parsed.body.find_all("td", attrs={"class":"titre"})
        # During location crawling, one page has two titles
        # in that page the second is more interesting
        try:
            title = title[1]
        except:
            try:
                title = title[0]
            except IndexError:
                # exception for guilds page
                title = self._parsed.body.find("p", attrs={"class":"titre"})
        return title.text

    def _get_rps(self):
        post = 0
        test = self._parsed.body.find_all('table', attrs={'class':'cadre2'})
        while test:
            item = test.pop()
            title = self._get_post_title(item)
            if title:
                date_in_game, date_irl = self._get_date(item)
                if date_irl in self.rps["posts"].keys():
                    if not self.rps["posts"][date_irl]["title"] == title:
                        # this is done in case two posts were done within one
                        # minute. The Edenya website does not store seconds in
                        # posts datas, thus two consecutive posts could result
                        # as only one (the other is deleted)
                        temp = datetime.strptime(date_irl, self.date_format)
                        temp = temp + timedelta(minutes=1)
                        date_irl = temp.strftime(self.date_format)
                    else:
                        self._all_links = None
                        break

                self.rps["posts"][date_irl] = dict()
                self.rps["posts"][date_irl]["date in game"] = date_in_game
                self.rps["posts"][date_irl]["title"] = title
                self.rps["posts"][date_irl]["author"] = self._get_author_infos(item)
                self.rps["posts"][date_irl]["language"] = self._get_language(item)
                self.rps["posts"][date_irl]["text"] = self._get_text(item)
                post += 1

    def _get_post_title(self, item):
        title = item.find_all("td", attrs={"align":"center"})
        if not title:
            return None
        else:
            title = title[0].text
            title = self._prettify(title)
            return title

    def _get_author_infos(self, item):
        name_raw = [x.text for x in item.find_all("a",attrs={"href":"javascript:;"}) if x]
        infos = item.find("img", attrs={"src":"images/forum/infos.gif"}).get("onmouseover")
        name, race, sex, look, clothes = ("Inconnu", "?", "?", "?", "?")
        if name_raw:
            name = name_raw[0]
        if not "Aucune information" in infos:
            part = re.split("<\/{0,}b>|<br>",infos)
            part = [i for i in part if i and not "ShowHelpPerso" in i and not ":" in i]
            race, sex, look, clothes = part[0:4]

        return (name,race,sex,look,clothes)

    def _get_date(self, item):
        date = item.find_all("em", attrs={"class":"tooltips"})
        for part in date:
            in_game = part.text[:14]
            irl = part.text[14:]
        return (in_game, irl)

    def _get_language(self, item):
        language = [s for s in item.find_all("div", attrs={"align":"center"})]
        language = language[0].text.split(" ")[-1]
        return language

    def _get_text(self, item):
        text = str(item.find_all("td",attrs={"class":"naration"})[0])
        text = self._prettify(text)
        return text

    def _prettify(self, text, newlines=True):
        replacements = [
                ("<br/>","\n"),
                ("<br />","\n"),
                ("</td>",""),
                ("\t",""),
                ("\r",""),
                ("\n\n\n","\n"),
                ("[ ]{1,}\n","\n"),
                ("\n[ ]{1,}","\n"),
                ("(\s*)</span>",r"</span>\1"),
                (" langue=\"[0-9]\"",""),
                ("<td class=\"naration\" colspan=\"3\">",""),
                ("<span class=\"dialogue\">(.*?)</span>",r"\1"),
                ("<span class=\"cri\">\s*(\S.*?\S)\s*</span>",       r"0b00df5945BOLD \1 BOLD72800245ef"),
                ("<span class=\"narration\">\s*(\S.*?\S)\s*</span>", r"0b00df5945ITAL \1 ITAL72800245ef"),
                ("<span class=\"hj\">\s*(\S.*?\S)\s*</span>",        r"0b00df5945CODE \1 CODE72800245ef"),
                ("<span class=\"ecriture\">\s*(\S.*?\S)\s*</span>",  r"0b00df5945BLOC\n\1\nBLOC72800245ef"),
                ("&lt;","<"),
                ]
        if not newlines:
            replacements += [
                    ("\n",""),
                    (" {1,}$",""),
                ]
        for couple in replacements:
            old, new = couple
            text = re.sub(old, new, text, flags=re.S)

        return text

    def _get_location(self):
        full_location = list()
        while self._check_if_back_button_present():
            location = self._get_page_title()
            location = self._prettify(location, newlines=False)
            if not location == "Voir une discussion" \
                    and not location == "Discuter":
                full_location.append(location)
            self._post_back_button()
            raw_html = self._post.content
            self._get_parsed(raw_html=raw_html)
        full_location.reverse()
        return full_location

    def _check_if_back_button_present(self):
        back = bool(self._parsed.body.find("input", attrs={"value":"Revenir"}))
        out = bool(self._parsed.body.find("input", attrs={"value":"Sortir"}))
        return bool(sum([back, out]))

    def _post_back_button(self):
        form = self._parsed.body.find("form", attrs={"name":"form3"})
        if not form:
            form = self._parsed.body.find("form")
        data = dict()

        location_value = form.find("input", attrs={"name":"loca"}).get("value")
        location_name = form.find("input", attrs={"name":"loca"}).get("name")
        data[location_name] = location_value

        try:
            sector_value = form.find("input", attrs={"name":"secteur"}).get("value")
            sector_name = form.find("input", attrs={"name":"secteur"}).get("name")
            data[sector_name] = sector_value
        except:
            pass

        try:
            id_value = form.find("input", attrs={"name":"id_secteur"}).get("value")
            id_name = form.find("input", attrs={"name":"id_secteur"}).get("name")
            data[id_name] = id_value
        except:
            try:
                id_value = form.find("input", attrs={"name":"id"}).get("value")
                id_name = form.find("input", attrs={"name":"id"}).get("name")
                data[id_name] = id_value
            except:
                pass

        try:
            room_value = form.find("input", attrs={"name":"piece"}).get("value")
            room_name = form.find("input", attrs={"name":"piece"}).get("name")
            data[room_name] = room_value
        except:
            pass

        self._post = self._session.post(self._base_url+"index.php", data=data)

    def _get_rp_title(self):
        dates = [datetime.strptime(x, self.date_format) \
                for x in self.rps["posts"].keys()]
        dates.sort()
        oldest = dates[0].strftime(self.date_format)
        title = self.rps["posts"][oldest]["title"]
        return (oldest, title)

    def _merge(self):
        title = self.rps["title"]
        oldest = self.rps["oldest"]
        filename = title+"_"+oldest
        for item in [(" ","_"), ("/","-"), (":","-")]:
            old, new = item
            filename = filename.replace(old, new)
        path = self._rps_dir+filename

        self._rps_config = self._rps_config.load_rp(path)

        old_rps = self._rps_config.rp

        try :
            self.rps["posts"] = {**self.rps["posts"], **old_rps["posts"]}
        except KeyError:
            pass
