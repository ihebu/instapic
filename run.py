import sys


from helpers import make_folder
from scraper import InstagramScraper


def main():
    scraper = InstagramScraper()
    scraper.query_hash = scraper.get_query_hash()
    scraper.scrape()
    make_folder(scraper.username)
    scraper.download_images()


if __name__ == "__main__":
    main()
