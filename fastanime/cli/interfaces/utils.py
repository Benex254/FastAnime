import concurrent.futures
import logging
import os
import shutil
import subprocess
import textwrap
from threading import Thread

import requests
from yt_dlp.utils import clean_html

from ...constants import APP_CACHE_DIR
from ...libs.anilist.types import AnilistBaseMediaDataSchema
from ...Utility import anilist_data_helper
from ..utils.utils import get_true_fg

logger = logging.getLogger(__name__)

# this script was written by the fzf devs as an example on how to preview images
# its only here for convinience
fzf_preview = r"""
#
# The purpose of this script is to demonstrate how to preview a file or an
# image in the preview window of fzf.
#
# Dependencies:
# - https://github.com/sharkdp/bat
# - https://github.com/hpjansson/chafa
# - https://iterm2.com/utilities/imgcat
fzf-preview(){
    if [[ $# -ne 1 ]]; then
    >&2 echo "usage: $0 FILENAME"
    exit 1
    fi

    file=${1/#\~\//$HOME/}
    type=$(file --dereference --mime -- "$file")

    if [[ ! $type =~ image/ ]]; then
    if [[ $type =~ =binary ]]; then
        file "$1"
        exit
    fi

    # Sometimes bat is installed as batcat.
    if command -v batcat > /dev/null; then
        batname="batcat"
    elif command -v bat > /dev/null; then
        batname="bat"
    else
        cat "$1"
        exit
    fi

    ${batname} --style="${BAT_STYLE:-numbers}" --color=always --pager=never -- "$file"
    exit
    fi

    dim=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}
    if [[ $dim = x ]]; then
    dim=$(stty size < /dev/tty | awk '{print $2 "x" $1}')
    elif ! [[ $KITTY_WINDOW_ID ]] && (( FZF_PREVIEW_TOP + FZF_PREVIEW_LINES == $(stty size < /dev/tty | awk '{print $1}') )); then
    # Avoid scrolling issue when the Sixel image touches the bottom of the screen
    # * https://github.com/junegunn/fzf/issues/2544
    dim=${FZF_PREVIEW_COLUMNS}x$((FZF_PREVIEW_LINES - 1))
    fi

# 1. Use kitty icat on kitty terminal
    if [[ $KITTY_WINDOW_ID ]]; then
    # 1. 'memory' is the fastest option but if you want the image to be scrollable,
    #    you have to use 'stream'.
    #
    # 2. The last line of the output is the ANSI reset code without newline.
    #    This confuses fzf and makes it render scroll offset indicator.
    #    So we remove the last line and append the reset code to its previous line.
    kitty icat --clear --transfer-mode=memory --unicode-placeholder --stdin=no --place="$dim@0x0" "$file" | sed '$d' | sed $'$s/$/\e[m/'

# 2. Use chafa with Sixel output
    elif command -v chafa > /dev/null; then
    chafa -f sixel -s "$dim" "$file"
    # Add a new line character so that fzf can display multiple images in the preview window
    echo

# 3. If chafa is not found but imgcat is available, use it on iTerm2
    elif command -v imgcat > /dev/null; then
    # NOTE: We should use https://iterm2.com/utilities/it2check to check if the
    # user is running iTerm2. But for the sake of simplicity, we just assume
    # that's the case here.
    imgcat -W "${dim%%x*}" -H "${dim##*x}" "$file"

# 4. Cannot find any suitable method to preview the image
    else
    file "$file"
    fi
}
"""


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
    SEPARATOR_WIDTH = 45
    # use concurency to download and write as fast as possible
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {}
        for anime, title in zip(anilist_results, titles):
            # actual image url
            image_url = anime["coverImage"]["large"]
            future_to_task[executor.submit(save_image_from_url, image_url, title)] = (
                image_url
            )

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


def get_fzf_preview(
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
    background_worker.daemon = True
    background_worker.start()

    # the preview script is in bash so making sure fzf doesnt use any other shell lang to process the preview script
    os.environ["SHELL"] = shutil.which("bash") or "bash"
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
