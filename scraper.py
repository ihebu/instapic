import json
import re
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from helpers import get_json_string, make_folder, print_same_line, rmtree, query_hash
from image import Image
import socket

# TODO ADD DOCUMENTATION


class InstagramScraper:
    @staticmethod
    def get_username():
        prompt = input("insert instagram username : ").strip()

        if prompt == "":
            print("Error : username cannot be empty. Please use a valid username")
            quit()

        if len(prompt) > 30:
            print(
                "Error : username cannot contain more than 30 characters. Please use a valid username"
            )
            quit()

        for char in prompt:
            if not (char.isalnum() or char == "." or char == "_"):
                print(
                    "Error : username can only contain letters, numbers, periods, and underscores. Please use a valid username"
                )
                quit()

        return prompt

    def __init__(self):
        self.username = self.get_username()
        self.query_hash = ""
        self.id = ""
        self.has_next_page = True
        self.end_cursor = ""
        self.first = True
        self.count = 0
        self.downloaded = 0
        self.images = []
        self.downloads = []

    @property
    def soup(self):
        try:
            http_response = requests.get(self.http_request).text
            return bs(http_response, "lxml")
        except:
            print(
                "Error : failed to establish connection. Please verify your internet connection"
            )
            quit()

    def get_query_hash(self):
        print(f"scraping user {self.username}...")
        # ppc = profile page container
        ppc_link = self.soup.find("link", href=re.compile("ProfilePageContainer.js"))
        if not ppc_link:
            print(
                f"Error : could not find user {self.username}. Please verify that the user exists."
            )
            quit()

        script_url = "http://instagram.com" + ppc_link["href"]
        script = requests.get(script_url).text
        return query_hash(script)

    @property
    def parsed_json(self):
        if self.first:
            script = self.soup.find("script", text=re.compile("window._sharedData"))
            json_string = get_json_string(script)
            return json.loads(json_string)
        else:
            http_response = requests.get(self.http_request).text
            return json.loads(http_response)

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
        posts_count = edge_owner["count"]
        if posts_count == 0:
            print(f"user {self.username} has 0 posts")
            quit()
        page_info = edge_owner["page_info"]
        # get the needed data
        self.has_next_page = page_info["has_next_page"]
        self.end_cursor = page_info["end_cursor"]
        if self.first:
            print("collecting images (ctrl + c to stop)")
        self.images = edge_owner["edges"]

    def scrape(self):
        while self.has_next_page:
            try:
                self.get_query_params()
                for item in self.images:
                    image = Image.from_json_data(item, self.username)
                    self.count += 1
                    self.downloads.append(image)
                    print_same_line(f"collected [ {self.count} images. ]")
                    if image.has_children:
                        image.get_children()
                        self.count += image.num_of_children
                        self.downloads += image.children
                        print_same_line(f"collected [ {self.count} images. ] ")
                self.first = False

            except KeyboardInterrupt:
                print("\nKeyboard interrupt : Search stopped.")
                break

            except:
                print(
                    "\nError: could not establish connection. Please check your internet connection"
                )
                quit()

        if self.count > 0:
            print(f"successully collected {self.count} images")
        else:
            print("no images were found.")
            quit()

    def download_images(self):
        print("Starting download (ctrl + c to stop)")
        downloader = tqdm(self.downloads, leave=False)
        for image in downloader:
            downloader.set_description(f"downloading {image.shortcode}.jpg")
            try:
                image.download()
                self.downloaded += 1

            except KeyboardInterrupt:
                print("\nKeyboard interrupt : download stopped.")
                downloader.close()
                break

            except Exception as exception:
                print_same_line(
                    f"Error : could not establish connection. Please check your internet connection"
                )

        if self.downloaded > 0:
            print(f"successfully downloaded {self.downloaded} images")
        else:
            print("no images were downloaded")
            rmtree("images/" + self.username)
