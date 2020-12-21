# -*- coding: utf-8 -*-

import os
import browser_cookie3
import requests
import bs4
import re
import atexit
import fake_useragent
import logging
logger = logging.getLogger(__name__)


from ..rp_manager import RPmanager


class EdenyaParser:

    def __init__(self, urls, secrets, rps_dir):
        self._define_urls()
        self._login(secrets)
        self.rps = {}

        for url in urls:
            self._parse_location_main_type(url)
            self._parse_html(url)
            # TODO: this is not enough stringeant
            if not "Situation RP" in self._parsed.body.text:
                logger.error("Returned page is not a RP: {}".format(url))
                continue

            logger.debug("Building RP of {}".format(url))
            self._rp = RPmanager(rps_dir, "%Y-%m-%d %H:%M:%S")

            self._parse_urls()
            for page,page_url in enumerate(self._urls):
                self._parse_html(page_url)
                self._parse_rp(page)
                if page == 0:
                    if not self._already_in:
                        location = self._parse_location(page_url)
                    else:
                        location = self._rp.get_location()
                    self._rp.set_metadata(location)

            self._rp.save()
            self.rps[url] = self._rp
            logger.debug("RP parsing finished: {}".format(url))

        logger.info("Closing session.")
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
        edenya_cookies = self._get_cookies()
        edenya_cookies_names = [c.name for c in edenya_cookies]
        check_cookie_name = "cache_timezone"
        if not check_cookie_name in edenya_cookies_names:
            logger.info("Setting new session.")
            self._response = self._session.post(self._login_url, data=load, verify=True, headers={**header,**supp_header})
            if not self._response.ok or not check_cookie_name in self._session.cookies.keys():
                logger.error("Could not connect to Edenya.")
                return
            self._session.get("https://v4.edenya.net/accueil/", headers=header)
            self._session.get("https://v4.edenya.net/jouer/", headers=header)
            self._session.get("https://v4.edenya.net/_game/vahal/accueil/", headers=header)
        else:
            logger.info("Using existing session.")
            for c in edenya_cookies:
                self._session.cookies.set_cookie(c)

    def _get_cookies(self):
        flatpak_firefox = os.path.expanduser("~/.var/app/org.mozilla.firefox/.mozilla/firefox")
        if os.path.exists(flatpak_firefox):
            logger.info("Getting cookies from firefox flatpak.")
            profile = [i for i in os.listdir(flatpak_firefox) if "default-beta" in i][0]
            cookie_path = flatpak_firefox+"/"+profile+"/cookies.sqlite"
            cookies = browser_cookie3.firefox(cookie_file=cookie_path)
        else:
            logger.info("Loading cookies from all browsers.")
            cookies = browser_cookie3.load()
        cookies.clear_expired_cookies()
        domain_cookies = [c for c in cookies if self._domain in c.domain]
        logger.debug("Cookies: {}".format(repr([c.name for c in domain_cookies])))
        return domain_cookies

    def _parse_location_main_type(self, url):
        self._location_type = url.split("lieux/")[1].split("?")[0]

    def _parse_html(self, url):
        raw_html = self._session.get(url).text
        self._parsed = bs4.BeautifulSoup(raw_html,features="lxml")

    def _parse_urls(self):
        links = self._parsed.body.find_all('div', attrs={'class':'pager'})
        self._urls = []
        for i in links[0].find_all("a"):
            if not "Suivant" in i.text and not "Précédent" in i.text:
                self._urls.append(self._base_url+self._location_type+"/"+i["href"])

    def _parse_rp(self, page):
        posts = self._parsed.body.find_all('div', attrs={'class':'forum-message box'})
        ig_date = self._parse_ig_date()
        weather = self._parse_weather()
        if page == 0 :
            self._rp_title = self._parse_post_title(posts[0])
            self._already_in = self._rp.load(self._rp_title)
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
        weather = [re.sub(r"<strong>(.*)</strong>(.*)",r"\1\2", i.strip()) for i in weather_split]
        weather = [i.lower().capitalize() for i in weather]
        weather_str = ", ".join(weather)
        return weather_str

    def _get_context_box(self):
        for i in self._parsed.body.find_all("div", {"class":"darkbox"}):
            if "La date" in i.text:
                date_box = i
                break
        return date_box

    def _parse_post_date(self, item):
        dates = item.find("div", {"class":"date"})
        try:
            irl_date = dates.find("span", {"class":"normal"}).text.strip()
        except AttributeError:
            irl_date = dates.find("span", {"class":"new"}).text.strip()
        return irl_date

    def _parse_post_author_infos(self, item):
        author_infos = item.find("div", {"class":"infos"})
        if "inconnu(e)" in author_infos.text:
            return tuple(["Inconnu(e)"]+["?" for i in range(4)])

        name = author_infos.find("a").text.strip()

        others = author_infos.find("div", {"class":"infosurvol"})
        others_string = "".join([str(i) for i in others.children])
        others_split = [i.replace("<b>", "").replace("</b>", "") for i in others_string.split("<br/>")]
        others_split = [i for i in others_split if not "<" in i and not ">" in i]
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
        return item.find("div", {"class":"langue"}).text.strip()

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
                ("<span class=\"langage dialogue .*?\">(.*?)</span>",r"\1"),
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

    def _parse_location(self, url):
        buttons = self._parsed.body.find_all("form", {"method":"post"})
        back_button = buttons[0]
        assert "Revenir" in str(back_button)
        action = back_button.get("action")
        url = self._base_url+self._location_type+"/"+action
        self._parse_html(url)

        location_type = self._parsed.h2.text # prettier than the previous
        # the location type on the webpage is the same for both in that case
        if location_type == "Les quais":
            location_type = "Le port"
        elif location_type == "La Grand' place":
            location_type = "La ville"
        location_name = self._parsed.h2.text
        full_location = "Vahal - "+location_type
        full_location += " - "+location_name if location_type != location_name else ""
        return full_location
