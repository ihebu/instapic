import json
import os

from image import Image


class User:
    def __init__(self, data):
        self.update(data)
        self.username = data["username"]
        self.full = data["full_name"]
        self.bio = data["biography"]
        self.id = data["id"]
        self.followers = data["edge_followed_by"]["count"]
        self.followees = data["edge_follow"]["count"]
        self.posts_count = self.timeline_media["count"]
        self.is_private = data["is_private"]
        self.is_verified = data["is_verified"]
        self.is_business = data["is_business_account"]
        self.business_category = data["business_category_name"]
        self.has_channel = data["has_channel"]
        self.is_joined_recently = data["is_joined_recently"]
        self.profile_pic = data["profile_pic_url"]
        self.profile_pic_hd = data["profile_pic_url_hd"]
        self.next = True
        self.downloaded = 0

    def update(self, data):
        self.timeline_media = data["edge_owner_to_timeline_media"]
        self.page_info = self.timeline_media["page_info"]
        self.end_cursor = self.page_info["end_cursor"]
        self.next = self.page_info["has_next_page"]

    @property
    def images(self):
        arr = self.timeline_media["edges"]
        n = len(arr)
        for i in range(n):
            node = arr[i]["node"]
            arr[i] = Image(node)
        return arr

    def download_image(self, img):
        img.download()
        self.downloaded += 1
        print("\r" + f"downloaded {img.filename}", end="", flush=True)
        print("\t" + f"(total {self.downloaded})", end="", flush=True)

    def download_children(self, img):
        for child in img.children():
            self.download_image(child)

    def download(self):
        for image in self.images:
            if image.is_video:
                continue
            self.download_image(image)
            self.download_children(image)

    def export_json(self):
        data = {
            "id": self.id,
            "username": self.username,
            "full name": self.full,
            "bio": self.bio,
            "followers": self.followers,
            "followees": self.followees,
            "posts": self.posts_count,
            "is_private": self.is_private,
            "profile_pic": self.profile_pic,
            "is_verified": self.is_verified,
            "is_business_account": self.is_business,
            "business_category": self.business_category,
            "has_channel": self.has_channel,
            "is_joined_recently": self.is_joined_recently,
        }
        path = os.path.join("data", "json", self.username, "data.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
