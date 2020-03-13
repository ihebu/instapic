from helpers import make_folder
from scraper import InstagramScraper


def main():
    scraper = InstagramScraper()
    scraper.get_query_hash()
    scraper.scrape()
    if scraper.approve_download:
        scraper.download_images()
    else:
        print("Aborting download.")
        quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt : Instagram Scraper stopped.")

    # check for dependencies
    except (NameError, ModuleNotFoundError):
        raise
        print("\nError : Please check that all necessary dependencies are installed.")

    except Exception as e:
        print(f"An unexpected error has occured.")
