import argparse
import json
import re
import time
import urllib
import sys

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

import helpers
from image import Image


# TODO ADD DOCUMENTATION
class InstagramScraper:
    def __init__(self, args):
        self.username = args.username or input("insert username : ")
        self.next = True
        self.first = True
        self.downloaded = 0
        self.images = []

    @property
    def soup(self):
        http_response = requests.get(self.http_request, timeout=10)
        status_code = http_response.status_code
        if status_code == 404:
            print(f"Error : could not find user {self.username}.")
            sys.exit(1)
        html = http_response.text
        return bs(html, "lxml")

    def get_query_hash(self):
        print("checking user {}...".format(self.username))
        # ppc = profile page container
        ppc_link = self.soup.find("link", href=re.compile("ProfilePageContainer.js"))
        script_url = "http://instagram.com" + ppc_link["href"]
        script = requests.get(script_url, timeout=10).text
        self.query_hash = helpers.query_hash(script)

    @property
    def parsed_json(self):
        if self.first:
            pattern = "window._sharedData = "
            script = self.soup.find("script", text=re.compile(pattern))
            json_string = script.text.replace(pattern, "").replace(";", "")
            return json.loads(json_string)
        else:
            http_response = requests.get(self.http_request, timeout=10).text
            return json.loads(http_response)

    @property
    def http_request(self):
        if self.first:
            return f"https://www.instagram.com/{self.username}/?hl=en"
        else:
            variables = f'{{"id":"{self.id}","first":12,"after":"{self.end_cursor}"}}'
            # encode the variables with the UTF-8 encoding scheme
            encoded = urllib.parse.quote(variables)
            return f"https://www.instagram.com/graphql/query/?query_hash={self.query_hash}&variables={encoded}"

    def get_query_params(self):
        if self.first:
            print("getting user info...")
            user = self.parsed_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            self.id = user["id"]
        else:
            user = self.parsed_json["data"]["user"]

        edge_owner = user["edge_owner_to_timeline_media"]
        posts_count = edge_owner["count"]

        if posts_count == 0:
            print(f"user {self.username} has 0 posts")
            quit()

        page_info = edge_owner["page_info"]
        # get the needed data
        self.next = page_info["has_next_page"]
        self.end_cursor = page_info["end_cursor"]
        if self.first:
            helpers.print_same_line("starting download...")
            print()
        self.images = edge_owner["edges"]

    def download(self, image):
        image.download()
        self.downloaded += 1
        display = "downloaded {} images".format(self.downloaded)
        helpers.print_same_line(display)

    def download_children(self, image):
        for child in image.children:
            self.download(child)

    def download_images(self):
        for item in self.images:
            image = Image.from_json_data(item, self.username)
            if image.is_video:
                continue
            self.download(image)
            if image.has_children:
                image.get_children()
                self.download_children(image)

    def loop(self):
        while self.next:
            self.get_query_params()
            self.download_images()
            self.first = False

    def scrape(self):
        helpers.make_folder(self.username)
        self.loop()
        if self.downloaded > 0:
            print(f"\nsuccessully downloaded {self.downloaded} images")
        else:
            print("no images were found.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="specify the username", metavar="")
    args = parser.parse_args()
    scraper = InstagramScraper(args)
    scraper.get_query_hash()
    scraper.scrape()


if __name__ == "__main__":
    main()
