import re

SERVERS_AVAILABLE = [
    "sharepoint",
    "dropbox",
    "gogoanime",
    "weTransfer",
    "wixmp",
    "Yt",
    "mp4-upload",
]
API_BASE_URL = "allanime.day"
API_REFERER = "https://allanime.to/"
API_ENDPOINT = f"https://api.{API_BASE_URL}/api/"

# search constants
DEFAULT_COUNTRY_OF_ORIGIN = "all"
DEFAULT_NSFW = True
DEFAULT_UNKNOWN = True
DEFAULT_PER_PAGE = 40
DEFAULT_PAGE = 1

# regex stuff

MP4_SERVER_JUICY_STREAM_REGEX = re.compile(
    r"video/mp4\",src:\"(https?://.*/video\.mp4)\""
)
