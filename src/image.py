import os

import requests


class Child:
    def __init__(self, node, username=None):
        self.username = username
        self.id = node["id"]
        self.filename = self.id + ".jpg"
        self.url = node["display_url"]

    def download(self):
        content = requests.get(self.url, timeout=10).content
        destination = os.path.join("data", "images", self.username, self.filename)
        with open(destination, "wb") as f:
            f.write(content)


class Image(Child):
    def __init__(self, node):
        super().__init__(node)
        self.node = node
        self.username = node["owner"]["username"]
        self.type = node["__typename"]
        self.is_video = node["is_video"]

    def children(self):
        result = []
        if self.type == "GraphSidecar":
            edges = self.node["edge_sidecar_to_children"]["edges"][1:]
            for item in edges:
                node = item["node"]
                child = Child(node, self.username)
                result.append(child)
        return result
