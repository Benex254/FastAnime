from ..Controller import (
    AnimeScreenController,
    CrashLogScreenController,
    DownloadsScreenController,
    HelpScreenController,
    HomeScreenController,
    MyListScreenController,
    SearchScreenController,
)
from ..Model import (
    AnimeScreenModel,
    CrashLogScreenModel,
    DownloadsScreenModel,
    HelpScreenModel,
    HomeScreenModel,
    MyListScreenModel,
    SearchScreenModel,
)

screens = {
    "home screen": {
        "model": HomeScreenModel,
        "controller": HomeScreenController,
    },
    "search screen": {
        "model": SearchScreenModel,
        "controller": SearchScreenController,
    },
    "my list screen": {
        "model": MyListScreenModel,
        "controller": MyListScreenController,
    },
    "anime screen": {
        "model": AnimeScreenModel,
        "controller": AnimeScreenController,
    },
    "crashlog screen": {
        "model": CrashLogScreenModel,
        "controller": CrashLogScreenController,
    },
    "downloads screen": {
        "model": DownloadsScreenModel,
        "controller": DownloadsScreenController,
    },
    "help screen": {
        "model": HelpScreenModel,
        "controller": HelpScreenController,
    },
}
