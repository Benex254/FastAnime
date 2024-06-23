from ...utils.fzf import fzf
from ....libs.anilist.anilist_data_schema import (
    AnilistDataSchema,
    AnilistBaseMediaDataSchema,
)


def get_search_result(
    anilist_data: AnilistDataSchema,
) -> AnilistBaseMediaDataSchema | None:
    choices = []
    data = anilist_data["data"]["Page"]["media"]
    for choice in data:
        choices.append(choice["title"]["romaji"])
    _selected_anime = fzf(choices)
    if not _selected_anime:
        return None

    def _get_result(x):
        return x["title"]["romaji"] == _selected_anime

    selected_anime = list(filter(_get_result, data))
    if not selected_anime:
        return None
    return selected_anime[0]
