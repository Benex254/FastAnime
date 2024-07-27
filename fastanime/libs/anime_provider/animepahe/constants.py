from yt_dlp.utils.networking import random_user_agent

USER_AGENT = random_user_agent()
ANIMEPAHE = "animepahe.ru"
ANIMEPAHE_BASE = f"https://{ANIMEPAHE}/"
ANIMEPAHE_ENDPOINT = f"{ANIMEPAHE_BASE}/api?"

REQUEST_HEADERS = {
    "Cookie": "__ddgid_=VvX0ebHrH2DsFZo4; __ddgmark_=3savRpSVFhvZcn5x; __ddg2_=buBJ3c4pNBYKFZNp; __ddg1_=rbVADKr9URtt55zoIGFa; SERVERID=janna; XSRF-TOKEN=eyJpdiI6IjV5bFNtd0phUHgvWGJxc25wL0VJSUE9PSIsInZhbHVlIjoicEJTZktlR2hxR2JZTWhnL0JzazlvZU5TQTR2bjBWZ2dDb0RwUXVUUWNSclhQWUhLRStYSmJmWmUxWkpiYkFRYU12RjFWejlSWHorME1wZG5qQ1U0TnFlNnBFR2laQjN1MjdyNjc5TjVPdXdJb2o5VkU1bEduRW9pRHNDTHh6Sy8iLCJtYWMiOiI0OTc0ZmNjY2UwMGJkOWY2MWNkM2NlMjk2ZGMyZGJmMWE0NTdjZTdkNGI2Y2IwNTIzZmFiZWU5ZTE2OTk0YmU4IiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6ImxvdlpqREFnTjdaeFJubUlXQWlJVWc9PSIsInZhbHVlIjoiQnE4R3VHdjZ4M1NDdEVWM1ZqMUxtNnVERnJCcmtCUHZKNzRPR2RFbzNFcStTL29xdnVTbWhsNVRBUXEybVZWNU1UYVlTazFqYlN5UjJva1k4czNGaXBTbkJJK01oTUd3VHRYVHBoc3dGUWxHYnFlS2NJVVNFbTFqMVBWdFpuVUgiLCJtYWMiOiI1NDdjZTVkYmNhNjUwZTMxZmRlZmVmMmRlMGNiYjAwYjlmYjFjY2U0MDc1YTQzZThiMTIxMjJlYTg1NTA4YjBmIiwidGFnIjoiIn0%3D; latest=5592 ",
    "Host": ANIMEPAHE,
    "User-Agent": USER_AGENT,
    "Accept": "application , text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": ANIMEPAHE_BASE,
    "X-Requested-With": "XMLHttpRequest",
    "DNT": "1",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "TE": "trailers",
}
