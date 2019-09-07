try:
    import urllib
    import requests

    from bs4 import BeautifulSoup as bs
    from tqdm import tqdm
except:
    print("Error : Please check that all necessary dependencies are installed.")
    print("run '$ pip install -r requirements.txt'")
    quit()

import json
import re
import time

from helpers import get_json_string, make_folder, print_same_line, query_hash, rmtree
from image import Image

# TODO ADD DOCUMENTATION


class InstagramScraper:
    @staticmethod
    def get_username():
        prompt = input("insert instagram username: ").strip()

        if prompt == "":
            print("Error : username cannot be empty. Please use a valid username")
            quit()

        if len(prompt) > 30:
            print("Error : username is too long. Please use a valid username")
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
            http_response = requests.get(self.http_request, timeout=10)
            status_code = http_response.status_code

            if status_code == 404:
                print(
                    f"Error : could not find user {self.username}. Please verify that the user exists."
                )
                quit()

            html = http_response.text
            return bs(html, "lxml")

        except KeyboardInterrupt:
            raise

        except requests.exceptions.ConnectionError:
            print("Connection Error : Please verify your internet connection")
            quit()

        except requests.exceptions.ReadTimeout:
            print_same_line("Timeout Error: Query stopped due to timeout")
            quit()

        except:
            raise

    def get_query_hash(self):
        print(f"scraping user '{self.username}'...")
        # ppc = profile page container
        ppc_link = self.soup.find("link", href=re.compile("ProfilePageContainer.js"))
        script_url = "http://instagram.com" + ppc_link["href"]

        try:
            script = requests.get(script_url, timeout=10).text

        except KeyboardInterrupt:
            raise

        except requests.exceptions.ConnectionError:
            print("Connection Error : Please verify your internet connection")
            quit()

        except requests.exceptions.ReadTimeout:
            print_same_line("Timeout Error: Query stopped due to timeout")
            quit()

        except:
            raise

        self.query_hash = query_hash(script)

    @property
    def parsed_json(self):
        if self.first:
            script = self.soup.find("script", text=re.compile("window._sharedData"))
            json_string = get_json_string(script)
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
        self.has_next_page = page_info["has_next_page"]
        self.end_cursor = page_info["end_cursor"]
        if self.first:
            print_same_line("collecting images...")
            print()
        self.images = edge_owner["edges"]

    def scrape(self):
        while self.has_next_page:
            try:
                self.get_query_params()
                for item in self.images:
                    image = Image.from_json_data(item, self.username)
                    self.count += 1
                    self.downloads.append(image)
                    print_same_line(f"[{self.count} images]")
                    if image.has_children:
                        image.get_children()
                        self.count += image.num_of_children
                        self.downloads += image.children
                        print_same_line(f"[{self.count} images]")
                self.first = False

            except KeyboardInterrupt:
                print_same_line("Keyboard interrupt : Search stopped.\n")
                break

            except requests.exceptions.ConnectionError:
                print("\nConnection Error : Please verify your internet connection")
                quit()

            except requests.exceptions.ReadTimeout:
                print("\nTimeout Error: Query stopped due to timeout")
                quit()

            except:
                raise

        if self.count > 0:
            print(f"successully collected {self.count} images")
        else:
            print("no images were found.")
            quit()

    def download_images(self):
        print("Starting download...")
        downloader = tqdm(self.downloads, leave=False)
        for image in downloader:
            downloader.set_description(f"downloading {image.shortcode}.jpg")
            try:
                image.download()
                self.downloaded += 1

            except KeyboardInterrupt:
                print_same_line("Keyboard interrupt : download stopped.\n")
                break

            except requests.exceptions.ConnectionError:
                print("Connection Error : Please verify your internet connection")
                quit()

            except requests.exceptions.ReadTimeout:
                print_same_line("Timeout Error: Query stopped due to timeout")
                quit()

            except:
                raise

        if self.downloaded > 0:
            print(f"successfully downloaded {self.downloaded} images")
        else:
            print("no images were downloaded.")
            rmtree("images/" + self.username)
