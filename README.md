# FastAnime

Welcome to **FastAnime**, anime site experience from the terminal.

[fa_demo.webm](https://github.com/user-attachments/assets/bb46642c-176e-42b3-a533-ff55d4dac111)

Heavily inspired by [animdl](https://github.com/justfoolingaround/animdl), [magic-tape](https://gitlab.com/christosangel/magic-tape/-/tree/main?ref_type=heads) and [ani-cli](https://github.com/pystardust/ani-cli).

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
      - [The anilist command](#the-anilist-command)
        - [Running without any subcommand](#running-without-any-subcommand)
        - [Subcommands](#subcommands)
      - [download subcommand](#download-subcommand)
      - [search subcommand](#search-subcommand)
      - [downloads subcommand](#downloads-subcommand)
      - [config subcommand](#config-subcommand)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [Receiving Support](#receiving-support)
  - [Supporting the Project](#supporting-the-project)
  <!--toc:end-->

> [!IMPORTANT]
>
> This project currently scrapes allanime and is in no way related to them. The site is in the public domain and can be access by any one with a browser.

> [!NOTE]
>
> The docs are still being worked on and are far from completion.

## Installation

The app can run wherever python can run. So all you need to have is python installed on your device.
On android you can use [termux](https://github.com/termux/termux-app).
If you have any difficulty consult for help on the [discord channel](https://discord.gg/HRjySFjQ)

### Installation using your favourite package manager

Currently the app is only published on [pypi](https://pypi.org/project/fastanime/).
The app is published approximately after every 14 days, which will include accumulative changes during that period.

#### Using pipx

Preferred method of installation since [Pipx](https://github.com/pypa/pipx) creates an isolated environment for each app it installs.

```bash

pipx install fastanime
```

#### Using pip

```bash
pip install fastanime
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

1. Clone the repository: `git clone https://github.com/Benex254/FastAnime.git`
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

The only required external dependency, unless you won't be streaming, is [MPV](https://mpv.io/installation/), which i recommend installing with [uosc](https://github.com/tomasklaen/uosc) and [thumbfast](https://github.com/po5/thumbfast) for the best experience since they add a better interface to it.

> [!NOTE]
>
> The project currently sees no reason to support any other video
> player because we believe nothing beats **MPV** and it provides
> everything you could ever need with a small footprint.
> But if you have a reason feel free to encourage as to do so.

**Other dependencies that will just make your experience better:**

- [fzf](https://github.com/junegunn/fzf) :fire: which is used as a better alternative to the ui.
- [chafa](https://github.com/hpjansson/chafa) currently the best cross platform and cross terminal image viewer for the terminal.
- [icat](https://sw.kovidgoyal.net/kitty/kittens/icat/) an image viewer that only works in [kitty terminal](https://sw.kovidgoyal.net/kitty/), which is currently the best terminal in my opinion, and by far the best image renderer for the terminal thanks to kitty's terminal graphics protocol. Its terminal graphics is so op that you can [run a browser on it](https://github.com/chase/awrit?tab=readme-ov-file)!!
- [bash](https://www.gnu.org/software/bash/) is used as the preview script language.
- [ani-skip](https://github.com/synacktraa/ani-skip) :fire: used for skipping the opening and ending theme songs

## Usage

The app offers both a graphical interface (under development) and a robust command-line interface.

> [!NOTE]
>
> The GUI is mostly in hiatus; use the CLI for now.
> However, you can try it out before i decided to change my objective by checking out this [release](https://github.com/Benex254/FastAnime/tree/v0.20.0).
> But be reassured for those who aren't terminal chads, i will still complete the GUI for the fun of it

### The Commandline interface :fire:

Designed for power users who prefer efficiency over browser-based streaming and still want the experience in their terminal.

Overview of main commands:

- `fastanime anilist`: Powerful command for browsing and exploring anime due to AniList integration.
- `fastanime download`: Download anime.
- `fastanime search`: Powerful command meant for binging since it doesn't require the interfaces
- `fastanime downloads`: View downloaded anime and watch with MPV.
- `fastanime config`: Quickly edit configuration settings.

Configuration is directly passed into this command at run time to override your config.

Available options include:

- `--server;-s <server>` set the default server to auto select
- `--continue;-c/--no-continue;-no-c` whether to continue from the last episode you were watching
- `--quality;-q <0|1|2|3>` the link to choose from server
- `--translation-type;- <dub|sub` what language for anime
- `--auto-select;-a/--no-auto-select;-no-a` auto select title from provider results
- `--auto-next;-A;/--no-auto-next;-no-A` auto select next episode
- `-downloads-dir;-d <path>` set the folder to download anime into
- `--fzf` use fzf for the ui
- `--default` use the default ui
- `--preview` show a preview when using fzf
- `--no-preview` dont show a preview when using fzf
- `--format <yt-dlp format string>` set the format of anime downloaded and streamed based on yt-dlp format. Works when `--server gogoanime`
- `--icons/--no-icons` toggle the visibility of the icons
- `--skip/--no-skip` whether to skip the opening and ending theme songs.
- `--rofi` use rofi for the ui
- `--rofi-theme <path>` theme to use with rofi
- `--rofi-theme-input <path>` theme to use with rofi input
- `--rofi-theme-confirm <path>` theme to use with rofi confirm

#### The anilist command :fire: :fire: :fire:

Stream, browse, and discover anime efficiently from the terminal using the [AniList API](https://github.com/AniList/ApiV2-GraphQL-Docs).

##### Running without any subcommand

Run `fastanime anilist` to access the main interface.

##### Subcommands

The subcommands are mainly their as convenience. Since all the features already exist in the main interface.

- `fastanime anilist trending`: Top 15 trending anime.
- `fastanime anilist recent`: Top 15 recently updated anime.
- `fastanime anilist search`: Search for anime (top 50 results).
- `fastanime anilist upcoming`: Top 15 upcoming anime.
- `fastanime anilist popular`: Top 15 popular anime.
- `fastanime anilist favourites`: Top 15 favorite anime.
- `fastanime anilist random`: get random anime

The following are commands you can only run if you are signed in to your AniList account:

- `fastanime anilist watching`
- `fastanime anilist planning`
- `fastanime anilist rewatching`
- `fastanime anilist dropped`
- `fastanime anilist paused`
- `fastanime anilist completed`

Plus: `fastanime anilist notifier` :fire:

```bash
# basic form
fastanime anilist notifier

# with logging to stdout
fastanime --log anilist notifier

# with logging to a file. stored in the same place as your config
fastanime --log-file anilist notifier
```

The above commands will start a loop that checks every 2 minutes if any of the anime in your watch list that are aireing has just released a new episode.

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

#### download subcommand

Download anime to watch later dub or sub with this one command.
Its optimized for scripting due to fuzzy matching.
So every step of the way has been and can be automated.

> [!NOTE]
>
> The download feature is powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp) so all the bells and whistles that it provides are readily available in the project.
> Like continuing from where you left of while downloading, after lets say you lost your internet connection.

**Syntax:**

```bash
# Download all available episodes
fastanime download <anime-title>

# Download specific episode range
# be sure to observe the range Syntax
fastanime download <anime-title> -r <episodes-start>-<episodes-end>
```

#### search subcommand

Powerful command mainly aimed at binging anime. Since it doesn't require interaction with the interfaces.

**Syntax:**

```bash
# basic form where you will still be promted for the episode number
fastanime search <anime-title>

# binge all episodes with this command
fastanime search <anime-title> -

# binge a specific episode range with this command
# be sure to observe the range Syntax
fastanime search <anime-title> <episodes-start>-<episodes-end>
```

#### downloads subcommand

View and stream the anime you downloaded using MPV.

**Syntax:**

```bash
fastanime downloads

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
```

> [!Note]
>
> If it opens [vim](https://www.vim.org/download.php) you can exit by typing `:q` in case you don't know.

## Configuration

The app includes sensible defaults but can be customized extensively. Configuration is stored in `.ini` format at `~/.config/FastAnime/config.ini` on Linux and mac or somewhere on windows; you can check by running `fastanime config --path`.

```ini
[stream]
continue_from_history = True  # Auto continue from watch history
translation_type = sub  # Preferred language for anime (options: dub, sub)
server = top  # Default server (options: dropbox, sharepoint, wetransfer.gogoanime, top, wixmp)
auto_next = False  # Auto-select next episode
# Auto select the anime provider results with fuzzy find.
# Note this wont always be correct.But 99% of the time will be.
auto_select=True
# whether to skip the opening and ending theme songs
# note requires ani-skip to be in path
skip=false
# the maximum delta time in minutes after which the episode should be considered as completed
# used in the continue from time stamp
error=3

# the format of downloaded anime and trailer
# based on yt-dlp format and passed directly to it
# learn more by looking it up on their site
# only works for downloaded anime if server=gogoanime
# since its the only one that offers different formats
# the others tend not to
format=best[height<=1080]/bestvideo[height<=1080]+bestaudio/best # default

[general]
preferred_language = romaji  # Display language (options: english, romaji)
downloads_dir = <Default-videos-dir>/FastAnime  # Download directory
preview=false # whether to show a preview window when using fzf or rofi

use_fzf=False # whether to use fzf as the interface for the anilist command and others.

use_rofi=false # whether to use rofi for the ui
rofi_theme=<path-to-rofi-theme-file>
rofi_theme_input=<path-to-rofi-theme-file>
rofi_theme_confirm=<path-to-rofi-theme-file>


# whether to show the icons
icons=false

# the duration in minutes a notification will stay in the screen
# used by notifier command
notification_duration=2

[anilist]
# Not implemented yet
```

## Contributing

We welcome your issues and feature requests. However, due to time constraints, we currently do not plan to add another provider.

If you wish to contribute directly, please first open an issue describing your proposed changes so it can be discussed.

## Receiving Support

For inquiries, join our [Discord Server](https://discord.gg/4NUTj5Pt).

<p align="center">
<a href="https://discord.gg/HRjySFjQ">
<img src="https://invidget.switchblade.xyz/HRjySFjQ"/>
</a>
</p>

## Supporting the Project

Show your support by starring our GitHub repository or [buying us a coffee](https://ko-fi.com/benex254).
