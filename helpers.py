from sys import stdout
from os import mkdir
import shutil
import re


def print_same_line(text):
    stdout.write("\r")
    stdout.flush()
    stdout.write(text)
    stdout.flush()


def make_http_request(query_hash, profile_id, end_cursor):
    sample = f'https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={{"id":"{profile_id}","first":12,"after":"{end_cursor}"}}'
    return sample


def rmtree(path):
    try:
        shutil.rmtree(path)
    except:
        print(f"Error :  could not delete folder {path}")
        quit()


def make_folder(user_name):
    try:
        mkdir("images")
        try:
            mkdir("images/" + user_name)
        except FileExistsError:
            print(f"folder /images/{user_name} already exists.")
            rmtree("images/" + user_name)
            mkdir("images/" + user_name)
        except:
            print("Internal error: couldn't create the images folder.")
            quit()

    except FileExistsError:
        try:
            mkdir("images/" + user_name)
        except FileExistsError:
            rmtree("images/" + user_name)
            mkdir("images/" + user_name)
        except:
            print(f"Internal error: couldn't create /images/{user_name} folder.")
            quit()

    except:
        print("Error: couldn't create /images folder.")
        quit()


def query_hash(script):
    pattern = re.compile(r'profilePosts.+\.pagination},queryId:"\w+"')
    match = re.search(pattern, script)
    result = match.group(0)
    split = result.split('"')
    return split[1]
