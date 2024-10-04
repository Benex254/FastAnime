import concurrent.futures
import logging
import os
import shutil
import subprocess
import textwrap
from threading import Thread

import requests
from yt_dlp.utils import clean_html, sanitize_filename

from ...constants import APP_CACHE_DIR,S_PLATFORM
from ...libs.anilist.types import AnilistBaseMediaDataSchema
from ...Utility import anilist_data_helper
from ..utils.scripts import fzf_preview
from ..utils.utils import get_true_fg

logger = logging.getLogger(__name__)


# ---- aniskip intergration ----
def aniskip(mal_id: int, episode: str):
    """helper function to be used for setting and getting skip data

    Args:
        mal_id: mal id of the anime
        episode: episode number

    Returns:
        mpv chapter options
    """
    ANISKIP = shutil.which("ani-skip")
    if not ANISKIP:
        print("Aniskip not found, please install and try again")
        return
    args = [ANISKIP, "-q", str(mal_id), "-e", str(episode)]
    aniskip_result = subprocess.run(args, text=True, stdout=subprocess.PIPE)
    if aniskip_result.returncode != 0:
        return
    mpv_skip_args = aniskip_result.stdout.strip()
    return mpv_skip_args.split(" ")


# ---- prevew stuff ----
# import tempfile

# NOTE: May change this to a temp dir but there were issues so later
WORKING_DIR = APP_CACHE_DIR  # tempfile.gettempdir()

IMAGES_CACHE_DIR = os.path.join(WORKING_DIR, "images")
if not os.path.exists(IMAGES_CACHE_DIR):
    os.mkdir(IMAGES_CACHE_DIR)
ANIME_INFO_CACHE_DIR = os.path.join(WORKING_DIR, "info")
if not os.path.exists(ANIME_INFO_CACHE_DIR):
    os.mkdir(ANIME_INFO_CACHE_DIR)


def save_image_from_url(url: str, file_name: str):
    """Helper function that downloads an image to the FastAnime images cache dir given its url and filename

    Args:
        url: image url to download
        file_name: filename to use
    """
    image = requests.get(url)
    with open(f"{IMAGES_CACHE_DIR}/{file_name}", "wb") as f:
        f.write(image.content)


def save_info_from_str(info: str, file_name: str):
    """Helper function that writes text (anime details and info) to a file given  its filename

    Args:
        info: the information anilist has on the anime
        file_name: the filename to use
    """
    with open(f"{ANIME_INFO_CACHE_DIR}/{file_name}", "w") as f:
        f.write(info)


def write_search_results(
    anilist_results: list[AnilistBaseMediaDataSchema],
    titles: list[str],
    workers: int | None = None,
):
    """A helper function used by and run in a background thread by get_fzf_preview function inorder to get the actual preview data to be displayed by fzf

    Args:
        anilist_results: the anilist results from an anilist action
        titles: sanitized anime titles
        workers:number of threads to use defaults to as many as possible
    """
    # NOTE: Will probably make this a configuraable option
    HEADER_COLOR = 215, 0, 95
    SEPARATOR_COLOR = 208, 208, 208
    SEPARATOR_WIDTH = 30
    # use concurency to download and write as fast as possible
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {}
        for anime, title in zip(anilist_results, titles):
            # actual image url
            image_url = anime["coverImage"]["large"]
            future_to_task[executor.submit(save_image_from_url, image_url, title)] = (
                image_url
            )

            mediaListName = "Not in any of your lists"
            progress = "UNKNOWN"
            if anime_list := anime["mediaListEntry"]:
                mediaListName = anime_list["status"]
                progress = anime_list["progress"]
            # handle the text data
            template = f"""
            {get_true_fg("-"*SEPARATOR_WIDTH,*SEPARATOR_COLOR,bold=False)}
            {get_true_fg('Title(jp):',*HEADER_COLOR)} {anime['title']['romaji']}
            {get_true_fg('Title(eng):',*HEADER_COLOR)} {anime['title']['english']}
            {get_true_fg('Popularity:',*HEADER_COLOR)} {anime['popularity']}
            {get_true_fg('Favourites:',*HEADER_COLOR)} {anime['favourites']}
            {get_true_fg('Status:',*HEADER_COLOR)} {anime['status']}
            {get_true_fg('Episodes:',*HEADER_COLOR)} {anime['episodes']}
            {get_true_fg('Genres:',*HEADER_COLOR)} {anilist_data_helper.format_list_data_with_comma(anime['genres'])}
            {get_true_fg('Next Episode:',*HEADER_COLOR)} {anilist_data_helper.extract_next_airing_episode(anime['nextAiringEpisode'])}
            {get_true_fg('Start Date:',*HEADER_COLOR)} {anilist_data_helper.format_anilist_date_object(anime['startDate'])}
            {get_true_fg('End Date:',*HEADER_COLOR)} {anilist_data_helper.format_anilist_date_object(anime['endDate'])}
            {get_true_fg("-"*SEPARATOR_WIDTH,*SEPARATOR_COLOR,bold=False)}
            {get_true_fg('Media List:',*HEADER_COLOR)} {mediaListName}
            {get_true_fg('Progress:',*HEADER_COLOR)} {progress}
            {get_true_fg("-"*SEPARATOR_WIDTH,*SEPARATOR_COLOR,bold=False)}
            {get_true_fg('Description:',*HEADER_COLOR)}
            """
            template = textwrap.dedent(template)
            template = f"""
            {template}
            {textwrap.fill(clean_html(
                str(anime['description'])), width=45)}
            """
            future_to_task[executor.submit(save_info_from_str, template, title)] = title

        # execute the jobs
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                future.result()
            except Exception as exc:
                logger.error("%r generated an exception: %s" % (task, exc))


# get rofi icons
def get_rofi_icons(
    anilist_results: list[AnilistBaseMediaDataSchema], titles, workers=None
):
    """A helper function to make sure that the images are downloaded so they can be used as icons

    Args:
        titles (list[str]): sanitized titles of the anime; NOTE: its important that they are sanitized since they are used as the filenames of the images
        workers ([TODO:parameter]): Number of threads to use to download the images; defaults to as many as possible
        anilist_results: the anilist results from an anilist action
    """
    # use concurrency to download the images as fast as possible
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # load the jobs
        future_to_url = {}
        for anime, title in zip(anilist_results, titles):
            # actual link to download image from
            image_url = anime["coverImage"]["large"]
            future_to_url[executor.submit(save_image_from_url, image_url, title)] = (
                image_url
            )

        # execute the jobs
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                logger.error("%r generated an exception: %s" % (url, e))


# get rofi icons
def get_fzf_manga_preview(manga_results, workers=None, wait=False):
    """A helper function to make sure that the images are downloaded so they can be used as icons

    Args:
        titles (list[str]): sanitized titles of the anime; NOTE: its important that they are sanitized since they are used as the filenames of the images
        workers ([TODO:parameter]): Number of threads to use to download the images; defaults to as many as possible
        anilist_results: the anilist results from an anilist action
    """

    def _worker():
        # use concurrency to download the images as fast as possible
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # load the jobs
            future_to_url = {}
            for manga in manga_results:
                image_url = manga["poster"]
                future_to_url[
                    executor.submit(
                        save_image_from_url,
                        image_url,
                        sanitize_filename(manga["title"]),
                    )
                ] = image_url

            # execute the jobs
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error("%r generated an exception: %s" % (url, e))

    background_worker = Thread(
        target=_worker,
    )
    # ensure images and info exists
    background_worker.start()

    # the preview script is in bash so making sure fzf doesnt use any other shell lang to process the preview script
    os.environ["SHELL"] = shutil.which("bash") or "bash"
    preview = """
        %s
        if [ -s %s/{} ]; then fzf-preview %s/{}
        else echo Loading...
        fi
    """ % (
        fzf_preview,
        IMAGES_CACHE_DIR,
        IMAGES_CACHE_DIR,
    )
    if wait:
        background_worker.join()
    return preview


# get rofi icons
def get_fzf_episode_preview(
    anilist_result: AnilistBaseMediaDataSchema, episodes, workers=None, wait=False
):
    """A helper function to make sure that the images are downloaded so they can be used as icons

    Args:
        titles (list[str]): sanitized titles of the anime; NOTE: its important that they are sanitized since they are used as the filenames of the images
        workers ([TODO:parameter]): Number of threads to use to download the images; defaults to as many as possible
        anilist_results: the anilist results from an anilist action
    """

    HEADER_COLOR = 215, 0, 95
    import re

    def _worker():
        # use concurrency to download the images as fast as possible
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # load the jobs
            future_to_url = {}
            for episode in episodes:
                episode_title = ""
                image_url = ""
                for episode_detail in anilist_result["streamingEpisodes"]:
                    if re.match(f"Episode {episode} ", episode_detail["title"]):
                        episode_title = episode_detail["title"]
                        image_url = episode_detail["thumbnail"]

                if episode_title and image_url:
                    # actual link to download image from
                    if not image_url:
                        continue
                    future_to_url[
                        executor.submit(save_image_from_url, image_url, episode)
                    ] = image_url
                    template = textwrap.dedent(
                        f"""
                    {get_true_fg('Anime Title:',*HEADER_COLOR)} {anilist_result['title']['romaji'] or anilist_result['title']['english']}
                    {get_true_fg('Episode Title:',*HEADER_COLOR)} {episode_title}
                    """
                    )
                    future_to_url[
                        executor.submit(save_info_from_str, template, episode)
                    ] = episode_title

            # execute the jobs
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error("%r generated an exception: %s" % (url, e))

    background_worker = Thread(
        target=_worker,
    )
    # ensure images and info exists
    background_worker.start()

    # the preview script is in bash so making sure fzf doesnt use any other shell lang to process the preview script
    os.environ["SHELL"] = shutil.which("bash") or "bash"
    if S_PLATFORM == "win32":
        preview = """
            %s
            title={}
            dim=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}
            if [ -s "%s\\\\\\$title" ]; then 
                if command -v "chafa">/dev/null;then
                    chafa -s $dim "%s\\\\\\$title"
                else
                    echo please install chafa to enjoy image previews
                fi
                echo 
            else 
                echo Loading...
            fi
            if [ -s "%s\\\\\\$title" ]; then cat "%s\\\\\\$title"
                else echo Loading...
            fi
        """ % (
            fzf_preview,
            IMAGES_CACHE_DIR.replace("\\", "\\\\\\"),
            IMAGES_CACHE_DIR.replace("\\", "\\\\\\"),
            ANIME_INFO_CACHE_DIR.replace("\\", "\\\\\\"),
            ANIME_INFO_CACHE_DIR.replace("\\", "\\\\\\"),
        )
    else:
        preview = """
            %s
            if [ -s %s/{} ]; then fzf-preview %s/{}
            else echo Loading...
            fi
            if [ -s %s/{} ]; then cat %s/{}
            else echo Loading...
            fi
        """ % (
            fzf_preview,
            IMAGES_CACHE_DIR,
            IMAGES_CACHE_DIR,
            ANIME_INFO_CACHE_DIR,
            ANIME_INFO_CACHE_DIR,
        )
    if wait:
        background_worker.join()
    return preview


def get_fzf_anime_preview(
    anilist_results: list[AnilistBaseMediaDataSchema], titles, wait=False
):
    """A helper function that constructs data to be used for the fzf preview

    Args:
        titles (list[str]): The sanitized titles to use, NOTE: its important that they are sanitized since thay will be used as filenames
        wait (bool): whether to block the ui as we wait for preview defaults to false
        anilist_results: the anilist results got from an anilist action

    Returns:
        THe fzf preview script to use
    """
    # ensure images and info exists

    background_worker = Thread(
        target=write_search_results, args=(anilist_results, titles)
    )
    background_worker.start()

    # the preview script is in bash so making sure fzf doesnt use any other shell lang to process the preview script
    os.environ["SHELL"] = shutil.which("bash") or "bash"
    if S_PLATFORM == "win32":
        preview = """
            %s
            title={}
            dim=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}
            if [ -s "%s\\\\\\$title" ]; then 
                if command -v "chafa">/dev/null;then
                    chafa  -s $dim "%s\\\\\\$title"
                else
                    echo please install chafa to enjoy image previews
                fi
                echo 
            else 
                echo Loading...
            fi
            if [ -s "%s\\\\\\$title" ]; then cat "%s\\\\\\$title"
                else echo Loading...
            fi
        """ % (
            fzf_preview,
            IMAGES_CACHE_DIR.replace("\\", "\\\\\\"),
            IMAGES_CACHE_DIR.replace("\\", "\\\\\\"),
            ANIME_INFO_CACHE_DIR.replace("\\", "\\\\\\"),
            ANIME_INFO_CACHE_DIR.replace("\\", "\\\\\\"),
        )
    else:
        preview = """
            %s
            if [ -s %s/{} ]; then fzf-preview %s/{}
            else echo Loading...
            fi
            if [ -s %s/{} ]; then cat %s/{}
            else echo Loading...
            fi
        """ % (
            fzf_preview,
            IMAGES_CACHE_DIR,
            IMAGES_CACHE_DIR,
            ANIME_INFO_CACHE_DIR,
            ANIME_INFO_CACHE_DIR,
        )
    if wait:
        background_worker.join()
    return preview
