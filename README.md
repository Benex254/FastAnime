# Fast Anime

Welcome to **FastAnime**, an anime scrapper that brings a browser experience to the terminal.

[intro.webm](https://github.com/user-attachments/assets/036af7fc-83ff-4f9b-bda6-0c913f7d0f38)

Heavily inspired by [animdl](https://github.com/justfoolingaround/animdl), [magic-tape](https://gitlab.com/christosangel/magic-tape/-/tree/main?ref_type=heads) and [ani-cli](https://github.com/pystardust/ani-cli).

> [!IMPORTANT]
>
> This project currently scrapes allanime and is in no way related to them. The site is in the public domain and can be access by any one with a browser.

> [!NOTE]
>
> Also the docs are still being worked on and are far from completion.

## Table of Contents

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [Pre-built binaries](#pre-built-binaries)
  - [Building from the source](#building-from-the-source)
  - [External Dependencies](#external-dependencies)
- [Usage](#usage)
  - [The Commandline interface](#the-commandline-interface-fire)
    - [The anilist command](#the-anilist-command)
    - [download subcommand](#download-subcommand)
    - [search subcommand](#search-subcommand)
    - [downloads subcommand](#downloads-subcommand)
    - [config subcommand](#config-subcommand)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Receiving Support](#receiving-support)
- [Supporting the Project](#supporting-the-project)

## Installation

### Using pip

```bash
pip install https://github.com/Benex254/FastAnime/releases/download/v0.30.0/fastanime-0.3.0.tar.gz
```

### Using pipx

```bash

pipx install https://github.com/Benex254/FastAnime/releases/download/v0.30.0/fastanime-0.3.0.tar.gz
```

### Pre-built binaries

We will soon release pre-built binaries for Linux and Windows.

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

**Other dependecies that will just make your experience better:**

- [fzf](https://github.com/junegunn/fzf) :fire: which is used as a better alternative to the ui.
- [fzf-preview](https://github.com/junegunn/fzf/blob/master/bin/fzf-preview.sh) a script that is used to preview images and is maintained by the devs of fzf.
- [chafa](https://github.com/hpjansson/chafa) currently the best cross platform and cross terminal image viewer for the terminal.
- [icat](https://sw.kovidgoyal.net/kitty/kittens/icat/) an image viewer that only works in [kitty terminal](https://sw.kovidgoyal.net/kitty/), which is currently the best terminal in my opinion, and by far the best image renderer for the terminal thanks to kitty's terminal graphics protocol. Its terminal graphics is so op that you can [run a browser on it]()!!
- [bash](https://www.gnu.org/software/bash/) is used as the preview script language.

## Usage

The app offers both a graphical interface (under development) and a robust command-line interface.

> [!NOTE]
>
> The GUI is in development; use the CLI for now.
> However, you can try it out before i decided to change my objective by checking out this [release](https://github.com/Benex254/FastAnime/tree/v0.20.0).
> But be reassured for those who aren't terminal chads, i will still complete the GUI for the fun of it

### The Commandline interface :fire:

Designed for power users who prefer efficiency over browser-based streaming and still want the experience in their terminal.

Overview of main commands:

- `fastanime anilist`: Powerful command for browsing and exploring anime due to Anilist intergration.
- `fastanime download`: Download anime.
- `fastanime search`: Powerful command meant for binging since it doesn't require the interfaces
- `fastanime downloads`: View downloaded anime and watch with mpv.
- `fastanime config`: Quickly edit configuration settings.

Configuration is directly passed into this command at run time to overide your config.

#### The anilist command

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
```

#### config subcommand

Edit FastAnime configuration settings using your preferred editor (based on `$EDITOR` environment variable so be sure to set it).

**Syntax:**

```bash
fastanime config
```

> [!Note]
>
> If it opens [vim](https://www.vim.org/download.php) you can exit by typing `:q` in case you don't know.

## Configuration

The app includes sensible defaults but can be customized extensively. Configuration is stored in `.ini` format at `~/.config/FastAnime/config.ini` on linux and mac or somewhere on windows.

```ini
[stream]
continue_from_history = True  # Auto continue from watch history
translation_type = sub  # Preferred language for anime (options: dub, sub)
server = top  # Default server (options: dropbox, sharepoint, wetransfer.gogoanime, top)
auto_next = False  # Auto-select next episode
# Auto select the anime provider results with fuzzyfind.
# Note this wont always be correct.But 99% of the time will be.
auto_select=True

[general]
preferred_language = romaji  # Display language (options: english, romaji)
downloads_dir = <Default-videos-dir>/FastAnime  # Download directory
use_fzf=False # whether to use fzf as the interface for the anilist command and others.

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
<img src="https://invidget.switchblade.xyz/HRjySFjQ">
</a>
</p>

## Supporting the Project

Show your support by starring our GitHub repository or [buying us a coffee](https://ko-fi.com/benex254).
