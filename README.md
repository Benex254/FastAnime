# Fast Anime

Welcome to Fast Anime, your new favorite destination for streaming and downloading anime.

## Table of Contents

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using pipx](#using-pipx)
  - [Pre-built binaries](#pre-built-binaries)
  - [Building from the source](#building-from-the-source)
- [Major Dependencies](#major-dependencies)
- [Contributing](#contributing)
- [Receiving Support](#receiving-support)
- [Supporting the Project](#supporting-the-project)
- [demo video](#demo-video)

## Installation

### Using pip

Working on it...

### Using pipx

working on it...

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
# normal Installation
poetry build
cd dist
pip install fastanime<version>.whl

# editable installation
# which is currently the easiest way to update since all you have to do is git pull
pip install -e .

# FastAnime should now be installed and available as fastanime
# test if everything was success by running
fastanime --version

```

5. Enjoy

> [**Tip**]!
> To add completions:
> Fish Users: `cp $FASTANIME_PATH/completions/fastanime.fish ~/.config/fish/completions/`
> Bash Users: `source $FASTANIME_PATH/completions/fastanime.bash` in your `.bashrc file`
> Zsh Users: `source $FASTANIME_PATH/completions/fastanime.zsh` in your `.zshrc file`

## Usage

The app is meant to be flexible with its usage offering both a graphical interface and commandline interface.

> **_NOTE:_**
> The GUI is currently in dev mode and is actively being worked on so enjoy the cli for now

### The Commandline interface :fire:

Made for power users who love the terminal and hate the annoying ads and inefficiency of interacting with browsers.

Overview of main commands:

- `fastanime anilist # :fire: most powerful and useful command for streaming`
- `fastanime download # download anime`
- `fastanime search # basic streaming functionality`
- `fastanime downloads # view your downloads`
- `fastanime config # edit your config`

The following options are available to edit your config during run time:

- `--continue # default` / `--no-continue` to set to continue from your watch history
- `downloads-dir <dir_path>` to set the downloads diretory
- `--quality <int: 0-4>` to set the quality of the streams
- `--auto-next # flag` to automatically go to the next episode
- `--server <server>` your preferred server

#### The anilist command

The most useful command if you prefer to stream anime and prefer doing everything from the terminal. Cause its just way more effecient. If you haven't tried, try it, your productivity would skyrocket.
The command uses the **Anilist api** to provide a rich experience similar if not better than your traditional ad filled site.

##### Running without any subcommand

If you run the command `fastanime anilist` by itself you will reach the main interface.

##### Sub commands

The following subcommands are available for convinience and quick navigation:

- `fastanime anilist trending` to get the top 15 trending anime.
- `fastanime anilist recent` to get the top 15 recently updated anime.
- `fastanime anilist search` to search for anime and get the top 50 results.
- `fastanime anilist upcoming` to get the top 15 most scored anime.
- `fastanime anilist popular` to get the top 15 most popular anime.
- `fastanime anilist favourites` to get the top 15 most favourite anime.

#### download subcommand

Useful for downloading anime.
**syntax:**

```bash
# basic command, will download all available episodes
fastanime download <anime-title>

# specifying episode range to download
fastanime download <anime-title> -r <episodes-start>-<episodes-end>
```

#### search subcommand

Directly interacts with the provider offering a more minimal ui and ux.

**syntax:**

```bash
fastanime search <anime-title>
```

#### downloads subcommand

Convinience command to view your downloads and stream them with mpv.
**syntax:**

```bash
fastanime downloads
```

#### config subcommand

Convinience command to edit your fastanime config with your preferred editor. Looks for `$EDITOR` environment variable
**syntax:**

```bash
fastanime config
```

## Configuration

The app comes with sensible defaults but if you wish to extend it to fit more to your use case it is super easy.
The config is in the `.ini` format and located `~/.config/FastAnime/config.ini`

```ini
[stream]
continue_from_history = True # whether to auto continue from where you left of based on your watch history
translation_type = sub # preffered language for anime. options: [dub,sub]
server=top # the default server [dropbox,sharepoint,wetransfer.gogoanime]. "top" auto selects the best
auto_next = False # whether to automatically select the next episode. Useful for binging

[general]
preferred_language = romaji # the language used for the display name. acceptable [english,romaji]
downloads_dir=<Default-videos-dir>/FastAnime # set where downlad videos are to be stored

[anilist]
# not implemented
```

## Contributing

We welcome your issues and feature requests. However, we currently have no plans to add another provider, so issues related to this may not be addressed due to time constraints. If you wish to contribute directly, please open an issue detailing the changes you wish to add and request a PR.

## Receiving Support

If you have any inquiries, join our [Discord Server](https://discord.gg/4NUTj5Pt).

[![Join our Discord server!](https://invidget.switchblade.xyz/4NUTj5Pt)](http://discord.gg/4NUTj5Pt)

## Supporting the Project

If you want to support the project, please consider leaving a star on our GitHub repository or [buying us a coffee](https://ko-fi.com/benex254). We appreciate both!

## demo-video
