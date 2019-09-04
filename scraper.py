import json
import re
import time
from os import mkdir
from helpers import rmtree
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

import util
from helpers import get_json_string, make_folder, print_same_line
from image import Image


class InstagramScraper:
    def get_username(self):
        while True:
            username = input("insert instagram username : ")
            if username.strip() != "":
                return username

    def __init__(self):
        self.username = self.get_username()
        self.query_hash = ""
        self.id = ""
        self.has_next_page = True
        self.end_cursor = ""
        self.first = True
        self.images = []
        self.count = 0
        self.downloads = []
        self.downloaded = 0

    @property
    def soup(self):
        http_response = requests.get(self.http_request).text
        return bs(http_response, "lxml")

    def get_query_hash(self):
        # ppc = profile page container
        ppc_link = self.soup.find("link", href=re.compile("ProfilePageContainer.js"))
        script_url = "http://instagram.com" + ppc_link["href"]
        script = requests.get(script_url).text
        pattern = re.compile(r'profilePosts.+\.pagination},queryId:"\w+"')
        match = re.search(pattern, script)
        result = match.group(0)
        split = result.split('"')
        return split[1]

    @property
    def parsed_json(self):
        if self.first:
            script = self.soup.find("script", text=re.compile("window._sharedData"))
            json_string = get_json_string(script)
            return json.loads(json_string)
        else:
            http_response = requests.get(self.http_request).text
            return json.loads(http_response)

        # extract the json part as text

    @property
    def http_request(self):
        if self.first:
            return f"https://www.instagram.com/{self.username}/?hl=en"
        else:
            variables = f'{{"id":"{self.id}","first":12,"after":"{self.end_cursor}"}}'
            # encode the variables with the UTF-8 encoding scheme
            encoded = quote(variables)
            return f"https://www.instagram.com/graphql/query/?query_hash={self.query_hash}&variables={encoded}"

    def get_query_params(self):
        if self.first:
            user = self.parsed_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]
            self.id = user["id"]
        else:
            user = self.parsed_json["data"]["user"]

        edge_owner = user["edge_owner_to_timeline_media"]
        page_info = edge_owner["page_info"]
        # get the needed data
        self.has_next_page = page_info["has_next_page"]
        self.end_cursor = page_info["end_cursor"]
        self.images = edge_owner["edges"]

    def scrape(self):
        print("collecting images (ctrl + c to stop)")
        try:
            animation = "|/-\\"
            i = 0
            while self.has_next_page:
                self.get_query_params()
                for item in self.images:
                    image = Image.from_json_data(item, self.username)
                    self.count += 1
                    self.downloads.append(image)
                    i += 1
                    print_same_line(
                        f"collected [ {self.count} images. ] {animation[i % len(animation)]}"
                    )

                    if image.has_children:
                        image.get_children()
                        self.count += image.num_of_children
                        self.downloads += image.children
                        i += 1
                        print_same_line(
                            f"collected [ {self.count} images. ] {animation[i % len(animation)]}"
                        )
                self.first = False
        except KeyboardInterrupt:
            print("\nKeyboard interrupt : search stopped.")

        print(f"successully collected {self.count} images")

    def download_images(self):
        print("Starting download (ctrl + c to stop)")
        downloads = tqdm(self.downloads, leave=False)
        for image in downloads:
            downloads.set_description(f"downloading {image.shortcode}.jpg")
            try:
                image.download()
                self.downloaded += 1

            except KeyboardInterrupt:
                print("\nKeyboard interrupt : download stopped.")
                downloads.close()
                break

            except:
                print_same_line(
                    f"error downloading {image.shortcode}.jpg | image skipped"
                )

        if self.downloaded > 0:
            print(f"successfully downloaded {self.downloaded} images")
        else:
            print("no images were downloaded")
            rmtree("images/" + self.username)

