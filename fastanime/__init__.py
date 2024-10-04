import sys

if sys.version_info < (3, 10):
    raise ImportError(
        "You are using an unsupported version of Python. Only Python versions 3.10 and above are supported by FastAnime"
    )  # noqa: F541


__version__ = "v2.6.2"

APP_NAME = "FastAnime"
AUTHOR = "Benex254"
GIT_REPO = "github.com"
REPO = f"{GIT_REPO}/{AUTHOR}/{APP_NAME}"


def FastAnime():
    from .cli import run_cli

    run_cli()
