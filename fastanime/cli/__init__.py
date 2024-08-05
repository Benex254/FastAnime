import signal

import click

from .. import __version__
from ..libs.anime_provider.allanime.constants import SERVERS_AVAILABLE
from ..Utility.data import anilist_sort_normalizer
from .commands.anilist import anilist
from .commands.config import configure
from .commands.download import download
from .commands.downloads import downloads
from .commands.search import search
from .config import Config

commands = {
    "search": search,
    "download": download,
    "anilist": anilist,
    "config": configure,
    "downloads": downloads,
}


# handle keyboard interupt
def handle_exit(signum, frame):
    from .utils.tools import exit_app
    from .utils.utils import clear

    clear()

    exit_app()


signal.signal(signal.SIGINT, handle_exit)


@click.group(
    commands=commands,
    help="A command line application for streaming anime that provides a complete and featureful interface",
    short_help="Stream Anime",
)
@click.version_option(__version__, "--version")
@click.option(
    "-s",
    "--server",
    type=click.Choice(SERVERS_AVAILABLE, case_sensitive=False),
)
@click.option("-c-h/-no-h", "--continue_h/--no-continue_h", type=bool)
@click.option("-q", "--quality", type=int)
@click.option("-t-t", "--translation_type")
@click.option("-a-n", "--auto-next", type=bool)
@click.option(
    "-s-b",
    "--sort-by",
    type=click.Choice(anilist_sort_normalizer.keys()),  # pyright: ignore
)
@click.option("-d", "--downloads-dir", type=click.Path())
@click.pass_context
def run_cli(
    ctx: click.Context,
    server,
    continue_h,
    translation_type,
    quality,
    auto_next,
    sort_by,
    downloads_dir,
):
    ctx.obj = Config()
    if server:
        ctx.obj.server = server
    if continue_h:
        ctx.obj.continue_from_history = continue_h
    if quality:
        ctx.obj.quality = quality
    if auto_next:
        ctx.obj.auto_next = auto_next
    if sort_by:
        ctx.obj.sort_by = sort_by
    if downloads_dir:
        ctx.obj.downloads_dir = downloads_dir
    if translation_type:
        ctx.obj.translation_type = translation_type
