from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="Login to your anilist account")
@click.option("--status", "-s", help="Whether you are logged in or not", is_flag=True)
@click.option("--erase", "-e", help="Erase your login details", is_flag=True)
@click.pass_obj
def login(config: "Config", status, erase):
    from sys import exit

    from rich import print
    from rich.prompt import Confirm, Prompt

    if status:
        is_logged_in = True if config.user else False
        message = (
            "You are logged in :smile:" if is_logged_in else "You arent logged in :cry:"
        )
        print(message)
        print(config.user)
        exit(0)
    elif erase:
        if Confirm.ask(
            "Are you sure you want to erase your login status", default=False
        ):
            config.update_user({})
            print("Success")
            exit(0)
        else:
            exit(1)
    else:
        from click import launch

        from ....anilist import AniList

        if config.user:
            print("Already logged in :confused:")
            if not Confirm.ask("or would you like to reloggin", default=True):
                exit(0)
        # ---- new loggin -----
        print(
            f"A browser session will be opened ( [link]{config.fastanime_anilist_app_login_url}[/link] )",
        )
        launch(config.fastanime_anilist_app_login_url, wait=True)
        print("Please paste the token provided here")
        token = Prompt.ask("Enter token")
        user = AniList.login_user(token)
        if not user:
            print("Sth went wrong", user)
            exit(1)
            return
        user["token"] = token
        config.update_user(user)
        print("Successfully saved credentials")
        print(user)
        exit(0)
