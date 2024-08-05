from ..Controller.anime_screen import AnimeScreenController
from ..Controller.downloads_screen import DownloadsScreenController
from ..Controller.home_screen import HomeScreenController
from ..Controller.my_list_screen import MyListScreenController
from ..Controller.search_screen import SearchScreenController
from ..Model.anime_screen import AnimeScreenModel
from ..Model.download_screen import DownloadsScreenModel
from ..Model.home_screen import HomeScreenModel
from ..Model.my_list_screen import MyListScreenModel
from ..Model.search_screen import SearchScreenModel

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
