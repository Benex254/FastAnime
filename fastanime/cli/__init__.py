import click
from rich import print
from .commands import search, download, anilist

commands = {"search": search, "download": download, "anilist": anilist}


@click.group(commands=commands)
def run_cli():
    print("Yellow")
