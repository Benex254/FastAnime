import shutil
import subprocess

import requests


def print_img(url: str):
    """helper funtion to print an image given its url

    Args:
        url: [TODO:description]
    """
    if EXECUTABLE := shutil.which("icat"):
        subprocess.run([EXECUTABLE, url])
    else:
        EXECUTABLE = shutil.which("chafa")

        if EXECUTABLE is None:
            print("chafanot found")
            return

        res = requests.get(url)
        if res.status_code != 200:
            print("Error fetching image")
            return
        img_bytes = res.content
        subprocess.run([EXECUTABLE, url, "--size=15x15"], input=img_bytes)
