import os

import requests


class Image:
    def __init__(self, item, username=None):
        node = item["node"]
        self.username = username or node["owner"]["username"]
        self.node = node
        self.id = node["id"]
        self.url = node["display_url"]
        self.type = node["__typename"]
        self.is_video = node["is_video"]
        self.has_children = self.type == "GraphSidecar"
        self.filename = self.id + ".jpg"

    def download(self):
        content = requests.get(self.url, timeout=10).content
        destination = os.path.join("images", self.username, self.filename)
        with open(destination, "wb") as f:
            f.write(content)

    def children(self):
        edges = self.node["edge_sidecar_to_children"]["edges"][1:]
        result = []
        for item in edges:
            child = Image(item, self.username)
            result.append(child)
        return result
