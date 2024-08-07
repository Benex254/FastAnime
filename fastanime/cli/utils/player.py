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

    def get_episode(self, type: "Literal['next','previous','reload']"):
        anilist_config = self.anilist_config
        config = self.config
        episode_number: str = anilist_config.episode_number
        quality = config.quality
        episodes: list = sorted(anilist_config.episodes, key=float)
        anime_id: int = anilist_config.anime_id
        anime = anilist_config.anime
        translation_type = config.translation_type
        anime_provider = config.anime_provider

        # next or prev
        if type == "next":
            self.mpv_player.print_text("Fetching next episode")
            next_episode = episodes.index(episode_number) + 1
            if next_episode >= len(episodes):
                next_episode = len(episodes) - 1
            anilist_config.episode_number = episodes[next_episode]
            episode_number = anilist_config.episode_number
            config.update_watch_history(anime_id, episodes[next_episode])
        elif type == "reload":
            episode_number = anilist_config.episode_number
        else:
            self.mpv_player.print_text("Fetching previous episode")
            prev_episode = episodes.index(episode_number) - 1
            if prev_episode <= 0:
                prev_episode = 0
            anilist_config.episode_number = episodes[prev_episode]
            episode_number = anilist_config.episode_number
            config.update_watch_history(anime_id, episodes[prev_episode])
        # update episode progress
        if config.user and episode_number:
            AniList.update_anime_list(
                {
                    "mediaId": anime_id,
                    "progress": episode_number,
                }
            )
        # get them juicy streams
        episode_streams = anime_provider.get_episode_streams(
            anime,
            episode_number,
            translation_type,
            anilist_config.selected_anime_anilist,
        )
        if not episode_streams:
            self.mpv_player.print_text("No streams were found")
            return None

        # always select the first
        selected_server = next(episode_streams)
        self.current_media_title = selected_server["episode_title"]
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
        self.last_stop_time: str = "0"
        self.last_total_time: str = "0"
        self.last_stop_time_secs = 0
        self.last_total_time_secs = 0
        self.current_media_title = ""

        mpv_player = mpv.MPV(
            config=True,
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
        )
        mpv_player.title = title

        @mpv_player.on_key_press("shift+n")
        def _next_episode():
            url = self.get_episode("next")
            if url:
                mpv_player.loadfile(url, options=f"title={self.current_media_title}")
                mpv_player.title = self.current_media_title

        # TODO: select episode from mpv
        #
        # @mpv_player.on_key_press("shift+e")
        # def _episodes():
        # mpv_player
        # url = self.get_episode("next")
        # if url:
        # mpv_player.loadfile(url, options=f"title={self.current_media_title}")
        # mpv_player.title = self.current_media_title

        @mpv_player.on_key_press("shift+p")
        def _previous_episode():
            url = self.get_episode("previous")
            if url:
                mpv_player.loadfile(url, options=f"title={self.current_media_title}")
                mpv_player.title = self.current_media_title

        @mpv_player.on_key_press("shift+a")
        def _toggle_auto_next():
            config.auto_next = not config.auto_next

        @mpv_player.on_key_press("shift+t")
        def _toggle_translation_type():
            config.translation_type = (
                "sub" if config.translation_type == "dub" else "dub"
            )

        @mpv_player.on_key_press("shift+r")
        def _reload():
            url = self.get_episode("reload")
            if url:
                mpv_player.loadfile(url, options=f"title={self.current_media_title}")
                mpv_player.title = self.current_media_title

        @mpv_player.property_observer("time-pos")
        def handle_time_start_update(*args):
            if len(args) > 1:
                value = args[1]
                if value is not None:
                    self.last_stop_time_secs = value
                    self.last_stop_time = format_time(value)

        @mpv_player.property_observer("time-remaining")
        def handle_time_remaining_update(*args):
            if len(args) > 1:
                value = args[1]
                if value is not None:
                    rem_time = value
                    value += self.last_stop_time_secs
                    self.last_total_time = format_time(value)
                    if rem_time < 10 and config.auto_next:
                        url = self.get_episode("next")
                        if url:
                            mpv_player.loadfile(
                                url, options=f"title={self.current_media_title}"
                            )
                            mpv_player.title = self.current_media_title

        # TODO: custom skip functionality based on chapterskip.
        #
        # @mpv_player.property_observer("chapter-number")
        # def chapterskip(_, current_chapter: int):
        # mpv_player
        # chapters = mpv_player..get_property_native("chapter-list")

        # skipped={"1":1}
        # skip = false
        # for i, chapter in enumerate(chapters):
        #     if (not options.skip_once or not skipped[i]) and matches(i, chapter.title):
        #         if i == current_chapter + 1 or skip == i - 1:
        #             if skip:
        #                 skipped[skip] = true
        #             skip = i
        #     elif skip:
        #         mpv_player.set_property("time-pos", chapter.time)
        #         skipped[skip] = true
        #         return
        # if skip:
        #     if mpv_player.get_property_native("playlist-count") == mpv_player.get_property_native("playlist-pos-1"):
        #         return self.mpv_player.set_property("time-pos", mpv_player.get_property_native("duration"))
        #     mpv_player.command("playlist-next")
        #

        mpv_player.observe_property("time-pos", handle_time_start_update)
        mpv_player.observe_property("time-remaining", handle_time_remaining_update)
        # mpv_player.observe_property("chapter-number", chapterskip)
        # mpv_player.register_event("file-loaded", function() skipped = {} end)
        self.mpv_player = mpv_player
        return mpv_player

        # mpv_player.register_event("file-loaded", function() skipped = {} end)
        self.mpv_player = mpv_player
        return mpv_player


player = MpvPlayer()
