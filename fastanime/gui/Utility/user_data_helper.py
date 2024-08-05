"""
Contains Helper functions to read and write the user data files
"""

from datetime import date, datetime

from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore

from ... import USER_DATA_PATH

today = date.today()
now = datetime.now()

user_data = JsonStore(USER_DATA_PATH)


# Get the user data
def get_user_anime_list() -> list:
    try:
        return user_data.get("user_anime_list")[
            "user_anime_list"
        ]  # returns a list of anime ids
    except Exception as e:
        Logger.warning(f"User Data:Read failure:{e}")
        return []


def update_user_anime_list(updated_list: list):
    try:
        updated_list_ = list(set(updated_list))
        user_data.put("user_anime_list", user_anime_list=updated_list_)
    except Exception as e:
        Logger.warning(f"User Data:Update failure:{e}")
