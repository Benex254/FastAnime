"""
Just contains some useful data used across the codebase
"""

# useful incases where the anilist title is too different from the provider title
anime_normalizer = {
    "1P": "one piece",
    "Magia Record: Mahou Shoujo Madoka☆Magica Gaiden (TV)": "Mahou Shoujo Madoka☆Magica",
    "Dungeon ni Deai o Motomeru no wa Machigatte Iru Darouka": "Dungeon ni Deai wo Motomeru no wa Machigatteiru Darou ka",
    'Hazurewaku no "Joutai Ijou Skill" de Saikyou ni Natta Ore ga Subete wo Juurin suru made': "Hazure Waku no [Joutai Ijou Skill] de Saikyou ni Natta Ore ga Subete wo Juurin Suru made",
}


anilist_sort_normalizer = {"search match": "SEARCH_MATCH"}
