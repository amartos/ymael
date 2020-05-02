# -*- coding: utf-8 -*-

import requests
import bs4
import re
import logging
logger = logging.getLogger(__name__)


from ..rp_manager import RPmanager


class EdenyaV3Parser:

    def __init__(self, urls, secrets, rps_dir):
        self.treat_url(urls[0])
        self._login(secrets)
        self.rps = {}

        for url in urls:
            self._rp = RPmanager(rps_dir, date_format="%d/%m/%Y %H:%M", url=url)

            self._parse_html(url)
            if not self._check_if_rp():
                raise ValueError("returned page is not a RP: %s", url)
            self._parse_rp_urls()

            self._parse_rps(page=1)
            if not self._rp.is_posts_empty():
                title = self._rp.get_title()
                is_prev_rps = self._rp.load(title, url)
                if not is_prev_rps:
                    location = self._parse_location()
                else:
                    location = self._rp.get_location()
            self._rp.set_metadata(location)

            self._parse_rps()
            self._rp.save()
            self.rps[url] = self._rp

    def treat_url(self, url):
        domain_url = url.split("_vahal/index.php")[0]
        self._base_url = domain_url+"_vahal/"
        self._post_login = domain_url+"dologin.php"

    def _login(self, secrets):
        with requests.Session() as self._session:
            load = {"pseudo":secrets[0],"password":secrets[1]}
            self._post = self._session.post(self._post_login, data=load)
            if not self._post.ok:
                raise ValueError("Logging to Edenya v3 failed.")

    def _parse_html(self, url="", raw_html=""):
        if not raw_html and url:
            raw_html = self._session.get(url).text
        self._parsed = bs4.BeautifulSoup(raw_html,features="lxml")

    def _parse_rp_urls(self):
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
        return "Voir une discussion" in self._parse_page_title()

    def _parse_page_title(self):
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

    def _parse_rps(self, page=0):
        if page and page <= len(self._all_links):
            self._parse_page(self._all_links[0])
        else:
            stop = False
            while not stop and self._all_links:
                url = self._all_links.pop()
                stop = self._parse_page(url) # True means a known rp is encountered

    # This function returns True if it reached a rp that is already known.
    # Otherwise it returns False. The rp is not stored in the self._rp
    # structure.
    def _parse_page(self, url):
        self._parse_html(url)
        test = self._parsed.body.find_all('table', attrs={'class':'cadre2'})
        while test:
            item = test.pop()
            title = self._parse_post_title(item)
            if title:
                ig_date, irl_date = self._parse_post_date(item)
                if self._rp.is_post_already_in(irl_date, title):
                    return True
                weather = "?"
                self._rp.create_post(
                        irl_date,
                        ig_date,
                        weather,
                        title,
                        self._parse_post_author_infos(item),
                        self._parse_post_language(item),
                        self._parse_post_text(item)
                        )
        return False

    def _parse_post_title(self, item):
        title = item.find_all("td", attrs={"align":"center"})
        if not title:
            return None
        else:
            title = title[0].text
            title = self._prettify(title)
            return title

    def _parse_post_author_infos(self, item):
        name_raw = [x.text for x in item.find_all("a",attrs={"href":"javascript:;"}) if x]
        infos = item.find("img", attrs={"src":"images/forum/infos.gif"}).get("onmouseover")
        name, race, sex, look, clothes = ("Inconnu", "?", "?", "?", "?")
        if name_raw:
            name = name_raw[0]
            # ID the DMs
            # we don't use "Événement" here as some DMs like to mess up with the
            # author's name. The parentheses are the only common option.
            if "(" in name:
                real_name = name.split("(")[-1].replace(")","")
                name = self._rp.convert_name_dm(real_name)
        if not "Aucune information" in infos:
            part = re.split("<\/{0,}b>|<br>",infos)
            part = [i for i in part if i and not "ShowHelpPerso" in i and not ":" in i]
            race, sex, look, clothes = part[0:4]

        return (name,race,sex,look,clothes)

    def _parse_post_date(self, item):
        date = item.find_all("em", attrs={"class":"tooltips"})
        for part in date:
            in_game = part.text[:14]
            irl = part.text[14:]
        return (in_game, irl)

    def _parse_post_language(self, item):
        language = [s for s in item.find_all("div", attrs={"align":"center"})]
        language = language[0].text.split(" ")[-1]
        return language

    def _parse_post_text(self, item):
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

    def _parse_location(self):
        full_location = list()
        while self._check_if_back_button_present():
            location = self._parse_page_title()
            location = self._prettify(location, newlines=False)
            if not location == "Voir une discussion" \
                    and not location == "Discuter":
                full_location.append(location)
            self._post_back_button()
            raw_html = self._post.content
            self._parse_html(raw_html=raw_html)
        full_location.reverse()
        full_location = " - ".join(full_location)
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
