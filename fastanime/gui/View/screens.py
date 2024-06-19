from ..Controller import (
    AnimeScreenController,
    DownloadsScreenController,
    HomeScreenController,
    MyListScreenController,
    SearchScreenController,
)
from ..Model import (
    AnimeScreenModel,
    DownloadsScreenModel,
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
    "downloads screen": {
        "model": DownloadsScreenModel,
        "controller": DownloadsScreenController,
    },
}
