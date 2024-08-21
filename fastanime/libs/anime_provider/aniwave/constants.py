ANIWAVE_BASE = "https://aniwave.to"

SEARCH_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    # 'Accept-Encoding': 'Utf-8',
    "Referer": "https://aniwave.to/filter",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
    "Alt-Used": "aniwave.to",
    # 'Cookie': '__pf=1; usertype=guest; session=BElk9DJdO3sFdDmLiGxuNiM9eGYO1TjktGsmdwjV',
    "Priority": "u=0, i",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}
