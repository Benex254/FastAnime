from typing import TYPE_CHECKING

import mpv

from ...anilist import AniList
from .utils import filter_by_quality, move_preferred_subtitle_lang_to_top

if TYPE_CHECKING:
    from typing import Literal

    from ...AnimeProvider import AnimeProvider
    from ..config import Config
    from .tools import FastAnimeRuntimeState


def format_time(duration_in_secs: float):
    h = duration_in_secs // 3600
    m = duration_in_secs // 60
    s = duration_in_secs - ((h * 3600) + (m * 60))
    return f"{int(h):2d}:{int(m):2d}:{int(s):2d}".replace(" ", "0")


class MpvPlayer(object):
    anime_provider: "AnimeProvider"
    config: "Config"
    subs = []
    mpv_player: "mpv.MPV"
    last_stop_time: str = "0"
    last_total_time: str = "0"
    last_stop_time_secs = 0
    last_total_time_secs = 0
    current_media_title = ""
    player_fetching = False

    def get_episode(
        self,
        type: "Literal['next','previous','reload','custom']",
        ep_no=None,
        server="top",
    ):
        fastanime_runtime_state = self.fastanime_runtime_state
        config = self.config
        current_episode_number: str = (
            fastanime_runtime_state.provider_current_episode_number
        )
        quality = config.quality
        total_episodes: list = sorted(
            fastanime_runtime_state.provider_available_episodes, key=float
        )
        anime_id_anilist: int = fastanime_runtime_state.selected_anime_id_anilist
        provider_anime = fastanime_runtime_state.provider_anime
        translation_type = config.translation_type
        anime_provider = config.anime_provider
        self.last_stop_time: str = "0"
        self.last_total_time: str = "0"
        self.last_stop_time_secs = 0
        self.last_total_time_secs = 0

        # next or prev
        if type == "next":
            self.mpv_player.show_text("Fetching next episode...")
            next_episode = total_episodes.index(current_episode_number) + 1
            if next_episode >= len(total_episodes):
                next_episode = len(total_episodes) - 1
            fastanime_runtime_state.provider_current_episode_number = total_episodes[
                next_episode
            ]
            current_episode_number = (
                fastanime_runtime_state.provider_current_episode_number
            )
            config.media_list_track(
                anime_id_anilist,
                episode_no=str(current_episode_number),
                progress_tracking=fastanime_runtime_state.progress_tracking,
            )
        elif type == "reload":
            if current_episode_number not in total_episodes:
                self.mpv_player.show_text("Episode not available")
                return
            self.mpv_player.show_text("Replaying Episode...")
        elif type == "custom":
            if not ep_no or ep_no not in total_episodes:
                self.mpv_player.show_text("Episode number not specified or invalid")
                self.mpv_player.show_text(
                    f"Acceptable episodes are:  {total_episodes}",
                )
                return

            self.mpv_player.show_text(f"Fetching episode {ep_no}")
            current_episode_number = ep_no
            config.media_list_track(
                anime_id_anilist,
                episode_no=str(ep_no),
                progress_tracking=fastanime_runtime_state.progress_tracking,
            )
            fastanime_runtime_state.provider_current_episode_number = str(ep_no)
        else:
            self.mpv_player.show_text("Fetching previous episode...")
            prev_episode = total_episodes.index(current_episode_number) - 1
            if prev_episode <= 0:
                prev_episode = 0
            fastanime_runtime_state.provider_current_episode_number = total_episodes[
                prev_episode
            ]
            current_episode_number = (
                fastanime_runtime_state.provider_current_episode_number
            )
            config.media_list_track(
                anime_id_anilist,
                episode_no=str(current_episode_number),
                progress_tracking=fastanime_runtime_state.progress_tracking,
            )
        # update episode progress
        if config.user and current_episode_number:
            AniList.update_anime_list(
                {
                    "mediaId": anime_id_anilist,
                    "progress": int(float(current_episode_number)),
                }
            )
        # get them juicy streams
        episode_streams = anime_provider.get_episode_streams(
            provider_anime["id"],
            current_episode_number,
            translation_type,
        )
        if not episode_streams:
            self.mpv_player.show_text("No streams were found")
            return

        # always select the first
        if server == "top":
            selected_server = next(episode_streams, None)
            if not selected_server:
                self.mpv_player.show_text("Sth went wrong when loading the episode")
                return
        else:
            episode_streams_dict = {
                episode_stream["server"]: episode_stream
                for episode_stream in episode_streams
            }
            selected_server = episode_streams_dict.get(server)
            if selected_server is None:
                self.mpv_player.show_text(
                    f"Invalid server!!; servers available are: {episode_streams_dict.keys()}",
                )
                return
        self.current_media_title = selected_server["episode_title"]
        if config.normalize_titles:
            import re

            for episode_detail in fastanime_runtime_state.selected_anime_anilist[
                "streamingEpisodes"
            ]:
                if re.match(
                    f"Episode {current_episode_number} ", episode_detail["title"]
                ):
                    self.current_media_title = episode_detail["title"]
                    break

        links = selected_server["links"]

        stream_link_ = filter_by_quality(quality, links)
        if not stream_link_:
            self.mpv_player.show_text("Quality not found")
            return
        self.mpv_player._set_property("start", "0")
        stream_link = stream_link_["link"]
        fastanime_runtime_state.provider_current_episode_stream_link = stream_link
        self.subs = move_preferred_subtitle_lang_to_top(
            selected_server["subtitles"], config.sub_lang
        )
        return stream_link

    def create_player(
        self,
        stream_link,
        anime_provider: "AnimeProvider",
        fastanime_runtime_state: "FastAnimeRuntimeState",
        config: "Config",
        title,
        start_time,
        headers={},
        subtitles=[],
    ):
        self.subs = subtitles
        self.anime_provider = anime_provider
        self.fastanime_runtime_state = fastanime_runtime_state
        self.config = config
        self.last_stop_time: str = "0"
        self.last_total_time: str = "0"
        self.last_stop_time_secs = 0
        self.last_total_time_secs = 0
        self.current_media_title = ""

        mpv_player = mpv.MPV(
            log_handler=print,
            loglevel="error",
            config=True,
            input_default_bindings=True,
            input_vo_keyboard=True,
            osc=True,
            ytdl=True,
        )

        # -- events --
        @mpv_player.event_callback("file-loaded")
        def set_total_time(event, *args):
            d = mpv_player._get_property("duration")
            self.player_fetching = False
            if isinstance(d, float):
                self.last_total_time = format_time(d)
            try:
                if not mpv_player.core_shutdown:
                    if self.subs:
                        for i, subtitle in enumerate(self.subs):
                            if i == 0:
                                flag = "select"
                            else:
                                flag = "auto"
                            mpv_player.sub_add(
                                subtitle["url"], flag, None, subtitle["language"]
                            )
                        self.subs = []
            except mpv.ShutdownError:
                pass
            except Exception:
                pass

        @mpv_player.property_observer("time-pos")
        def handle_time_start_update(*args):
            if len(args) > 1:
                value = args[1]
                if value is not None:
                    self.last_stop_time = format_time(value)

        @mpv_player.property_observer("time-remaining")
        def handle_time_remaining_update(
            property, time_remaining: float | None = None, *args
        ):
            if time_remaining is not None:
                if time_remaining < 1 and config.auto_next and not self.player_fetching:
                    print("Auto Fetching Next Episode")
                    self.player_fetching = True
                    url = self.get_episode("next")
                    if url:
                        mpv_player.loadfile(
                            url,
                        )
                        mpv_player.title = self.current_media_title

        # -- keybindings --
        @mpv_player.on_key_press("shift+n")
        def _next_episode():
            url = self.get_episode("next")
            if url:
                mpv_player.loadfile(
                    url,
                )
                mpv_player.title = self.current_media_title

        @mpv_player.on_key_press("shift+p")
        def _previous_episode():
            url = self.get_episode("previous")
            if url:
                mpv_player.loadfile(
                    url,
                )
                mpv_player.title = self.current_media_title

        @mpv_player.on_key_press("shift+a")
        def _toggle_auto_next():
            config.auto_next = not config.auto_next
            if config.auto_next:
                mpv_player.show_text("Auto next enabled")
            else:
                mpv_player.show_text("Auto next disabled")

        @mpv_player.on_key_press("shift+t")
        def _toggle_translation_type():
            translation_type = "sub" if config.translation_type == "dub" else "dub"
            mpv_player.show_text("Changing translation type...")
            anime = anime_provider.get_anime(
                fastanime_runtime_state.provider_anime_search_result["id"],
            )
            if not anime:
                mpv_player.show_text("Failed to update translation type")
                return
            fastanime_runtime_state.provider_available_episodes = anime[
                "availableEpisodesDetail"
            ][translation_type]
            config.translation_type = translation_type

            if config.translation_type == "dub":
                mpv_player.show_text("Translation Type set to dub")
            else:
                mpv_player.show_text("Translation Type set to sub")

        @mpv_player.on_key_press("shift+r")
        def _reload():
            url = self.get_episode("reload")
            if url:
                mpv_player.loadfile(
                    url,
                )
                mpv_player.title = self.current_media_title

        # -- script messages --
        @mpv_player.message_handler("select-episode")
        def select_episode(episode: bytes | None = None, *args):
            if not episode:
                mpv_player.show_text("No episode was selected")
                return
            url = self.get_episode("custom", episode.decode())
            if url:
                mpv_player.loadfile(
                    url,
                )
                mpv_player.title = self.current_media_title

        @mpv_player.message_handler("select-server")
        def select_server(server: bytes | None = None, *args):
            if not server:
                mpv_player.show_text("No server was selected")
                return
            url = self.get_episode("reload", server=server.decode())
            if url:
                mpv_player.loadfile(
                    url,
                )
                mpv_player.title = self.current_media_title
            else:
                pass

        @mpv_player.message_handler("select-quality")
        def select_quality(quality_raw: bytes | None = None, *args):
            if not quality_raw:
                mpv_player.show_text("No quality was selected")
                return
            q = ["360", "720", "1080"]
            quality = quality_raw.decode()
            links: list = fastanime_runtime_state.provider_server_episode_streams
            q = [link["quality"] for link in links]
            if quality in q:
                config.quality = quality
                stream_link_ = filter_by_quality(quality, links)
                if not stream_link_:
                    mpv_player.show_text("Quality not found")
                    return
                mpv_player.show_text(f"Changing to stream of quality {quality}")
                stream_link = stream_link_["link"]
                mpv_player.loadfile(stream_link)
            else:
                mpv_player.show_text(f"invalid quality!! Valid quality includes: {q}")

        # -- events --
        mpv_player.observe_property("time-pos", handle_time_start_update)
        mpv_player.observe_property("time-remaining", handle_time_remaining_update)
        mpv_player.register_event_callback(set_total_time)

        # --script-messages --
        mpv_player.register_message_handler("select-episode", select_episode)
        mpv_player.register_message_handler("select-server", select_server)
        mpv_player.register_message_handler("select-quality", select_quality)

        self.mpv_player = mpv_player
        mpv_player.force_window = config.force_window
        # mpv_player.cache = "yes"
        # mpv_player.cache_pause = "no"
        mpv_player.title = title
        mpv_headers = ""
        if headers:
            for header_name, header_value in headers.items():
                mpv_headers += f"{header_name}:{header_value},"
        mpv_player.http_header_fields = mpv_headers

        mpv_player.play(stream_link)

        if not start_time == "0":
            mpv_player.start = start_time

        mpv_player.wait_for_shutdown()
        mpv_player.terminate()


player = MpvPlayer()
