import shutil
import subprocess
from sys import exit


def feh_manga_viewer(image_links: list[str], window_title: str):
    FEH_EXECUTABLE = shutil.which("feh")
    if not FEH_EXECUTABLE:
        print("feh not found")
        exit(1)
    commands = [FEH_EXECUTABLE, *image_links, "--title", window_title]
    subprocess.run(commands)
