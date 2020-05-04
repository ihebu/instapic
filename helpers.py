from sys import stdout
import os
import re


def print_same_line(text):
    stdout.write("\r")
    stdout.flush()
    stdout.write(text)
    stdout.flush()


def make_folder(name):
    if os.path.isdir("images"):
        path = os.path.join("images", name)
        if not os.path.isdir(path):
            os.mkdir(path)
    else:
        os.mkdir("images")
        path = os.path.join("images", name)
        os.mkdir(path)
