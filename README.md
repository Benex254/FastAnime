# FastAnime

Welcome to **FastAnime**, anime site experience from the terminal.

![fastanime-demo](https://github.com/user-attachments/assets/16e29f54-e9fa-48c7-b944-bfacb31ae1b5)

<details>
<summary><b>fzf mode</b></summary>
  
[fa_fzf_demo.webm](https://github.com/user-attachments/assets/b1fecf25-e358-4e8b-a144-bcb7947210cf)

</details>

<details>
<summary><b>rofi mode</b></summary>

[fa_rofi_mode.webm](https://github.com/user-attachments/assets/2ce669bf-b62f-4c44-bd79-cf0dcaddf37a)

</details>

<details>
<summary><b>Default mode</b></summary>
  
[fa_default_mode.webm](https://github.com/user-attachments/assets/1ce3a23d-f4a0-4bc1-8518-426ec7b3b69e)

</details>

Heavily inspired by [animdl](https://github.com/justfoolingaround/animdl), [jerry](https://github.com/justchokingaround/jerry/tree/main),[magic-tape](https://gitlab.com/christosangel/magic-tape/-/tree/main?ref_type=heads) and [ani-cli](https://github.com/pystardust/ani-cli).

<!--toc:start-->

- [FastAnime](#fastanime)
  - [Installation](#installation)
    - [Installation using your favourite package manager](#installation-using-your-favourite-package-manager)
      - [Using pipx](#using-pipx)
      - [Using pip](#using-pip)
    - [Installing the bleeding edge version](#installing-the-bleeding-edge-version)
    - [Building from the source](#building-from-the-source)
    - [External Dependencies](#external-dependencies)
  - [Usage](#usage)
    - [The Commandline interface :fire:](#the-commandline-interface-fire)
      - [The anilist command :fire: :fire: :fire:](#the-anilist-command-fire-fire-fire)
        - [Running without any subcommand](#running-without-any-subcommand)
        - [Subcommands](#subcommands)
      - [download subcommand](#download-subcommand)
      - [search subcommand](#search-subcommand)
      - [grab subcommand](#grab-subcommand)
      - [downloads subcommand](#downloads-subcommand)
      - [config subcommand](#config-subcommand)
      - [cache subcommand](#cache-subcommand)
      - [update subcommand](#update-subcommand)
      - [completions subcommand](#completions-subcommand)
    - [MPV specific commands](#mpv-specific-commands)
      - [Key Bindings](#key-bindings)
      - [Script Messages](#script-messages)
  - [styling the default interface](#styling-the-default-interface)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [Receiving Support](#receiving-support)
  - [Supporting the Project](#supporting-the-project)
  <!--toc:end-->

> [!IMPORTANT]
>
> This project currently scrapes allanime, aniwatch and animepahe. The site is in the public domain and can be accessed by any one with a browser.

## Installation

The app can run wherever python can run. So all you need to have is python installed on your device.
On android you can use [termux](https://github.com/termux/termux-app).
If you have any difficulty consult for help on the [discord channel](https://discord.gg/HBEmAwvbHV)

### Installation using your favourite package manager

Currently the app is only published on [pypi](https://pypi.org/project/fastanime/).

#### Using pipx

Preferred method of installation since [Pipx](https://github.com/pypa/pipx) creates an isolated environment for each app it installs.

```bash

pipx install fastanime
# -- or for the development version --
pipx install 'fastanime==<latest-pre-release-tag>.dev1'
# example
# pipx install 'fastanime==0.60.1.dev1'

```

#### Using pip

```bash
pip install fastanime
# -- or for the development version --
pip install 'fastanime==<latest-pre-release-tag>.dev1'
# example
# pip install 'fastanime==0.60.1.dev1'
```

### Installing the bleeding edge version

To install the latest build which are created on every push by GitHub actions, download the [fastanime_debug_build](https://github.com/Benex254/FastAnime/actions) of your choosing from the GitHub actions page.
Then:

```bash
unzip fastanime_debug_build

# outputs fastanime<version>.tar.gz

pipx install fastanime<version>.tar.gz

# --- or ---

pip install fastanime<version>.tar.gz
```

### Building from the source

Requirements:

- [git](https://git-scm.com/)
- [python 3.10 and above](https://www.python.org/)
- [poetry](https://python-poetry.org/docs/#installation)

To build from the source, follow these steps:

1. Clone the repository: `git clone https://github.com/Benex254/FastAnime.git --depth 1`
2. Navigate into the folder: `cd FastAnime`
3. Then build and Install the app:

```bash
# Normal Installation
poetry build
cd dist
pip install fastanime<version>.whl

# Editable installation (easiest for updates)
# just do a git pull in the Project dir
# the latter will require rebuilding the app
pip install -e .
```

4. Enjoy! Verify installation with:

```bash
fastanime --version
```

> [!Tip]
>
> Download the completions from [here](https://github.com/Benex254/FastAnime/tree/master/completions) for your shell.
> To add completions:
>
> - Fish Users: `cp $FASTANIME_PATH/completions/fastanime.fish ~/.config/fish/completions/`
> - Bash Users: Add `source $FASTANIME_PATH/completions/fastanime.bash` to your `.bashrc`
> - Zsh Users: Add `source $FASTANIME_PATH/completions/fastanime.zsh` to your `.zshrc`

### External Dependencies

The only required external dependency, unless you won't be streaming, is [MPV](https://mpv.io/installation/), which i recommend installing with [uosc](https://github.com/tomasklaen/uosc) :fire: and [thumbfast](https://github.com/po5/thumbfast) for the best experience since they add a better interface to it.

> [!NOTE]
>
> The project currently sees no reason to support any other video
> player because we believe nothing beats **MPV** and it provides
> everything you could ever need with a small footprint.
> But if you have a reason feel free to encourage as to do so.

**Other external dependencies that will just make your experience better:**

- [ffmpeg](https://www.ffmpeg.org/) is required to be in your path environment variables to properly download [hls](https://www.cloudflare.com/en-gb/learning/video/what-is-http-live-streaming/) streams.
- [fzf](https://github.com/junegunn/fzf) 🔥 which is used as a better alternative to the ui.
- [rofi](https://github.com/davatorium/rofi) 🔥 which is used as another alternative ui + the the desktop entry ui
- [chafa](https://github.com/hpjansson/chafa) currently the best cross platform and cross terminal image viewer for the terminal.
- [icat](https://sw.kovidgoyal.net/kitty/kittens/icat/) an image viewer that only works in [kitty terminal](https://sw.kovidgoyal.net/kitty/), which is currently the best terminal in my opinion, and by far the best image renderer for the terminal thanks to kitty's terminal graphics protocol. Its terminal graphics is so op that you can [run a browser on it](https://github.com/chase/awrit?tab=readme-ov-file)!!
- [bash](https://www.gnu.org/software/bash/) is used as the preview script language.
- [ani-skip](https://github.com/synacktraa/ani-skip) used for skipping the opening and ending theme songs
- [ffmpegthumbnailer](https://github.com/dirkvdb/ffmpegthumbnailer) used for local previews of downloaded anime
- [syncplay](https://syncplay.pl/) to enable watch together.
- [feh]() used in manga mode

## Usage

The project offers a featureful command-line interface and MPV interface through the use of python-mpv.
The project also offers subs in different languages thanks to aniwatch provider.

### The Commandline interface :fire:

Designed for efficiency and automation. Plus has a beautiful pseudo-TUI in some of the commands.

**Overview of main commands:**

- `fastanime anilist`: Powerful command for browsing and exploring anime due to AniList integration.
- `fastanime download`: Download anime.
- `fastanime search`: Powerful command meant for binging since it doesn't require the interfaces
- `fastanime downloads`: View downloaded anime and watch with MPV.
- `fastanime config`: Quickly edit configuration settings.
- `fastanime cache`: Quickly manage the cache fastanime uses
- `fastanime update`: Quickly update fastanime
- `fastanime grab`: print streams to stdout to use in non python application.

**Overview of options**

Most options are directly passed into fastanime directly and are shared by multiple subcommands.

Most of the options override your config file.

This is a convention to make the dev time faster since it reduces redundancy and also makes switching of subcommands with the same options easier to the end user.

In general `fastanime --<option-name>`

Available options for the fastanime include:

- `--server <server>` or `-s <server>` set the default server to auto select
- `--continue/--no-continue` or `-c/-no-c` whether to continue from the last episode you were watching
- `--local-history/--remote-history` whether to use remote or local history defaults to local
- `--quality <1080/720/480/360>` or `-q <1080/720/480/360>` the link to choose from server
- `--translation-type <dub/sub>` or `-t <dub/sub>` what language for anime
- `--dub` dubbed anime
- `--sub` subbed anime
- `--auto-select/--no-auto-select` or `-a/-no-a` auto select title from provider results
- `--auto-next/--no-auto-next` or `-A/-no-A` auto select next episode
- `-downloads-dir <path>` or `-d <path>` set the folder to download anime into
- `--fzf` use fzf for the ui
- `--default` use the default ui
- `--preview` show a preview when using fzf
- `--no-preview` dont show a preview when using fzf
- `--format <yt-dlp format string>` or `-f <yt-dlp format string>` set the format of anime downloaded and streamed based on [yt-dlp format](https://github.com/yt-dlp/yt-dlp#format-selection). Works when `--server gogoanime` or on providers that provide multi quality streams eg aniwatch
- `--icons/--no-icons` toggle the visibility of the icons
- `--skip/--no-skip` whether to skip the opening and ending theme songs.
- `--rofi` use rofi for the ui
- `--rofi-theme <path>` theme to use with rofi
- `--rofi-theme-input <path>` theme to use with rofi input
- `--rofi-theme-confirm <path>` theme to use with rofi confirm
- `--log` allow logging to stdout
- `--log-file` allow logging to a file
- `--rich-traceback` allow rich traceback
- `--use-mpv-mod/--use-default-player` whether to use python-mpv
- `--provider <allanime/animepahe>` anime site of choice to scrape from
- `--sync-play` or `-sp` use syncplay for streaming anime so you can watch with your friends
- `--sub-lang <en/or any other common shortform for country>` regex is used to determine the appropriate. Only works when provider is aniwatch.
- `--normalize-titles/--no-normalize-titles` whether to normalize provider titles
- `--manga` toggle experimental manga mode

Example usage of the above options

```bash
# example of syncplay intergration
fastanime --sync-play --server sharepoint search -t <anime-title>

# --- or ---

# to watch with anilist intergration
fastanime --sync-play --server sharepoint anilist

# downloading dubbed anime
fastanime --dub download -t <anime>

# use  icons and fzf for a more elegant ui with preview
fastanime --icons --preview --fzf anilist

# use icons with default ui
fastanime --icons --default anilist

# viewing manga
fastanime --manga search -t <manga-title>
```

#### The anilist command :fire: :fire: :fire:

Stream, browse, and discover anime efficiently from the terminal using the [AniList API](https://github.com/AniList/ApiV2-GraphQL-Docs).

##### Running without any subcommand

Run `fastanime anilist` to access the main interface.

##### Subcommands

The subcommands are mainly their as convenience. Since all the features already exist in the main interface.
Most of the subcommands share the common option `--dump-json` or `-d` which will print only the json data and suppress the ui.

- `fastanime anilist trending`: Top 15 trending anime.
- `fastanime anilist recent`: Top 15 recently updated anime.
- `fastanime anilist search`: Search for anime (top 50 results).
- `fastanime anilist upcoming`: Top 15 upcoming anime.
- `fastanime anilist popular`: Top 15 popular anime.
- `fastanime anilist favourites`: Top 15 favorite anime.
- `fastanime anilist random`: get random anime

**FastAnime Anilist Search subcommand** 🔥 🔥 🔥

It is by far one of the most powerful commands.
It offers the following options:

- `--sort <MediaSort>` or `-s <MediaSort>`
- `--title <anime-title>` or `-t <anime-title>`
- `--tags <tag>` or `-T <tag>` can be specified multiple times for different tags to filter by.
- `--year <year>` or `-y <year>`
- `--status <MediaStatus>` or `-S <MediaStatus>` can be specified multiple times
- `--media-format <MediaFormat>` or `-f <MediaFormat>`
- `--season <MediaSeason>`
- `--genres <genre>` or `-g <genre>` can be specified multiple times.
- `--on-list/--not-on-list`

Example:

```bash
# get anime with the tag of isekai
fastanime anilist search -T isekai

# get anime of 2024 and sort by popularity
# that has already finished airing or is releasing
# and is not in your anime lists
fastanime anilist search -y 2024 -s POPULARITY_DESC --status RELEASING --status FINISHED --not-on-list

# get anime of 2024 season WINTER
fastanime anilist search -y 2024 --season WINTER

# get anime genre action and tag isekai,magic
 fastanime anilist search -g Action -T Isekai -T Magic

# get anime of 2024 thats finished airing
fastanime anilist search -y 2024 -S FINISHED

# get the most favourite anime movies
fastanime anilist search -f MOVIE -s FAVOURITES_DESC
```

For more details visit the anilist docs or just get the completions which will improve the experience.

Like seriously **[get the completions](https://github.com/Benex254/FastAnime#completions-subcommand)** and the experience will be a 💯 💯 better.

The following are commands you can only run if you are signed in to your AniList account:

- `fastanime anilist watching`
- `fastanime anilist planning`
- `fastanime anilist rewatching`
- `fastanime anilist dropped`
- `fastanime anilist paused`
- `fastanime anilist completed`

Plus: `fastanime anilist notifier` 🔥

```bash
# basic form
fastanime anilist notifier

# with logging to stdout
fastanime --log anilist notifier

# with logging to a file. stored in the same place as your config
fastanime --log-file anilist notifier
```

The above commands will start a loop that checks every 2 minutes if any of the anime in your watch list that are airing has just released a new episode.

The notification will consist of a cover image of the anime in none windows systems.

You can place the command among your machines startup scripts.

For fish users for example you can decide to put this in your `~/.config/fish/config.fish`:

```fish
if ! ps aux | grep -q '[f]astanime .* notifier'
  echo initializing fastanime anilist notifier
  nohup fastanime --log-file anilist notifier>/dev/null &
end
```

> [!NOTE]
> To sign in just run `fastanime anilist login` and follow the instructions.
> To view your login status `fastanime anilist login --status`
> To erase login data `fastanime anilist login --erase`

#### download subcommand

Download anime to watch later dub or sub with this one command.
Its optimized for scripting due to fuzzy matching; basically you don't have to manually select search results.

So every step of the way has been and can be automated.
Uses a list slicing syntax similar to that of python as the value for the `-r` option.

> [!NOTE]
>
> The download feature is powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) so all the bells and whistles that it provides are readily available in the project.
> Like continuing from where you left of while downloading, after lets say you lost your internet connection.

**Syntax:**

```bash
# Download all available episodes
# multiple titles can be specified with -t option
fastanime download -t <anime-title> -t <anime-title>
# -- or --
fastanime download -t <anime-title> -t <anime-title> -r ':'

# download latest episode for the two anime titles
# the number can be any no of latest episodes but a minus sign
# must be present
fastanime download -t <anime-title> -t <anime-title> -r '-1'

# latest 5
fastanime download -t <anime-title> -t <anime-title> -r '-5'

# Download specific episode range
# be sure to observe the range Syntax
fastanime download -t <anime-title> -r '<episodes-start>:<episodes-end>:<step>'

fastanime download -t <anime-title> -r '<episodes-start>:<episodes-end>'

fastanime download -t <anime-title> -r '<episodes-start>:'

fastanime download -t <anime-title> -r ':<episodes-end>'

# download specific episode
# remember python indexing starts at 0
fastanime download -t <anime-title> -r '<episode-1>:<episode>'

# merge subtitles with ffmpeg to mkv format; aniwatch tends to give subs as separate files
# and dont prompt for anything
# eg existing file in destination instead remove
# and clean
# ie remove original files (sub file and vid file)
# only keep merged files
fastanime download -t <anime-title> --merge --clean --no-prompt

# EOF is used since -t always expects a title
# you can supply anime titles from file or -t at the same time
#
# from stdin
echo -e "<anime-title>\n<anime-title>\n<anime-title>" | fastanime download -t "EOF" -r <range> -f -

# from file
fastanime download -t "EOF" -r <range> -f <file-path>


```

#### search subcommand

Powerful command mainly aimed at binging anime. Since it doesn't require interaction with the interfaces.

Uses a list slicing syntax similar to that of python as the value of the `-r` option.

**Syntax:**

```bash
# basic form where you will still be prompted for the episode number
# multiple titles can be specified with the -t option
fastanime search -t <anime-title> -t <anime-title>

# binge all episodes with this command
fastanime search -t <anime-title> -r ':'

# watch latest episode
fastanime search -t <anime-title> -r '-1'

# binge a specific episode range with this command
# be sure to observe the range Syntax
fastanime search -t <anime-title> -r '<start>:<stop>'

fastanime search -t <anime-title> -r '<start>:<stop>:<step>'

fastanime search -t <anime-title> -r '<start>:'

fastanime search -t <anime-title> -r ':<end>'
```

#### grab subcommand

Helper command to print streams to stdout so it can be used by non-python applications.

The format of the printed out data is json and can be either an array or object depending on how many anime titles have been specified in the command-line or through a subprocess.

> [!TIP]
> For python applications just use its python api, for even greater and easier control.
> So just add fastanime as one of your dependencies.

Uses a list slicing syntax similar to that of python as the value of the `-r` option.

**Syntax:**

```bash
# --- print anime info + episode streams ---

# multiple titles can be specified with the -t option
fastanime grab -t <anime-title> -t <anime-title>

# -- or --

# print all available episodes
fastanime grab -t <anime-title> -r ':'

# print the latest episode
fastanime grab -t <anime-title> -r '-1'

# print a specific episode range
# be sure to observe the range Syntax
fastanime grab -t <anime-title> -r '<start>:<stop>'

fastanime grab -t <anime-title> -r '<start>:<stop>:<step>'

fastanime grab -t <anime-title> -r '<start>:'

fastanime grab -t <anime-title> -r ':<end>'

# --- grab options ---

# print search results only
fastanime grab -t <anime-title> -r <range> --search-results-only

# print anime info only
fastanime grab -t <anime-title> -r <range> --anime-info-only

# print episode streams only
fastanime grab -t <anime-title> -r <range> --episode-streams-only

```

#### downloads subcommand

View and stream the anime you downloaded using MPV.

**Syntax:**

```bash
fastanime downloads

# view individual episodes
fastanime downloads --view-episodes
# --- or ---
fastanime downloads -v

# to set seek time when using ffmpegthumbnailer for local previews
# -1 means random and is the default
fastanime downloads --time-to-seek <intRange(-1,100)>
# --- or ---
fastanime downloads -t <intRange(-1,100)>

# to watch a specific title
# be sure to get the completions for the best experience
fastanime downloads --title <title>

# to get the path to the downloads folder set
fastanime downloads --path
# useful when you want to use the value for other programs

```

#### config subcommand

Edit FastAnime configuration settings using your preferred editor (based on `$EDITOR` environment variable so be sure to set it).

**Syntax:**

```bash
fastanime config

# to get config path which is useful if you want to use it for another program.
fastanime config --path

# add a desktop entry
fastanime config --desktop-entry

# view current contents of your configuration or can be used to get an example config
fastanime config --view
```

> [!Note]
>
> If it opens [vim](https://www.vim.org/download.php) you can exit by typing `:q` .

#### cache subcommand

Easily manage the data fastanime has cached; for the previews.

**Syntax:**

```bash
# delete everything in the cache dir
fastanime cache --clean

# print the path to the cache dir and exit
fastanime cache --path

# print the current size of the cache dir and exit
fastanime cache --size

# open the cache dir and exit
fastanime cache
```

#### update subcommand

Easily update fastanime to latest

**Syntax:**

```bash
# update fastanime to latest
fastanime update

# check for latest release
fastanime update --check
```

#### completions subcommand

Helper command to setup shell completions

**Syntax:**

```bash
# try to detect your shell and print completions
fastanime completions
# print fish completions
fastanime completions --fish
# print bash completions
fastanime completions --bash
# print zsh completions
fastanime completions --zsh
```

### MPV specific commands

The project now allows on the fly media controls directly from mpv. This means you can go to the next or previous episode without the window ever closing thus offering a seamless experience.
This is all powered with [python-mpv]() which enables writing mpv scripts with python just like how it would be done in lua.

#### Key Bindings

`<shift>+n` fetch the next episode

`<shift>+p` fetch the previous episode

`<shift>+t` toggle the translation type from dub to sub

`<shift>+a` toggle auto next episode

`<shit>+r` reload episode

#### Script Messages

Commands issued in the MPV console.

Examples:

```bash
# to select episode from mpv without window closing
script-message select-episode <episode-number>

# to select server from mpv without window closing
script-message select-server <server-name>

# to select quality
script-message select-quality <1080/720/480/360>
```

## styling the default interface

The default interface uses inquirerPy which is customizable. Read here to findout more <https://inquirerpy.readthedocs.io/en/latest/pages/env.html>

## Configuration

The app includes sensible defaults but can be customized extensively. Configuration is stored in `.ini` format at `~/.config/FastAnime/config.ini` on arch linux; for the other operating systems you can check by running `fastanime config --path`.


> [!TIP]
> You can now use the option `--update` to update your config file from the command-line
> For Example:
> `fastanime --icons --fzf --preview config --update` 
> the above will set icons to true, use_fzf to true and preview to true in your config file
>


The default config:

```ini
#
#    ███████╗░█████╗░░██████╗████████╗░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ░█████╗░░█████╗░███╗░░██╗███████╗██╗░██████╗░
#    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗████╗░██║██║████╗░████║██╔════╝  ██╔══██╗██╔══██╗████╗░██║██╔════╝██║██╔════╝░
#    █████╗░░███████║╚█████╗░░░░██║░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░  ██║░░╚═╝██║░░██║██╔██╗██║█████╗░░██║██║░░██╗░
#    ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░  ██║░░██╗██║░░██║██║╚████║██╔══╝░░██║██║░░╚██╗
#    ██║░░░░░██║░░██║██████╔╝░░░██║░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗  ╚█████╔╝╚█████╔╝██║░╚███║██║░░░░░██║╚██████╔╝
#    ╚═╝░░░░░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝  ░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝░╚═════╝░
#
[general]
# whether to show the icons in the tui [True/False]
# more like emojis
# by the way if you have any recommendations to which should be used where please
# don't hesitate to share your opinion
# cause it's a lot of work to look for the right one for each menu option
# be sure to also give the replacement emoji
icons = False

# the quality of the stream [1080,720,480,360]
# this option is usually only reliable when:
# provider=animepahe
# since it provides links that actually point to streams of different qualities
# while the rest just point to another link that can provide the anime from the same server
quality = 1080

# whether to normalize provider titles [True/False]
# basically takes the provider titles and finds the corresponding anilist title then changes the title to that
# useful for uniformity especially when downloading from different providers
# this also applies to episode titles
normalize_titles = True

# can be [allanime, animepahe, aniwatch]
# allanime is the most realible
# animepahe provides different links to streams of different quality so a quality can be selected reliably with --quality option
# aniwatch which is now hianime usually provides subs in different languuages and its servers are generally faster
provider = allanime

# Display language [english, romaji]
# this is passed to anilist directly and is used to set the language which the anime titles will be in
# when using the anilist interface
preferred_language = english

# Download directory
# where you will find your videos after downloading them with 'fastanime download' command
downloads_dir = ~/Videos/FastAnime

# whether to show a preview window when using fzf or rofi [True/False]
# the preview requires you have a commandline image viewer as documented in the README
# this is only when usinf fzf
# if you dont care about image previews it doesnt matter
# though its awesome
# try it and you will see
preview = False 

# the time to seek when using ffmpegthumbnailer [-1 to 100]
# -1 means random and is the default
# ffmpegthumbnailer is used to generate previews and you can select at what time in the video to extract an image
# random makes things quite exciting cause you never no at what time it will extract the image from
ffmpegthumbnailer_seek_time = -1

# whether to use fzf as the interface for the anilist command and others. [True/False]
use_fzf = False 

# whether to use rofi for the ui [True/False]
# it's more useful if you want to create a desktop entry 
# which can be setup with 'fastanime config --desktop-entry'
# though if you want it to be your sole interface even when fastanime is run directly from the terminal
use_rofi = False

# rofi themes to use 
# the values of this option is the path to the rofi config files to use
# i choose to split it into three since it gives the best look and feel
# you can refer to the rofi demo on github to see for your self
# by the way i recommend getting the rofi themes from this project;  
rofi_theme = 

rofi_theme_input = 

rofi_theme_confirm = 

# the duration in minutes a notification will stay in the screen
# used by notifier command
notification_duration = 2

# used when the provider gives subs of different languages
# currently its the case for:
# aniwatch
# the values for this option are the short names for countries
# regex is used to determine what you selected
sub_lang = eng


[stream]
# Auto continue from watch history [True/False]
# this will make fastanime to choose the episode that you last watched to completion
# and increment it by one
# and use that to auto select the episode you want to watch
continue_from_history = True  

# which history to use [local/remote]
# local history means it will just use the watch history stored locally in your device 
# the file that stores it is called watch_history.json and is stored next to your config file
# remote means it ignores the last episode stored locally and instead uses the one in your anilist anime list
# this config option is useful if you want to overwrite your local history or import history covered from another device or platform
# since remote history will take precendence over whats available locally
preferred_history = local

# Preferred language for anime [dub/sub]
translation_type = sub

# what server to use for a particular provider
# allanime: [dropbox, sharepoint, wetransfer, gogoanime, wixmp]
# animepahe: [kwik]
# aniwatch: [HD1, HD2, StreamSB, StreamTape]
# 'top' can also be used as a value for this option
# 'top' will cause fastanime to auto select the first server it sees
# this saves on resources and is faster since not all servers are being fetched
server = top

# Auto select next episode [True/False]
# this makes fastanime increment the current episode number 
# then after using that value to fetch the next episode instead of prompting
# this option is useful for binging
auto_next = False

# Auto select the anime provider results with fuzzy find. [True/False]
# Note this won't always be correct
# this is because the providers sometime use non-standard names
# that are there own preference rather than the official names
# But 99% of the time will be accurate
# if this happens just turn of auto_select in the menus or from the commandline and manually select the correct anime title
# and then please open an issue at <> highlighting the normalized title and the title given by the provider for the anime you wished to watch  
# or even better edit this file <> and open a pull request
auto_select = True

# whether to skip the opening and ending theme songs [True/False]
# NOTE: requires ani-skip to be in path
# for python-mpv users am planning to create this functionality n python without the use of an external script
# so its disabled for now
skip = False

# the maximum delta time in minutes after which the episode should be considered as completed
# used in the continue from time stamp
error = 3

# whether to use python-mpv [True/False]
# to enable superior control over the player 
# adding more options to it
# Enable this one and you will be wonder why you did not discover fastanime sooner 
# Since you basically don't have to close the player window to go to the next or previous episode, switch servers, change translation type or 
change to a given episode x
# so try it if you haven't already
# if you have any issues setting it up 
# don't be afraid to ask
# especially on windows
# honestly it can be a pain to set it up there
# personally it took me quite sometime to figure it out
# this is because of how windows handles shared libraries
# so just ask when you find yourself stuck
# or just switch to arch linux
use_python_mpv = False

# force mpv window
# the default 'immediate' just makes mpv to open the window even if the video has not yet loaded
# done for asthetics
# passed directly to mpv so values are same
force_window = immediate

# the format of downloaded anime and trailer
# based on yt-dlp format and passed directly to it
# learn more by looking it up on their site
# only works for downloaded anime if: 
# provider=allanime, server=gogoanime
# provider=allanime, server=wixmp
# provider=aniwatch
# this is because they provider a m3u8 file that contans multiple quality streams
format = best[height<=1080]/bestvideo[height<=1080]+bestaudio/best

# NOTE:
# if you have any trouble setting up your config
# please don't be afraid to ask in our discord
# plus if there are any errors, improvements or suggestions please tell us in the discord
# or help us by contributing
# we appreciate all the help we can get
# since we may not always have the time to immediately implement the changes
#
# HOPE YOU ENJOY FASTANIME AND BE SURE TO STAR THE PROJECT ON GITHUB
#
```

## Contributing

We welcome your issues and feature requests. However, due to time constraints, we currently do not plan to add another provider.

If you wish to contribute directly, please first open an issue describing your proposed changes so it can be discussed or if you are in a rush for the feature to be merged just open a pr.

If you find an anime title that does not correspond with a provider or is just weird just [edit the data file](https://github.com/Benex254/FastAnime/blob/master/fastanime/Utility/data.py) and open a pr or if you don't want to do that open an issue.

## Receiving Support

For inquiries, join our [Discord Server](https://discord.gg/HBEmAwvbHV).

<p align="center">
<a href="https://discord.gg/HBEmAwvbHV">
<img src="https://invidget.switchblade.xyz/C4rhMA4mmK">
</a>
</p>

## Supporting the Project

Show your support by starring our GitHub repository or [buying us a coffee](https://ko-fi.com/benex254).
