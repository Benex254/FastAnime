import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

if os.environ.get("FA_RICH_TRACEBACK", False):
    from rich.traceback import install

    install(show_locals=True)


# initiate constants
__version__ = "v0.32.0"

APP_NAME = "FastAnime"
AUTHOR = "Benex254"
GIT_REPO = "github.com"
REPO = f"{GIT_REPO}/{AUTHOR}/{APP_NAME}"


def FastAnime():
    if "--update" in sys.argv:
        from .Utility.app_updater import update_app

        update_app()
        sys.argv.remove("--update")
    if "--log" in sys.argv:
        # Configure logging
        from rich.logging import RichHandler

        logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level to DEBUG
            format="%(message)s",  # Use a simple message format
            datefmt="[%X]",  # Use a custom date format
            handlers=[RichHandler()],  # Use RichHandler to format the logs
        )
        sys.argv.remove("--log")
    if "--log-file" in sys.argv:
        # Configure logging
        from rich.logging import RichHandler

        from .constants import NOTIFIER_LOG_FILE_PATH

        logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level to DEBUG
            format="%(asctime)s%(levelname)s: %(message)s",  # Use a simple message format
            datefmt="[%d/%m/%Y@%H:%M:%S]",  # Use a custom date format
            filename=NOTIFIER_LOG_FILE_PATH,
            filemode="a",  # Use RichHandler to format the logs
        )
        sys.argv.remove("--log-file")

    from .cli import run_cli

    run_cli()
