"""
Contains Helper functions to read and write the user data files
"""

from datetime import date, datetime

from kivy.logger import Logger


today = date.today()
now = datetime.now()


# Get the user data
def get_user_anime_list() -> list:
    from .. import user_data

    try:
        return user_data.get("user_anime_list")[
            "user_anime_list"
        ]  # returns a list of anime ids
    except Exception as e:
        Logger.warning(f"User Data:Read failure:{e}")
        return []


def update_user_anime_list(updated_list: list):
    from .. import user_data

    try:
        updated_list_ = list(set(updated_list))
        user_data.put("user_anime_list", user_anime_list=updated_list_)
    except Exception as e:
        Logger.warning(f"User Data:Update failure:{e}")
