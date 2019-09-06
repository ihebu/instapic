from helpers import print_same_line, get_json_string
import requests
from bs4 import BeautifulSoup as bs
import re
import json


class Image:
    def __init__(self, shortcode, display_url, __typename, username):
        self.shortcode = shortcode
        self.display_url = display_url
        self.__typename = __typename
        self.username = username
        self.children = []
        self.num_of_children = 0

    @classmethod
    def get_child(cls, item, username):
        image_object = item["node"]
        shortcode = image_object["shortcode"]
        display_url = image_object["display_url"]
        __typename = image_object["__typename"]
        return cls(shortcode, display_url, __typename, username)

    @classmethod
    def from_json_data(cls, data, username):
        item = data["node"]
        shortcode = item["shortcode"]
        display_url = item["display_url"]
        __typename = item["__typename"]
        return cls(shortcode, display_url, __typename, username)

    @property
    def has_children(self):
        return self.__typename == "GraphSidecar"

    @property
    def content(self):
        return requests.get(self.display_url).content

    def download(self):
        destination = f"images/{self.username}/{self.shortcode}.jpg"
        with open(destination, "wb") as image_file:
            image_file.write(self.content)

    def get_children(self):
        children_link = "https://www.instagram.com/p/" + self.shortcode
        html = requests.get(children_link,timeout=10).text
        soup = bs(html, "lxml")
        script = soup.find("script", text=re.compile("window._sharedData"))
        json_string = get_json_string(script)
        parsed_json = json.loads(json_string)
        profile_page_data = parsed_json["entry_data"]["PostPage"][0]
        shortcode_media = profile_page_data["graphql"]["shortcode_media"]
        result = shortcode_media["edge_sidecar_to_children"]["edges"]

        for item in result[1:]:
            child = Image.get_child(item, self.username)
            self.children.append(child)
            self.num_of_children += 1

