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
    help="Server of choice",
)
@click.option(
    "-c/-no-c",
    "--continue/--no-continue",
    "continue_",
    type=bool,
    help="Continue from last episode?",
)
@click.option(
    "-q",
    "--quality",
    type=click.IntRange(0, 3),
    help="set the quality of the stream",
)
@click.option(
    "-t",
    "--translation_type",
    type=click.Choice(["dub", "sub"]),
    help="Anime language[dub/sub]",
)
@click.option(
    "-A/-no-A",
    "--auto-next/--no-auto-next",
    type=bool,
    help="Auto select next episode?",
)
@click.option(
    "-a/-no-a",
    "--auto-select/--no-auto-select",
    type=bool,
    help="Auto select anime title?",
)
@click.option(
    "-S",
    "--sort-by",
    type=click.Choice(anilist_sort_normalizer.keys()),  # pyright: ignore
)
@click.option("-d", "--downloads-dir", type=click.Path(), help="Downloads location")
@click.option("--fzf", is_flag=True, help="Use fzf for the ui")
@click.option("--default", is_flag=True, help="Use the default interface")
@click.option("--preview", is_flag=True, help="Show preview when using fzf")
@click.option("--no-preview", is_flag=True, help="Dont show preview when using fzf")
@click.pass_context
def run_cli(
    ctx: click.Context,
    server,
    continue_,
    translation_type,
    quality,
    auto_next,
    auto_select,
    sort_by,
    downloads_dir,
    fzf,
    default,
    preview,
    no_preview,
):
    ctx.obj = Config()
    if server:
        ctx.obj.server = server
    if ctx.get_parameter_source("continue_") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.continue_from_history = continue_
    if quality:
        ctx.obj.quality = quality
    if ctx.get_parameter_source("auto-next") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.auto_next = auto_next
    if (
        ctx.get_parameter_source("auto_select")
        == click.core.ParameterSource.COMMANDLINE
    ):
        ctx.obj.auto_select = auto_select
    if sort_by:
        ctx.obj.sort_by = sort_by
    if downloads_dir:
        ctx.obj.downloads_dir = downloads_dir
    if translation_type:
        ctx.obj.translation_type = translation_type
    if fzf:
        ctx.obj.use_fzf = True
    if default:
        ctx.obj.use_fzf = False
    if preview:
        ctx.obj.preview = True
    if no_preview:
        ctx.obj.preview = False
