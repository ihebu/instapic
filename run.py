from helpers import make_folder
from scraper import InstagramScraper


def get_username():

    prompt = input("insert instagram username: ")
    # remove spaces from user input
    prompt = prompt.strip()
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


def main():
    username = get_username()
    scraper = InstagramScraper(username)
    scraper.get_query_hash()
    scraper.scrape()
    make_folder(username)
    scraper.download_images()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt : Instagram Scraper stopped.")

    # check for dependencies
    except (NameError, ModuleNotFoundError):
        print("\nError : Please check that all necessary dependencies are installed.")

    except Exception as e:
        print(f"An unexpected error has occured.")
