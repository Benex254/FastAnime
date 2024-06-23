from ..utils.fzf import fzf
from . import (
    binge_interface,
    bye,
    download_interface,
    info_interface,
    stream_interface,
    watchlist_interface,
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
