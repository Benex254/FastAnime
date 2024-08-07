from typing import TYPE_CHECKING

import mpv

from ...anilist import AniList

if TYPE_CHECKING:
    from typing import Literal

    from ...AnimeProvider import AnimeProvider
    from ..config import Config


def format_time(duration_in_secs: float):
    h = duration_in_secs // 3600
    m = duration_in_secs // 60
    s = duration_in_secs - ((h * 3600) + (m * 60))
    return f"{int(h):2d}:{int(m):2d}:{int(s):2d}".replace(" ", "0")


class MpvPlayer(object):
    anime_provider: "AnimeProvider"
    config: "Config"
    mpv_player: "mpv.MPV"
    last_stop_time: str = "0"
    last_total_time: str = "0"
    last_stop_time_secs = 0
    last_total_time_secs = 0
    current_media_title = ""

    def get_episode(self, type: "Literal['next','previous']"):
        anilist_config = self.anilist_config
        config = self.config
        episode_number: str = anilist_config.episode_number
        quality = config.quality
        episodes: list = sorted(anilist_config.episodes, key=float)
        anime_id: int = anilist_config.anime_id
        anime = anilist_config.anime
        translation_type = config.translation_type
        anime_provider = config.anime_provider

        if type == "next":
            next_episode = episodes.index(episode_number) + 1
            if next_episode >= len(episodes):
                next_episode = len(episodes) - 1
            anilist_config.episode_number = episodes[next_episode]
            episode_number = anilist_config.episode_number
            config.update_watch_history(anime_id, episodes[next_episode])
        else:
            prev_episode = episodes.index(episode_number) - 1
            if prev_episode <= 0:
                prev_episode = 0
            anilist_config.episode_number = episodes[prev_episode]
            episode_number = anilist_config.episode_number
            config.update_watch_history(anime_id, episodes[prev_episode])
        if config.user and episode_number:
            AniList.update_anime_list(
                {
                    "mediaId": anime_id,
                    "progress": episode_number,
                }
            )
        episode_streams = anime_provider.get_episode_streams(
            anime,
            episode_number,
            translation_type,
            anilist_config.selected_anime_anilist,
        )
        if not episode_streams:
            self.mpv_player.print_text("No streams were found")
            return None

        selected_server = next(episode_streams)
        self.current_media_title = selected_server["episode_title"]
        self.mpv_player.script_message(f"{self.current_media_title}")
        links = selected_server["links"]
        if quality > len(links) - 1:
            quality = config.quality = len(links) - 1
        elif quality < 0:
            quality = config.quality = 0
        stream_link = links[quality]["link"]
        return stream_link

    def create_player(
        self, anime_provider: "AnimeProvider", anilist_config, config: "Config", title
    ):
        self.anime_provider = anime_provider
        self.anilist_config = anilist_config
        self.config = config
        mpv_player = mpv.MPV(
            config=True,
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
            ytdl=True,
        )
        mpv_player.title = title

        @mpv_player.on_key_press("shift+n")
        def _next_episode():
            url = self.get_episode("next")
            if url:
                mpv_player.loadfile(url, options=f"title={self.current_media_title}")
                mpv_player.title = self.current_media_title

        @mpv_player.on_key_press("shift+p")
        def _previous_episode():
            url = self.get_episode("previous")
            if url:
                mpv_player.loadfile(url, options=f"title={self.current_media_title}")
                mpv_player.title = self.current_media_title

        @mpv_player.property_observer("time-pos")
        def handle_time_start_update(*args):
            if len(args) > 1:
                value = args[1]
                if value is not None:
                    self.last_stop_time = format_time(value)

        @mpv_player.property_observer("time-remaining")
        def handle_time_remaining_update(*args):
            if len(args) > 1:
                value = args[1]
                if value is not None:
                    self.last_total_time = format_time(value)

        mpv_player.observe_property("time-pos", handle_time_start_update)
        mpv_player.observe_property("time-remaining", handle_time_remaining_update)
        self.mpv_player = mpv_player
        return mpv_player


player = MpvPlayer()
