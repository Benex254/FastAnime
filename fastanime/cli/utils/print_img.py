import shutil
import subprocess

import requests


def print_img(url: str):
    executable = shutil.which("chafa")
    curl = shutil.which("curl")
    #   curl -sL "$1" | chafa /dev/stdin

    if executable is None or curl is None:
        print("chafa or curl not found")
        return

    res = requests.get(url)
    if res.status_code != 200:
        print("Error fetching image")
        return
    img_bytes = res.content
    if not img_bytes:
        print("No image found")
        img_bytes = subprocess.check_output([curl, "-sL", url])
    subprocess.run([executable, url, "--size=15x15"], input=img_bytes)
