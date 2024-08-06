import click


@click.command(
    help="Opens up your fastanime config in your preferred editor",
    short_help="Edit your config",
)
@click.option("--path", "-p", help="Print the config location and exit", is_flag=True)
@click.option(
    "--desktop-entry",
    "-d",
    help="Configure the desktop entry of fastanime",
    is_flag=True,
)
# @click.pass_obj
def configure(path, desktop_entry):
    import os
    import subprocess

    from pyshortcuts import make_shortcut
    from rich import print

    from ...constants import APP_NAME, ICON_PATH, USER_CONFIG_PATH
    from ..utils.tools import exit_app

    if path:
        print(USER_CONFIG_PATH)
    elif desktop_entry:
        import shutil

        FASTANIME_EXECUTABLE = shutil.which("fastanime")
        if FASTANIME_EXECUTABLE:
            cmds = f"{FASTANIME_EXECUTABLE} --rofi anilist"
        else:
            cmds = "_ -m fastanime --rofi anilist"
        shortcut = make_shortcut(
            name=APP_NAME,
            description="Watch Anime from the terminal",
            icon=ICON_PATH,
            script=cmds,
            terminal=False,
        )
        if shortcut:
            print("Success", shortcut)
        else:
            print("Failed")
    else:
        if EDITOR := os.environ.get("EDITOR"):
            subprocess.run([EDITOR, USER_CONFIG_PATH])
            exit_app()
        else:
            print("$EDITOR environment variable missing :confused:")
            print(
                "Please Set the $EDITOR environment variable to enable editing of config"
            )
