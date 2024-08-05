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
    "anime screen": {
        "model": AnimeScreenModel,
        "controller": AnimeScreenController,
    },
    "my list screen": {
        "model": MyListScreenModel,
        "controller": MyListScreenController,
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
