from Controller import SearchScreenController,HomeScreenController,MyListScreenController,AnimeScreenController
from Model import HomeScreenModel,SearchScreenModel,MyListScreenModel,AnimeScreenModel


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
}