from yt_dlp.utils.networking import random_user_agent

ALLANIME_BASE = "allanime.day"
ALLANIME_REFERER = "https://allanime.to/"
ALLANIME_API_ENDPOINT = "https://api.{}/api/".format(ALLANIME_BASE)
USER_AGENT = random_user_agent()
SERVERS_AVAILABLE = ["sharepoint", "dropbox", "gogoanime", "weTransfer"]
