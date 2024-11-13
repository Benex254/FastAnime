"""
Just contains some useful data used across the codebase
"""

# useful incases where the anilist title is too different from the provider title
anime_normalizer_raw = {
    "allanime": {
        "1P": "one piece",
        "Magia Record: Mahou Shoujo Madoka☆Magica Gaiden (TV)": "Mahou Shoujo Madoka☆Magica",
        "Dungeon ni Deai o Motomeru no wa Machigatte Iru Darouka": "Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka",
        'Hazurewaku no "Joutai Ijou Skill" de Saikyou ni Natta Ore ga Subete wo Juurin suru made': "Hazure Waku no [Joutai Ijou Skill] de Saikyou ni Natta Ore ga Subete wo Juurin Suru made",
        "Re:Zero kara Hajimeru Isekai Seikatsu Season 3": "Re:Zero kara Hajimeru Isekai Seikatsu 3rd Season",
    },
    "hianime": {"My Star": "Oshi no Ko"},
    "animepahe": {"Azumanga Daiou The Animation": "Azumanga Daioh"},
    "nyaa": {},
    "yugen": {},
}


def get_anime_normalizer():
    """Used because there are different providers"""
    import os

    current_provider = os.environ.get("FASTANIME_PROVIDER", "allanime")
    return anime_normalizer_raw[current_provider]


anime_normalizer = get_anime_normalizer()
