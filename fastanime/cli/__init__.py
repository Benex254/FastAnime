import signal

import click

from .. import __version__
from ..libs.anime_provider import anime_sources
from ..libs.anime_provider.allanime.constants import SERVERS_AVAILABLE
from ..Utility.data import anilist_sort_normalizer
from .commands import LazyGroup

commands = {
    "search": "search.search",
    "download": "download.download",
    "anilist": "anilist.anilist",
    "config": "config.config",
    "downloads": "downloads.downloads",
    "cache": "cache.cache",
}


# handle keyboard interupt
def handle_exit(signum, frame):
    from click import clear

    from .utils.tools import exit_app

    clear()

    exit_app()


signal.signal(signal.SIGINT, handle_exit)


@click.group(
    lazy_subcommands=commands,
    cls=LazyGroup,
    help="A command line application for streaming anime that provides a complete and featureful interface",
    short_help="Stream Anime",
)
@click.version_option(__version__, "--version")
@click.option("--log", help="Allow logging to stdout", is_flag=True)
@click.option("--log-file", help="Allow logging to a file", is_flag=True)
@click.option("--rich-traceback", help="Use rich to output tracebacks", is_flag=True)
@click.option("--update", help="Update fastanime to the latest version", is_flag=True)
@click.option(
    "-p",
    "--provider",
    type=click.Choice(list(anime_sources.keys()), case_sensitive=False),
    help="Provider of your choice",
)
@click.option(
    "-s",
    "--server",
    type=click.Choice([*SERVERS_AVAILABLE, "top"], case_sensitive=False),
    help="Server of choice",
)
@click.option(
    "-f",
    "--format",
    type=str,
    help="yt-dlp format to use",
)
@click.option(
    "-c/-no-c",
    "--continue/--no-continue",
    "continue_",
    type=bool,
    help="Continue from last episode?",
)
@click.option(
    "--skip/--no-skip",
    type=bool,
    help="Skip opening and ending theme songs?",
)
@click.option(
    "-q",
    "--quality",
    type=click.IntRange(0, 3),
    help="set the quality of the stream",
)
@click.option(
    "-t",
    "--translation-type",
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
@click.option(
    "--icons/--no-icons",
    type=bool,
    help="Use icons in the interfaces",
)
@click.option("--dub", help="Set the translation type to dub", is_flag=True)
@click.option("--sub", help="Set the translation type to sub", is_flag=True)
@click.option("--rofi", help="Use rofi for the ui", is_flag=True)
@click.option("--rofi-theme", help="Rofi theme to use", type=click.Path())
@click.option(
    "--rofi-theme-confirm",
    help="Rofi theme to use for the confirm prompt",
    type=click.Path(),
)
@click.option(
    "--rofi-theme-input",
    help="Rofi theme to use for the user input prompt",
    type=click.Path(),
)
@click.pass_context
def run_cli(
    ctx: click.Context,
    log,
    log_file,
    rich_traceback,
    update,
    provider,
    server,
    format,
    continue_,
    skip,
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
    icons,
    dub,
    sub,
    rofi,
    rofi_theme,
    rofi_theme_confirm,
    rofi_theme_input,
):
    from .config import Config

    ctx.obj = Config()
    if log:
        import logging

        from rich.logging import RichHandler

        FORMAT = "%(message)s"

        logging.basicConfig(
            level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
        )
        logger = logging.getLogger(__name__)
        logger.info("logging has been initialized")
    elif log_file:
        import logging

        from ..constants import NOTIFIER_LOG_FILE_PATH

        format = "%(asctime)s%(levelname)s: %(message)s"
        logging.basicConfig(
            level=logging.DEBUG,
            filename=NOTIFIER_LOG_FILE_PATH,
            format=format,
            datefmt="[%d/%m/%Y@%H:%M:%S]",
            filemode="w",
        )
    if rich_traceback:
        from rich.traceback import install

        install()
    if update and None:
        from .app_updater import update_app

        update_app()
        return

    if provider:
        ctx.obj.provider = provider
        ctx.obj.load_config()
    if server:
        ctx.obj.server = server
    if format:
        ctx.obj.format = format
    if ctx.get_parameter_source("continue_") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.continue_from_history = continue_
    if ctx.get_parameter_source("skip") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.skip = skip

    if quality:
        ctx.obj.quality = quality
    if ctx.get_parameter_source("auto_next") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.auto_next = auto_next
    if ctx.get_parameter_source("icons") == click.core.ParameterSource.COMMANDLINE:
        ctx.obj.icons = icons
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
    if dub:
        ctx.obj.translation_type = "dub"
    if sub:
        ctx.obj.translation_type = "sub"
    if rofi:
        ctx.obj.use_fzf = False
        ctx.obj.use_rofi = True
    if rofi:
        from ..libs.rofi import Rofi

        if rofi_theme:
            ctx.obj.rofi_theme = rofi_theme
            Rofi.rofi_theme = rofi_theme

        if rofi_theme_input:
            ctx.obj.rofi_theme_input = rofi_theme_input
            Rofi.rofi_theme_input = rofi_theme_input

        if rofi_theme_confirm:
            ctx.obj.rofi_theme_confirm = rofi_theme_confirm
            Rofi.rofi_theme_confirm = rofi_theme_confirm
