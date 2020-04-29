# -*- coding: utf-8 -*-

import requests
import bs4
import re
import json
import atexit
import fake_useragent
import logging
logger = logging.getLogger(__name__)


from ..rp_manager import RPmanager


class EdenyaV4Parser:

    def __init__(self, urls, secrets, rps_dir):
        self._define_urls()
        self._login(secrets)
        self.rps = {}

        for url in urls:
            self._url = url
            self._parse_html(url)
            # TODO: this is not enough stringeant
            if not "Posté le :" in self._parsed.body.text:
                raise ValueError("Returned page is not a RP.")

            self._rp = RPmanager(rps_dir, "%Y-%m-%d %H:%M:%S")

            self._parse_rp()
            if not self._already_in:
                location = self._parse_location()
                self._rp.set_metadata(location)

            self._rp.save()
            self.rps[url] = self._rp

        self._session.close()

    def _define_urls(self):
        self._domain = "v4.edenya.net"
        domain_url = "https://"+self._domain+"/"
        self._base_url = domain_url+"_game/vahal/lieux/"
        self._login_url = domain_url+"accueil/"

    def _login(self, secrets):
        load = {"pseudo":secrets[0],"password":secrets[1],"action":"login","remember":"true"}
        ua = fake_useragent.UserAgent()
        header = {
            "Host":"v4.edenya.net",
            "User-Agent":ua.random,
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language":"fr-FR,en;q=0.7,en-US;q=0.3",
            "Accept-Encoding":"gzip, deflate, br",
            "Referer":"https://v4.edenya.net/accueil/",
            "DNT":"1",
            "Connection":"keep-alive",
            "Upgrade-Insecure-Requests":"1",
            "TE":"Trailers"
        }
        supp_header = {
            "Content-Type":"application/x-www-form-urlencoded",
            "Content-Length":"65",
            "Origin":"https://v4.edenya.net",
        }

        self._session = requests.Session()
        atexit.register(self._session.close)
        self._response = self._session.post(self._login_url, data=load, verify=True, headers={**header,**supp_header})
        if not self._response.ok:
            raise ValueError("Could not connect to Edenya v4.")
        self._session.get("https://v4.edenya.net/accueil/", headers=header)
        self._session.get("https://v4.edenya.net/jouer/", headers=header)
        self._session.get("https://v4.edenya.net/_game/vahal/accueil/", headers=header)

    def _parse_html(self, url):
        raw_html = self._session.get(url).text
        self._parsed = bs4.BeautifulSoup(raw_html,features="lxml")

    def _parse_rp(self, page=0):
        posts = self._parsed.body.find_all('div', attrs={'class':'forum-message box'})
        rp_title = self._parse_post_title(posts[0])
        ig_date = self._parse_ig_date()
        weather = self._parse_weather()
        self._already_in = self._rp.load(rp_title)
        for index,item in enumerate(posts):
            self._rp.create_post(
                    self._parse_post_date(item),
                    ig_date,
                    weather,
                    self._parse_post_title(item),
                    self._parse_post_author_infos(item),
                    self._parse_post_language(item),
                    self._parse_post_text(item)
                    )

    def _parse_post_title(self, item):
        title = item.h4.text.strip()
        return self._prettify(title)

    def _parse_ig_date(self):
        date_box = self._get_context_box()
        date = [i for i in date_box.text.split("\n") if "La date" in i][0]
        ig_date = date.split(" : ")[1]
        return ig_date

    def _parse_weather(self):
        weather_box = self._get_context_box()
        weather_box = weather_box.find("div", id="cadran")
        weather_box = str(weather_box).split("</p>")[1].replace("</div>", "").replace("\n", "")
        weather_split = [i for i in weather_box.split("<br/>") if i and "strong" in i]
        weather = []
        for i in weather_split:
            w = i.split(" : </strong>")
            wtype = w[0].replace("<strong>", "")
            weather.append(wtype+" : "+w[1])

        weather_str = ", ".join(weather)
        return weather_str

    def _get_context_box(self):
        for i in self._parsed.body.find_all("div", {"class":"darkbox"}):
            if "La date" in i.text:
                date_box = i
                break
        return date_box

    def _parse_post_date(self, item):
        irl_date = item.find("span", {"class":"date"})
        irl_date = irl_date.find("span", {"class":"normal"}).text.strip()
        return irl_date

    def _parse_post_author_infos(self, item):
        author_infos = item.find("span", {"class":"infos"})
        if "inconnu(e)" in author_infos.text:
            return tuple(["Inconnu(e)"]+["?" for i in range(4)])

        name = author_infos.find("a").text.strip()

        others = author_infos.find("div", {"class":"infosurvol"})
        others_string = "".join([str(i) for i in others.children])
        others_split = [i.replace("<b>", "").replace("</b>", "") for i in others_string.split("<br/>")]
        infos = dict()
        for i in others_split:
            if len(i) > 1:
                temp = i.split(" : ")
                infos[temp[0]] = temp[1]
        race = infos["Race"]
        sex = infos["Sexe"]
        look = infos["Apparence"]
        clothes = infos["Habillement"]

        return (name,race,sex,look,clothes)

    def _parse_post_language(self, item):
        return item.find("span", {"class":"langue"}).text.strip()

    def _parse_post_text(self, item):
        text = str(item.find("div", {"class":"message darkbox"}))
        text = self._prettify(text)
        return text

    def _prettify(self, text, newlines=True):
        replacements = [
                ("<br/>","\n"),
                ("<br />","\n"),
                ("\t",""),
                ("\r",""),
                # newlines
                ("\n\n\n","\n"),
                ("[ ]{1,}\n","\n"),
                ("\n[ ]{1,}","\n"),
                # other tags
                ("<div class=\"message darkbox\">(.*?)</div>", r"\1"),
                ("<span>\s*(.*?)\s*</span>",r"<span>\1</span>"),
                ("<div class=\"darkbox\">(.*?)</div>", r"\1"),
                ("<p>(.*?)</p>", r"\n\n\1"),
                ("<ul>(.*?)</ul>", r"\1"),
                ("<li>(.*?)</li>", r"\1"),
                ("<td>(.*?)</td>", r"\1"),
                # empty formatting tags
                ("<span class=\"langage cri\">(\s*)</span>",r"\1"),
                ("<span class=\"narration\">(\s*)</span>",r"\1"),
                ("<span class=\"hj\">(\s*)</span>",r"\1"),
                ("<span class=\"ecriture\">(\s*)</span>",r"\1"),
                ("<div class=\"box\">(\s*)</div>",r"\1"),
                # formatting tags
                ("<span class=\"langage dialogue\">(.*?)</span>",r"\1"),
                ("<span class=\"langage cri\">\s*(\S.*?\S)\s*</span>",       r"0b00df5945BOLD \1 BOLD72800245ef"),
                ("<span class=\"narration\">\s*(\S.*?\S)\s*</span>", r"0b00df5945ITAL \1 ITAL72800245ef"),
                ("<span class=\"hj\">\s*(\S.*?\S)\s*</span>",        r"0b00df5945CODE \1 CODE72800245ef"),
                ("<span class=\"ecriture\">\s*(\S.*?\S)\s*</span>",  r"\n\n0b00df5945BLOC\n\1\nBLOC72800245ef\n\n"),
                ("<div class=\"box\">\s*(\S.*?\S)\s*</div>",  r"\n\n0b00df5945BLOC\n\1\nBLOC72800245ef\n\n"),
                # litteral <
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
        location_type = self._url.split("lieux/")[1].split("/")[0]
        buttons = self._parsed.body.find_all("form", {"method":"post"})
        back_button = buttons[0]
        assert "Revenir" in str(back_button)
        action = back_button.get("action")
        url = self._base_url+location_type+"/"+action
        self._parse_html(url)

        location_type = self._parsed.h2.text # prettier than the previous
        # the location type on the webpage is the same for both in that case
        if location_type == "Les quais":
            location_type = "Le port"
        elif location_type == "La Grand' place":
            location_type = "La ville"
        location_name = self._parsed.h3.text
        full_location = "Vahal - "+location_type+" - "+location_name

        return full_location
