# Fast Anime

Welcome to Fast Anime, your new favorite destination for streaming and downloading anime.
![](https://github.com/Benex254/FastAnime/raw/master/.assets/screencasts/intro.webm)
Heavily inspired by animdl, magic-tape and ani-cli.

## Table of Contents

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [Pre-built binaries](#pre-built-binaries)
  - [Building from the source](#building-from-the-source)
- [Usage](#usage)
  - [The Commandline interface](#the-commandline-interface-fire)
    - [The anilist command](#the-anilist-command)
    - [download subcommand](#download-subcommand)
    - [search subcommand](#search-subcommand)
    - [downloads subcommand](#downloads-subcommand)
    - [config subcommand](#config-subcommand)
- [Configuration](#configuration)
- [Major Dependencies](#major-dependencies)
- [Contributing](#contributing)
- [Receiving Support](#receiving-support)
- [Supporting the Project](#supporting-the-project)
- [Demo Video](#demo-video)

## Installation

### Using pip

Work in progress...

### Using pipx

Work in progress...

### Pre-built binaries

We will soon release pre-built binaries for Linux and Windows.

### Building from the source

Requirements:

- git
- python 3.10 and above
- poetry

To build from the source, follow these steps:

1. Clone the repository: `git clone https://github.com/Benex254/FastAnime.git`
2. Navigate into the folder: `cd FastAnime`
3. Install the Dependencies with **poetry**: `poetry install`
4. Install the app

```bash
# Normal Installation
poetry build
cd dist
pip install fastanime<version>.whl

# Editable installation (easiest for updates)
pip install -e .
```

5. Enjoy! Verify installation with:

```bash
fastanime --version
```

> **Tip**: To add completions:
>
> - Fish Users: `cp $FASTANIME_PATH/completions/fastanime.fish ~/.config/fish/completions/`
> - Bash Users: Add `source $FASTANIME_PATH/completions/fastanime.bash` to your `.bashrc`
> - Zsh Users: Add `source $FASTANIME_PATH/completions/fastanime.zsh` to your `.zshrc`

## Usage

The app offers both a graphical interface (under development) and a robust command-line interface.

> **_NOTE:_** The GUI is in development; use the CLI for now.

### The Commandline interface :fire:

Designed for power users who prefer efficiency over browser-based streaming.

Overview of main commands:

- `fastanime anilist`: Powerful command for streaming from Anilist.
- `fastanime download`: Download anime episodes.
- `fastanime search`: Basic streaming functionality.
- `fastanime downloads`: View downloaded episodes.
- `fastanime config`: Edit configuration settings.

#### The anilist command

Stream anime efficiently from the terminal using Anilist API.

##### Running without any subcommand

Run `fastanime anilist` to access the main interface.

##### Subcommands

- `fastanime anilist trending`: Top 15 trending anime.
- `fastanime anilist recent`: Top 15 recently updated anime.
- `fastanime anilist search`: Search for anime (top 50 results).
- `fastanime anilist upcoming`: Top 15 upcoming anime.
- `fastanime anilist popular`: Top 15 popular anime.
- `fastanime anilist favourites`: Top 15 favorite anime.

#### download subcommand

Download anime episodes.

**Syntax:**

```bash
# Download all available episodes
fastanime download <anime-title>

# Download specific episode range
fastanime download <anime-title> -r <episodes-start>-<episodes-end>
```

#### search subcommand

Minimal UI for searching anime.

**Syntax:**

```bash
fastanime search <anime-title>
```

#### downloads subcommand

View and stream downloaded episodes using MPV.

**Syntax:**

```bash
fastanime downloads
```

#### config subcommand

Edit FastAnime configuration settings using your preferred editor (based on `$EDITOR` environment variable).

**Syntax:**

```bash
fastanime config
```

## Configuration

The app includes sensible defaults but can be customized extensively. Configuration is stored in `.ini` format at `~/.config/FastAnime/config.ini`.

```ini
[stream]
continue_from_history = True  # Auto continue from watch history
translation_type = sub  # Preferred language for anime (options: dub, sub)
server = top  # Default server (options: dropbox, sharepoint, wetransfer.gogoanime, top)
auto_next = False  # Auto-select next episode

[general]
preferred_language = romaji  # Display language (options: english, romaji)
downloads_dir = <Default-videos-dir>/FastAnime  # Download directory

[anilist]
# Not implemented yet
```

## Contributing

We welcome your issues and feature requests. However, due to time constraints, we currently do not plan to add another provider.

If you wish to contribute directly, please open an issue describing your proposed changes and request a pull request.

## Receiving Support

For inquiries, join our [Discord Server](https://discord.gg/4NUTj5Pt).

[![Join our Discord server!](https://invidget.switchblade.xyz/4NUTj5Pt)](http://discord.gg/4NUTj5Pt)

## Supporting the Project

Show your support by starring our GitHub repository or [buying us a coffee](https://ko-fi.com/benex254). We appreciate both!

## Demo Video

Check out our demo video for a quick overview and installation guide.
