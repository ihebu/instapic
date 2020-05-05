import os
import re
import sys

import requests
from bs4 import BeautifulSoup as bs


def print_same_line(text):
    sys.stdout.write("\r")
    sys.stdout.flush()
    sys.stdout.write(text)
    sys.stdout.flush()


def make_folder(name):
    if os.path.isdir("images"):
        path = os.path.join("images", name)
        if not os.path.isdir(path):
            os.mkdir(path)
    else:
        os.mkdir("images")
        path = os.path.join("images", name)
        os.mkdir(path)


def link(url):
    html = requests.get(url, timeout=10).text
    soup = bs(html, "lxml")
    pattern = "window._sharedData = "
    script = soup.find("script", text=re.compile(pattern))
    string = script.text.replace(pattern, "").replace(";", "")
    return string
