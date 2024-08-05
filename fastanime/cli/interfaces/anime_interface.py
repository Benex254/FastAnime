import rich
from ..utils.fzf import fzf
from . import (
    info_interface,
    stream_interface,
    binge_interface,
    download_interface,
    watchlist_interface,
    bye,
)

options = {
    "info": info_interface,
    "stream": stream_interface,
    "binge": binge_interface,
    "download": download_interface,
    "watchlist": watchlist_interface,
    "quit": bye,
}


def anime_interface(anime):
    command = fzf(options.keys())
    if command:
        options[command](anime, options)
