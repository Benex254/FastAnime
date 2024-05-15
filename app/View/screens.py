# The screens dictionary contains the objects of the models and controllers
# of the screens of the application.


from Controller import SearchScreenController,MainScreenController,MyListScreenController
from Model import MainScreenModel,SearchScreenModel,MyListScreenModel

screens = {
    "main screen": {
        "model": MainScreenModel,
        "controller": MainScreenController,
    },
    "search screen": {
        "model": SearchScreenModel,
        "controller": SearchScreenController,
    },
    "my list screen": {
        "model": MyListScreenModel,
        "controller": MyListScreenController,
    },
}