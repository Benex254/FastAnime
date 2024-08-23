from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="Print out your anilist stats")
@click.pass_obj
def stats(
    config: "Config",
):
    import shutil
    import subprocess
    from sys import exit

    from rich.console import Console

    console = Console()
    from rich.markdown import Markdown
    from rich.panel import Panel

    from ....anilist import AniList

    user_data = AniList.get_user_info()
    if not user_data[0] or not user_data[1]:
        print("Failed to get user info")
        print(user_data[1])
        exit(1)

    KITTEN_EXECUTABLE = shutil.which("kitten")
    if not KITTEN_EXECUTABLE:
        print("Kitten not found")
        exit(1)

    image_url = user_data[1]["data"]["User"]["avatar"]["medium"]
    user_name = user_data[1]["data"]["User"]["name"]
    about = user_data[1]["data"]["User"]["about"] or ""
    console.clear()
    image_x = int(console.size.width * 0.1)
    image_y = int(console.size.height * 0.1)
    img_w = console.size.width // 3
    img_h = console.size.height // 3
    image_process = subprocess.run(
        [
            KITTEN_EXECUTABLE,
            "icat",
            "--clear",
            "--place",
            f"{img_w}x{img_h}@{image_x}x{image_y}",
            image_url,
        ],
    )
    if not image_process.returncode == 0:
        print("failed to get image from icat")
        exit(1)
    console.print(
        Panel(
            Markdown(about),
            title=user_name,
        )
    )
