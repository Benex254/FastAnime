import logging

from requests import get

logger = logging.getLogger(__name__)


def fetch_anime_info_from_bal(anilist_id):
    try:
        url = f"https://raw.githubusercontent.com/bal-mackup/mal-backup/master/anilist/anime/{anilist_id}.json"
        response = get(url, timeout=11)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(e)
