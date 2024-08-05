"""
Contains Helper functions to read and write the user data files
"""

import os
from datetime import date, datetime

from kivy.logger import Logger

from kivy.storage.jsonstore import JsonStore

from .. import data_folder

today = date.today()
now = datetime.now()


# TODO:confirm data integrity
if os.path.exists(os.path.join(data_folder, "user_data.json")):
    user_data = JsonStore(os.path.join(data_folder, "user_data.json"))
else:
    user_data_path = os.path.join(data_folder, "user_data.json")
    user_data = JsonStore(user_data_path)


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
