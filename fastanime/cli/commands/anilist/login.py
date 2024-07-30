import webbrowser

import click
from rich import print
from rich.prompt import Confirm, Prompt

from ....anilist import AniList
from ...config import Config
from ...utils.tools import exit_app


@click.command(help="Login to your anilist account")
@click.option("--status", "-s", help="Whether you are logged in or not", is_flag=True)
@click.pass_obj
def login(config: Config, status):
    if status:
        is_logged_in = True if config.user else False
        message = (
            "You are logged in :happy:" if is_logged_in else "You arent logged in :cry"
        )
        print(message)
        print(config.user)
        exit_app()
    if config.user:
        print("Already logged in :confused:")
        if not Confirm.ask("or would you like to reloggin", default=True):
            exit_app()
    # ---- new loggin -----
    print(
        f"A browser session will be opened ( [link]{config.fastanime_anilist_app_login_url}[/link] )",
    )
    webbrowser.open(config.fastanime_anilist_app_login_url)
    print("Please paste the token provided here")
    token = Prompt.ask("Enter token")
    user = AniList.login_user(token)
    if not user:
        print("Sth went wrong", user)
        exit_app()
        return
    user["token"] = token
    config.update_user(user)
    print("Successfully saved credentials")
    print(user)
    exit_app()
