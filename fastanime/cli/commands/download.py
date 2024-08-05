import click

from ...libs.anime_provider.allanime.api import anime_provider
from ...Utility.downloader.downloader import downloader
from ..config import Config
from ..utils.utils import clear, fuzzy_inquirer


@click.command()
@click.option("--anime-title", prompt="Enter the anime title", required=True)
@click.option("--episode-start", prompt="Enter the episode start", required=True)
@click.option("--episode-end", prompt="Enter the episode end", required=True)
@click.pass_obj
def download(config: Config, anime_title, episode_start, episode_end):
    translation_type = config.translation_type
    download_dir = config.downloads_dir
    quality = config.quality
    search_results = anime_provider.search_for_anime(
        anime_title, translation_type=translation_type
    )

    episodes_to_download = range(int(episode_start), int(episode_end) + 1)
    options = {show["name"]: show for show in search_results["shows"]["edges"]}
    anime = fuzzy_inquirer("Please select the anime:", options.keys())

    anime_data = options[anime]
    availableEpisodesDetail = anime_data["availableEpisodes"]

    episodes = availableEpisodesDetail[translation_type]

    server = config.server
    for episode_number in episodes_to_download:
        if episode_number not in range(episodes):
            print(f"Episode {episode_number} not available")
            continue
        print(f"Downloading episode {episode_number} of {anime_data['name']}")
        episode = anime_provider.get_anime_episode(
            anime_data["_id"], str(episode_number), translation_type
        )

        # get streams for episode from provider
        episode_streams = anime_provider.get_episode_streams(episode)
        episode_streams = {
            episode_stream[0]: episode_stream[1] for episode_stream in episode_streams
        }

        # prompt for preferred server
        if not server or server not in episode_streams.keys():
            server = fuzzy_inquirer("Please select server:", episode_streams.keys())
        print(episode)
        print(episode_streams)
        selected_server = episode_streams[server]

        links = selected_server["links"]
        if quality > len(links) - 1:
            quality = config.quality = len(links) - 1
        elif quality < 0:
            quality = config.quality = 0
        stream_link = links[quality]["link"]

        downloader._download_file(
            stream_link,
            download_dir,
            (anime_data["name"], str(episode_number)),
            lambda *_: "",
            silent=True,
        )
        clear()
