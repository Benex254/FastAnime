import os
import shutil

from ... import APP_CACHE_DIR
from ...libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ...Utility import anilist_data_helper
from ...Utility.utils import remove_html_tags, sanitize_filename
from ..config import Config

fzf_preview = """
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


SEARCH_RESULTS_CACHE = os.path.join(APP_CACHE_DIR, "search_results")


def write_search_results(
    search_results: list[AnilistBaseMediaDataSchema], config: Config
):
    import textwrap

    import requests

    for anime in search_results:
        if not os.path.exists(SEARCH_RESULTS_CACHE):
            os.mkdir(SEARCH_RESULTS_CACHE)
        anime_title = (
            anime["title"][config.preferred_language] or anime["title"]["romaji"]
        )
        anime_title = sanitize_filename(anime_title)
        ANIME_CACHE = os.path.join(SEARCH_RESULTS_CACHE, anime_title)
        if not os.path.exists(ANIME_CACHE):
            os.mkdir(ANIME_CACHE)
        with open(
            f"{ANIME_CACHE}/image",
            "wb",
        ) as f:
            try:
                image = requests.get(anime["coverImage"]["large"], timeout=5)
                f.write(image.content)
            except Exception:
                pass

        with open(f"{ANIME_CACHE}/data", "w") as f:
            # data = json.dumps(anime, sort_keys=True, indent=2, separators=(',', ': '))
            template = f"""
            {"-"*40}
            Anime Title(jp): {anime['title']['romaji']}
            Anime Title(eng): {anime['title']['english']}
            {"-"*40}
            Popularity: {anime['popularity']}
            Favourites: {anime['favourites']}
            Status: {anime['status']}
            Episodes: {anime['episodes']}
            Genres: {anilist_data_helper.format_list_data_with_comma(anime['genres'])}
            Next Episode: {anilist_data_helper.extract_next_airing_episode(anime['nextAiringEpisode'])}
            Start Date: {anilist_data_helper.format_anilist_date_object(anime['startDate'])}
            End Date: {anilist_data_helper.format_anilist_date_object(anime['endDate'])}
            {"-"*40}
            Description:
            """
            template = textwrap.dedent(template)
            template = f"""
            {template}
            {textwrap.fill(remove_html_tags(str(anime['description'])),width=45)}
            """
            f.write(template)


def get_preview(search_results: list[AnilistBaseMediaDataSchema], config: Config):
    from threading import Thread

    background_worker = Thread(
        target=write_search_results, args=(search_results, config)
    )
    background_worker.daemon = True
    background_worker.start()

    os.environ["SHELL"] = shutil.which("bash") or "bash"
    preview = """
        %s
        if [ -s %s/{}/image ]; then fzf-preview %s/{}/image
        else echo Loading...
        fi
        if [ -s %s/{}/data ]; then cat %s/{}/data
        else echo Loading...
        fi
    """ % (
        fzf_preview,
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
    )
    # preview.replace("\n", ";")
    return preview
