from Controller import (
    SearchScreenController,
    HomeScreenController,
    MyListScreenController,
    AnimeScreenController,
    DownloadsScreenController,
    HelpScreenController,
    CrashLogScreenController,
)
from Model import (
    HomeScreenModel,
    SearchScreenModel,
    MyListScreenModel,
    AnimeScreenModel,
    DownloadsScreenModel,
    HelpScreenModel,
    CrashLogScreenModel,
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
