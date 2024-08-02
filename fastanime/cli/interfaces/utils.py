import concurrent.futures
import logging
import os
import shutil
import subprocess
import textwrap
from threading import Thread

import requests

from ...constants import APP_CACHE_DIR
from ...libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ...Utility import anilist_data_helper
from ...Utility.utils import remove_html_tags, sanitize_filename
from ..config import Config
from ..utils.utils import get_true_fg

logger = logging.getLogger(__name__)

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
def aniskip(mal_id, episode):
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

WORKING_DIR = APP_CACHE_DIR  # tempfile.gettempdir()
IMAGES_DIR = os.path.join(WORKING_DIR, "images")
if not os.path.exists(IMAGES_DIR):
    os.mkdir(IMAGES_DIR)
INFO_DIR = os.path.join(WORKING_DIR, "info")
if not os.path.exists(INFO_DIR):
    os.mkdir(INFO_DIR)


def save_image_from_url(url: str, file_name: str):
    image = requests.get(url)
    with open(f"{IMAGES_DIR}/{file_name}", "wb") as f:
        f.write(image.content)


def save_info_from_str(info: str, file_name: str):
    with open(f"{INFO_DIR}/{file_name}", "w") as f:
        f.write(info)


def write_search_results(
    search_results: list[AnilistBaseMediaDataSchema], config: Config, workers=None
):
    H_COLOR = 215, 0, 95
    S_COLOR = 208, 208, 208
    S_WIDTH = 45
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {}
        for anime in search_results:
            anime_title = (
                anime["title"][config.preferred_language] or anime["title"]["romaji"]
            )
            anime_title = sanitize_filename(anime_title)
            image_url = anime["coverImage"]["large"]
            future_to_task[
                executor.submit(save_image_from_url, image_url, anime_title)
            ] = image_url

            # handle the text data
            template = f"""
            {get_true_fg("-"*S_WIDTH,*S_COLOR,bold=False)}
            {get_true_fg('Title(jp):',*H_COLOR)} {anime['title']['romaji']}
            {get_true_fg('Title(eng):',*H_COLOR)} {anime['title']['english']}
            {get_true_fg('Popularity:',*H_COLOR)} {anime['popularity']}
            {get_true_fg('Favourites:',*H_COLOR)} {anime['favourites']}
            {get_true_fg('Status:',*H_COLOR)} {anime['status']}
            {get_true_fg('Episodes:',*H_COLOR)} {anime['episodes']}
            {get_true_fg('Genres:',*H_COLOR)} {anilist_data_helper.format_list_data_with_comma(anime['genres'])}
            {get_true_fg('Next Episode:',*H_COLOR)} {anilist_data_helper.extract_next_airing_episode(anime['nextAiringEpisode'])}
            {get_true_fg('Start Date:',*H_COLOR)} {anilist_data_helper.format_anilist_date_object(anime['startDate'])}
            {get_true_fg('End Date:',*H_COLOR)} {anilist_data_helper.format_anilist_date_object(anime['endDate'])}
            {get_true_fg("-"*S_WIDTH,*S_COLOR,bold=False)}
            {get_true_fg('Description:',*H_COLOR)}
            """
            template = textwrap.dedent(template)
            template = f"""
            {template}
            {textwrap.fill(remove_html_tags(
                str(anime['description'])), width=45)}
            """
            future_to_task[
                executor.submit(save_info_from_str, template, anime_title)
            ] = anime_title

        # execute the jobs
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                future.result()
            except Exception as exc:
                logger.error("%r generated an exception: %s" % (task, exc))


# get rofi icons
def get_icons(search_results: list[AnilistBaseMediaDataSchema], config, workers=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        # load the jobs
        future_to_url = {}
        for anime in search_results:
            anime_title = (
                anime["title"][config.preferred_language] or anime["title"]["romaji"]
            )
            anime_title = sanitize_filename(anime_title)
            image_url = anime["coverImage"]["large"]
            future_to_url[
                executor.submit(save_image_from_url, image_url, anime_title)
            ] = image_url

        # execute the jobs
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as exc:
                logger.error("%r generated an exception: %s" % (url, exc))


def get_preview(
    search_results: list[AnilistBaseMediaDataSchema], config: Config, wait=False
):
    # ensure images and info exists
    background_worker = Thread(
        target=write_search_results, args=(search_results, config)
    )
    background_worker.daemon = True
    background_worker.start()

    os.environ["SHELL"] = shutil.which("bash") or "sh"
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
        IMAGES_DIR,
        IMAGES_DIR,
        INFO_DIR,
        INFO_DIR,
    )
    # preview.replace("\n", ";")
    if wait:
        background_worker.join()
    return preview
