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
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt : Instagram Scraper stopped.")

    except NameError:
        print("Error : Please check that all necessary dependencies are installed.")

    except (NameError, ModuleNotFoundError):
        print("\nError : Please check that all necessary dependencies are installed.")

    except:
        print("\nAn unknown error has occured: Instagram Scraper stopped.")

    except Exception as e:
        print(f"Error : {e}")
