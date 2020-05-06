import json
import sys
import urllib

import requests
from bs4 import BeautifulSoup as bs

import helpers
from image import Image
from user import User


class InstagramScraper:
    def __init__(self):
        self.username = input("insert username : ").strip()
        self.next = True
        self.first = True
        self.downloaded = 0
        self.query_hash = "9dcf6e1a98bc7f6e92953d5a61027b98"
        self.images = []

    @property
    def json(self):
        if self.first:
            string = helpers.link(self.url)
        else:
            string = requests.get(self.url, timeout=10).text
        return json.loads(string)

    @property
    def variables(self):
        return {"id": self.user.id, "first": 12, "after": self.end_cursor}

    @property
    def query_params(self):
        params = {
            "query_hash": self.query_hash,
            "variables": json.dumps(self.variables),
        }
        return urllib.parse.urlencode(params)

    @property
    def url(self):
        if self.first:
            return "https://www.instagram.com/" + self.username
        return "https://www.instagram.com/graphql/query/?" + self.query_params

    def get_query_params(self):
        if self.first:
            data = self.json["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            self.user = User(data)
            if self.user.is_private:
                print("User account is private. Abort")
                sys.exit()
        else:
            data = self.json["data"]["user"]
        edge_owner = data["edge_owner_to_timeline_media"]
        page_info = edge_owner["page_info"]
        self.next = page_info["has_next_page"]
        self.end_cursor = page_info["end_cursor"]
        self.images = edge_owner["edges"]
        if self.user.posts_count == 0:
            print(f"user {self.username} has 0 posts")
            sys.exit()
        if self.first:
            helpers.print_same_line("starting download...")
            print()

    def download(self, image):
        image.download()
        self.downloaded += 1
        display = "downloaded {} images".format(self.downloaded)
        helpers.print_same_line(display)

    def download_images(self):
        for item in self.images:
            image = Image(item)
            if image.is_video:
                continue
            self.download(image)
            if image.has_children:
                for child in image.children():
                    self.download(child)

    def scrape(self):
        helpers.make_folder(self.username)
        print("getting user info...")
        while self.next:
            self.get_query_params()
            self.download_images()
            self.first = False

        if self.downloaded > 0:
            print(f"\nsuccessully downloaded {self.downloaded} images")
        else:
            print("no images were found.")


def main():
    scraper = InstagramScraper()
    scraper.scrape()


if __name__ == "__main__":
    main()
