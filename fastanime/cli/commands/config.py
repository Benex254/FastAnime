import os
import subprocess

import click
from rich import print

from ... import USER_CONFIG_PATH
from ..utils.tools import exit_app


@click.command(
    help="Opens up your fastanime config in your preferred editor",
    short_help="Edit your config",
)
@click.option("--path", "-p", help="Print the config location and exit", is_flag=True)
def configure(path):
    if path:
        print(USER_CONFIG_PATH)
    else:
        if EDITOR := os.environ.get("EDITOR"):
            subprocess.run([EDITOR, USER_CONFIG_PATH])
            exit_app()
        else:
            print("$EDITOR environment variable missing :confused:")
            print(
                "Please Set the $EDITOR environment variable to enable editing of config"
            )
