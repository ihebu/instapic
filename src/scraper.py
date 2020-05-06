import json
import os
import re
import urllib

import requests
from bs4 import BeautifulSoup as bs

from user import User


def folder(parent, username):
    if not os.path.isdir("data"):
        os.mkdir("data")
    path = os.path.join("data", parent)
    if not os.path.isdir(path):
        os.mkdir(path)
    path = os.path.join("data", parent, username)
    if not os.path.isdir(path):
        os.mkdir(path)


class InstagramScraper:
    def __init__(self, username, download, extract):
        self.first = True
        self.username = username
        self.download = download
        self.extract = extract
        self.query_hash = "9dcf6e1a98bc7f6e92953d5a61027b98"

    @property
    def json(self):
        if self.first:
            print(f"checking user {self.username}...")
            url = "https://www.instagram.com/" + self.username
            html = requests.get(url, timeout=10).text
            soup = bs(html, "lxml")
            pattern = "window._sharedData = "
            script = soup.find("script", text=re.compile(pattern))
            raw = script.text.replace(pattern, "").replace(";", "")
        else:
            url = "https://www.instagram.com/graphql/query/?" + self.query_params
            raw = requests.get(url, timeout=10).text
        return json.loads(raw)

    @property
    def variables(self):
        obj = {"id": self.user.id, "first": 12, "after": self.user.end_cursor}
        return json.dumps(obj)

    @property
    def query_params(self):
        params = {"query_hash": self.query_hash, "variables": self.variables}
        return urllib.parse.urlencode(params)

    def update_user(self):
        if self.first:
            data = self.json["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            self.user = User(data)
        else:
            data = self.json["data"]["user"]
            self.user.update(data)

    def scrape(self):
        if self.download:
            folder("images", self.username)
        if self.extract:
            folder("json", self.username)
        while True:
            self.update_user()
            if self.first and self.extract:
                self.user.export_json()
            if self.download:
                self.user.download()
            else:
                break
            self.first = False
            if not self.user.next:
                break
        print("\n" + "done.")


def main():
    username = input("Enter username : ").strip()
    print()
    print("[1] Download user pictures")
    print("[2] Extract user info in JSON format")
    print()
    print("Usage : enter the desired numbers separated by a blank space")
    options = input("Enter the option(s) : ").split()
    print()
    download = extract = False
    if len(options) == 0:
        quit()
    for option in options:
        if option == "1":
            download = True
        elif option == "2":
            extract = True
        else:
            quit()
    scraper = InstagramScraper(username, download, extract)
    scraper.scrape()


if __name__ == "__main__":
    main()
